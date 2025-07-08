from typing import Any, Dict, List, Optional, Set, Tuple, Union
from langchain.prompts import (
    ChatMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import boto3
from botocore.exceptions import ClientError
import boto3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import threading
from unbiasedupdates.prompts import SUMMARY_GEN_SYS_TEMP
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os

def _extract_text_between_last_tag_pair(xml_text, tag):
    """
    Extracts the content between the last pair of opening and closing tags.

    Args:
        xml_text (str): The full input string (e.g., XML or custom-tagged text).
        tag (str): The tag name (without angle brackets), e.g., 'final_answer'.

    Returns:
        str: The content between the last occurrence of the opening and closing tags.

    Raises:
        ValueError: If the opening or closing tag is not found.
    """
    open_tag = f"<{tag}>"
    close_tag = f"</{tag}>"

    end_idx = xml_text.rfind(close_tag)
    if end_idx == -1:
        raise ValueError(f"Closing tag '{close_tag}' not found.")

    start_idx = xml_text.rfind(open_tag, 0, end_idx)
    if start_idx == -1:
        raise ValueError(f"Opening tag '{open_tag}' not found.")

    start_idx += len(open_tag)
    return xml_text[start_idx:end_idx].strip()

def lg_runnable(
    llm: Any,
    system_message: str,
    schema: Optional[
        Any
    ] = None,  # Optionally specify the type of schema if needed, otherwise 'Any' is used
    strict: bool = False,
    use_schema: bool = False,
    human_message: Union[str, bool] = False,
    json_schema: bool = False,  ## This doesnt work as intended at the moment, idealy when this is true the model should doutput the json out but instead it outputs pydantic class type output.
):
    """
    Constructs a runnable configuration for a large language model (LLM) based on provided messages and settings.

    This function assembles a sequence of message templates into a prompt and optionally configures the LLM
    for structured output based on a schema and a specified output mode.

    Parameters:
    - llm (Any): The large language model to be configured.
    - system_message (str): A template string for the system message to be used in the chat.
    - schema (Optional[Any]): The schema used to format the LLM's output. None means no schema is used.
    - use_schema (bool): Flag to determine whether to apply the schema to the LLM's output.
    - human_message (Union[str, bool]): A template string for the human message or a boolean flag.
      If True, raises an error as it's not a valid input.
    - json_schema (bool): Flag to determine whether the output should be structured as JSON when using a schema.

    Returns:
    - runnable: A configured pipeline combining prompt templates and LLM output settings.

    Raises:
    - ValueError: If `human_message` is True, indicating an invalid input type.
    """
    messages = []  # Initialize list to hold message templates

    # Create a system message template from the provided string message
    system_template = SystemMessagePromptTemplate.from_template(system_message)
    messages.append(system_template)  # Add system message template to messages list

    # Handle human message based on its type (string or boolean)
    if isinstance(human_message, str):
        # If it's a string, create a human message template
        human_template = HumanMessagePromptTemplate.from_template(human_message)
        messages.append(human_template)
    elif human_message is True:
        # Raise an error if human_message is True as it's not a valid string template
        raise ValueError("human_message must be a string template or False, not True")

    # Create the final chat prompt template from accumulated messages
    prompt = ChatPromptTemplate.from_messages(messages)

    # Depending on the flags, prepare the large language model (LLM) with structured output or a simple output parser

    if strict and not json_schema:
        raise ValueError("Strict can only be set to True with json_schema enabled.")

    if use_schema and schema is None:
        raise ValueError("When use_schema is enabled, a schema needs to be provided.")

    if use_schema:
        if json_schema:
            # Configure LLM for structured output in JSON mode if specified
            structured_llm = llm.with_structured_output(
                schema, method="json_schema", strict=strict
            )
            runnable = prompt | structured_llm

        else:
            # Configure LLM for structured output without JSON mode
            structured_llm = llm.with_structured_output(schema)
            runnable = prompt | structured_llm

    else:
        # Default to a simple string output parser if no schema is used
        output_parser = StrOutputParser()
        runnable = prompt | llm | output_parser

    return runnable


def gemini_runnable(llm, template:str):
    prompt = ChatPromptTemplate.from_messages([template])
    output_parser = StrOutputParser()
    runnable = prompt | llm | output_parser
    return runnable


def parse_rss_feed_bbc(xml_content, days_back=1):
    """
    Parse BBC RSS XML and return a list of dicts for articles published within `days_back` days.
    Each dict includes title, link, pubDate, and thumbnail URL.
    """
    ns = {
        'media': 'http://search.yahoo.com/mrss/',
    }

    root = ET.fromstring(xml_content)
    items = []

    # Calculate date threshold
    today = datetime.utcnow()
    date_limit = today - timedelta(days=days_back)

    for item in root.findall('.//item'):
        title_el = item.find('title')
        link_el = item.find('link')
        pubDate_el = item.find('pubDate')
        thumb_el = item.find('media:thumbnail', ns)

        if title_el is None or link_el is None or pubDate_el is None:
            continue
        
        link_text = link_el.text.strip()
        if "/news/articles/" not in link_text:
            continue


        try:
            pub_date = datetime.strptime(pubDate_el.text.strip(), '%a, %d %b %Y %H:%M:%S %Z')
        except ValueError:
            continue

        if pub_date >= date_limit:
            article = {
                'title': title_el.text.strip(),
                'link': link_el.text.strip(),
                'pubDate': pub_date.strftime('%Y-%m-%d %H:%M:%S'),
                'thumbnail': thumb_el.attrib['url'] if thumb_el is not None else None
            }
            items.append(article)

    return items

def get_article_content_and_images_bbc(url, headers):
    """
    Fetches the title, content, main image, and date of a single article
    
    Args:
        url (str): Article URL
        headers (dict): Request headers
        
    Returns:
        tuple: (title, content_string, main_image_url, publication_date)
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # EXTRACT TITLE
        title = ""
        title_selectors = [
            'h1[id="main-heading"]',
            'h1.ssrcss-1s9pby4-Heading',
            'h1 span[role="text"]',
            'h1',
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                title = title_element.get_text(strip=True)
                break
        
        if not title:
            title = "Title not found"

        # EXTRACT DATE
        publication_date = ""
        date_selectors = [
            'time[data-testid="timestamp"]',  # BBC timestamp element
            'time[datetime]',  # Generic time with datetime attribute
            '[data-component="metadata-block"] time',  # Time in metadata block
            '.ssrcss-1pvwv4b-MetadataSnippet time',  # BBC metadata time
        ]
        
        for selector in date_selectors:
            date_element = soup.select_one(selector)
            if date_element:
                # Try to get the datetime attribute first, then text content
                publication_date = (date_element.get('datetime') or 
                                  date_element.get_text(strip=True))
                break
        
        if not publication_date:
            publication_date = "Date not found"

        # EXTRACT CONTENT (existing code)
        content_selectors = [
            '[data-component="text-block"] p',
            '.story-body__inner p',
            '[data-component="text-block"]',
            'article p',
            '.gel-body-copy p',
            '.ssrcss-1q0x1qg-Paragraph p'
        ]

        content_paragraphs = []
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 20:
                        content_paragraphs.append(text)
                break

        # EXTRACT MAIN IMAGE (existing code)
        main_image_url = ""
        image_selectors = [
            'article img.ssrcss-11yxrdo-Image',
            '[data-component="image-block"] img',
            'figure img',
            'img[src*="ichef.bbci.co.uk"]'
        ]

        for selector in image_selectors:
            img = soup.select_one(selector)
            if img:
                img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if img_url:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://www.bbc.co.uk' + img_url
                    
                    if 'ichef.bbci.co.uk' in img_url:
                        main_image_url = img_url
                        break

        content = '\n\n'.join(content_paragraphs) if content_paragraphs else "Content could not be extracted"

        return title, content, main_image_url, publication_date

    except Exception as e:
        return "Error extracting title", f"Error fetching content: {str(e)}", "", "Date not found"


# Thread-local storage for AWS resources
thread_local = threading.local()

def get_aws_resources():
    """Return DynamoDB table using local profile only if not running inside AWS Lambda"""
    
    if not hasattr(thread_local, 'table'):
        # Auto-detect if running in Lambda environment
        running_in_lambda = 'AWS_LAMBDA_FUNCTION_NAME' in os.environ

        if running_in_lambda:
            # Use IAM role in Lambda
            session = boto3.Session(region_name='us-east-1')
        else:
            # Local development (assumes profile is configured)
            session = boto3.Session(profile_name='root-access', region_name='us-east-1')

        dynamodb_resource = session.resource('dynamodb')
        thread_local.table = dynamodb_resource.Table('news_articles')

    return thread_local.table






def process_single_article_bbc(article: Dict[str, Any], model: str, headers: Dict[str, str], 
                          runnable, grunnable) -> Dict[str, Any]:
    """
    Process a single article - extract content, generate summary, and save to DynamoDB
    
    Args:
        article: Dictionary containing article data with 'link' key
        model: Model to use ('openai' or 'gemini')
        headers: Headers for web requests
        runnable: OpenAI runnable instance
        grunnable: Gemini runnable instance
    
    Returns:
        Dictionary with processing result
    """
    url = article['link']
    table = get_aws_resources()
    
    try:
        # 1. Extract article content
        title, content, _, _ = get_article_content_and_images_bbc(url, headers)
        article['content'] = content
        article['source'] = 'BBC'

        # 2. Check if the title already exists in the table
        response = table.get_item(Key={'title': title})
        if 'Item' in response:
            return {
                'status': 'skipped',
                'title': title,
                'url': url,
                'message': 'Article already exists'
            }

        # 3. Generate summary using the selected model
        if model == 'openai':
            llm_output = runnable.invoke({'content': content})
        elif model == 'gemini':
            llm_output = grunnable.invoke({'content': content})
        else:
            return {
                'status': 'error',
                'title': title,
                'url': url,
                'message': f'Unsupported model: {model}'
            }

        # 4. Extract structured fields from the LLM response
        try:
            insights = _extract_text_between_last_tag_pair(xml_text=llm_output, tag='insights')
            summary = _extract_text_between_last_tag_pair(xml_text=llm_output, tag='thumbnail_snippet')
            gen_title = _extract_text_between_last_tag_pair(xml_text=llm_output, tag='title')
        except Exception as parsing_error:
            return {
                'status': 'parsing_error',
                'title': title,
                'url': url,
                'message': f'Error extracting fields from LLM response: {str(parsing_error)}',
                'llm_output': llm_output[:500] + "..." if len(llm_output) > 500 else llm_output  # First 500 chars for debugging
            }
        
        # 4a. Validate that all required fields were extracted
        if not all([insights, summary, gen_title]):
            missing_fields = []
            if not insights: missing_fields.append('insights')
            if not summary: missing_fields.append('thumbnail_snippet')
            if not gen_title: missing_fields.append('title')
            
            return {
                'status': 'parsing_error',
                'title': title,
                'url': url,
                'message': f'Missing or empty fields: {", ".join(missing_fields)}',
                'llm_output': llm_output[:500] + "..." if len(llm_output) > 500 else llm_output,
                'extracted_data': {
                    'insights': insights if insights else '',
                    'summary': summary if summary else '',
                    'gen_title': gen_title if gen_title else ''
                }
            }

        # 5. Prepare item for insertion (with fallback values)
        item = {
            'title': title,
            'url': article.get('link'),
            'publisheddate': article.get('pubDate'),
            'thumbnail': article.get('thumbnail'),
            'content': content,
            'source': 'BBC',
            'generated_title': gen_title or title,  # Fallback to original title
            'summary': summary or content[:500] + "...",  # Fallback to truncated content
            'insights': insights or "No insights available"  # Fallback message
        }

        # 6. Insert into DynamoDB
        table.put_item(Item=item)
        
        return {
            'status': 'success',
            'title': title,
            'url': url,
            'message': 'Article processed successfully'
        }

    except Exception as e:
        return {
            'status': 'error',
            'title': article.get('title', 'Unknown'),
            'url': url,
            'message': str(e)
        }

def process_articles_parallel_bbc(articles: List[Dict[str, Any]], 
                            batch_size: int, 
                            model: str, 
                            headers: Dict[str, str],
                            runnable=None, 
                            grunnable=None,
                            max_workers: int = 5,
                            delay_between_batches: float = 2.0) -> List[Dict[str, Any]]:
    """
    Process articles in parallel batches
    
    Args:
        articles: List of article dictionaries
        batch_size: Number of articles to process in each batch
        model: Model to use ('openai' or 'gemini')
        headers: Headers for web requests
        runnable: OpenAI runnable instance (required if model='openai')
        grunnable: Gemini runnable instance (required if model='gemini')
        max_workers: Maximum number of threads per batch
        delay_between_batches: Delay in seconds between batches
    
    Returns:
        List of processing results for all articles
    """
    
    if model == 'openai' and runnable is None:
        raise ValueError("runnable is required when model='openai'")
    if model == 'gemini' and grunnable is None:
        raise ValueError("grunnable is required when model='gemini'")
    
    # Split articles into batches
    batches = [articles[i:i + batch_size] for i in range(0, len(articles), batch_size)]
    all_results = []
    
    print(f"Processing {len(articles)} articles in {len(batches)} batches of {batch_size}")
    
    for batch_idx, batch in enumerate(batches, 1):
        print(f"\nProcessing batch {batch_idx}/{len(batches)} ({len(batch)} articles)...")
        
        batch_results = []
        
        # Process batch in parallel
        with ThreadPoolExecutor(max_workers=min(max_workers, len(batch))) as executor:
            # Submit all tasks in the batch
            future_to_article = {
                executor.submit(
                    process_single_article_bbc, 
                    article, 
                    model, 
                    headers, 
                    runnable, 
                    grunnable
                ): article for article in batch
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_article):
                article = future_to_article[future]
                try:
                    result = future.result()
                    batch_results.append(result)
                    
                    # Print progress
                    if result['status'] == 'success':
                        print(f"✓ {result['title']}")
                    elif result['status'] == 'skipped':
                        print(f"→ Skipped: {result['title']}")
                    elif result['status'] == 'parsing_error':
                        print(f"⚠ Parsing error: {result['title']} - {result['message']}")
                    else:
                        print(f"✗ Error: {result['title']} - {result['message']}")
                        
                except Exception as e:
                    error_result = {
                        'status': 'error',
                        'title': article.get('title', 'Unknown'),
                        'url': article.get('link', 'Unknown'),
                        'message': f'Future execution error: {str(e)}'
                    }
                    batch_results.append(error_result)
                    print(f"✗ Future error: {article.get('link', 'Unknown')} - {str(e)}")
        
        all_results.extend(batch_results)
        
        # Print batch summary
        success_count = sum(1 for r in batch_results if r['status'] == 'success')
        skipped_count = sum(1 for r in batch_results if r['status'] == 'skipped')
        error_count = sum(1 for r in batch_results if r['status'] == 'error')
        
        print(f"Batch {batch_idx} complete: {success_count} success, {skipped_count} skipped, {error_count} errors")
        
        # Delay between batches (except for the last batch)
        if batch_idx < len(batches):
            print(f"Waiting {delay_between_batches}s before next batch...")
            time.sleep(delay_between_batches)
    
    return all_results

def print_final_summary(results: List[Dict[str, Any]]):
    """Print a summary of all processing results"""
    success_count = sum(1 for r in results if r['status'] == 'success')
    skipped_count = sum(1 for r in results if r['status'] == 'skipped')
    error_count = sum(1 for r in results if r['status'] == 'error')
    parsing_error_count = sum(1 for r in results if r['status'] == 'parsing_error')
    
    print(f"\n{'='*50}")
    print(f"FINAL SUMMARY")
    print(f"{'='*50}")
    print(f"Total articles: {len(results)}")
    print(f"Successfully processed: {success_count}")
    print(f"Skipped (already exist): {skipped_count}")
    print(f"General errors: {error_count}")
    print(f"Parsing errors: {parsing_error_count}")
    
    if error_count > 0:
        print(f"\nGeneral errors:")
        for result in results:
            if result['status'] == 'error':
                print(f"  - {result['url']}: {result['message']}")
                
    if parsing_error_count > 0:
        print(f"\nParsing errors:")
        for result in results:
            if result['status'] == 'parsing_error':
                print(f"  - {result['url']}: {result['message']}")
                if 'extracted_data' in result:
                    print(f"    Extracted data: {result['extracted_data']}")


import xml.etree.ElementTree as ET
from datetime import datetime, timedelta,timezone
import requests


def parse_aljazeera_news_sitemap(xml_content, days_back=20):
    """
    Parse Al Jazeera's sitemap and return news articles published within `days_back` days.
    """
    ns = {
        'news': 'http://www.google.com/schemas/sitemap-news/0.9'
    }

    root = ET.fromstring(xml_content)
    articles = []
    
    today = datetime.now(timezone.utc)
    date_limit = today - timedelta(days=days_back)

    for url_el in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc_el = url_el.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        pub_el = url_el.find('news:news/news:publication_date', ns)
        title_el = url_el.find('news:news/news:title', ns)

        if loc_el is None or pub_el is None or title_el is None:
            continue

        url = loc_el.text.strip()
        if "/news/" not in url or "/liveblog/" in url:
            continue

        try:
            pub_date = datetime.fromisoformat(pub_el.text.strip().replace("Z", "+00:00"))
        except ValueError:
            continue

        if pub_date >= date_limit:
            articles.append({
                'title': title_el.text.strip(),
                'link': url,
                'pubDate': pub_date.strftime('%Y-%m-%d %H:%M:%S'),
            })

    return articles


import requests
from bs4 import BeautifulSoup
import time

def get_article_content_and_images_aj(url, headers):
    """
    Fetches the title, content, main image, and date of a single Al Jazeera article
    
    Args:
        url (str): Article URL
        headers (dict): Request headers
        
    Returns:
        tuple: (title, content_string, main_image_url, publication_date)
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # EXTRACT TITLE
        title = ""
        title_selectors = [
            'header.article-header h1',  # Al Jazeera main title
            'h1',  # Fallback
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                title = title_element.get_text(strip=True)
                break
        
        if not title:
            title = "Title not found"

        # EXTRACT DATE
        publication_date = ""
        date_selectors = [
            '.article-dates .date-simple span[aria-hidden="true"]',  # Al Jazeera date format
            '.date-simple span[aria-hidden="true"]',  # Alternative date selector
            'time[datetime]',  # Generic time with datetime attribute
            '.article-dates',  # Broader date container
        ]
        
        for selector in date_selectors:
            date_element = soup.select_one(selector)
            if date_element:
                # Try to get the datetime attribute first, then text content
                publication_date = (date_element.get('datetime') or 
                                  date_element.get_text(strip=True))
                break
        
        if not publication_date:
            publication_date = "Date not found"

        # EXTRACT CONTENT
        content_selectors = [
            '.wysiwyg.wysiwyg--all-content p',  # Al Jazeera main content paragraphs
            '.wysiwyg p',  # Alternative content selector
            'article p',  # Generic article paragraphs
            '.article-content p',  # Another possible content selector
        ]

        content_paragraphs = []
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    # Skip elements that are likely ads or navigation
                    if (element.find_parent(['aside', 'nav', '.more-on', '.article-related-list']) or
                        'newsletter' in element.get('class', []) or
                        'advertisement' in element.get_text().lower()):
                        continue
                    
                    text = element.get_text(strip=True)
                    if text and len(text) > 20:  # Filter out very short text
                        content_paragraphs.append(text)
                break

        # EXTRACT MAIN IMAGE
        main_image_url = ""
        image_selectors = [
            'figure.article-featured-image img',  # Al Jazeera featured image
            '.article-featured-image img',  # Alternative featured image
            'figure img',  # Generic figure image
            '.responsive-image img',  # Responsive image container
        ]

        for selector in image_selectors:
            img = soup.select_one(selector)
            if img:
                img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if img_url:
                    # Handle relative URLs
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://www.aljazeera.com' + img_url
                    
                    # Prefer high-quality images (look for wp-content which Al Jazeera uses)
                    if 'wp-content' in img_url or img_url.startswith('https://'):
                        main_image_url = img_url
                        break

        content = '\n\n'.join(content_paragraphs) if content_paragraphs else "Content could not be extracted"

        return title, content, main_image_url, publication_date

    except Exception as e:
        return "Error extracting title", f"Error fetching content: {str(e)}", "", "Date not found"
    


def process_single_article_aj(article: Dict[str, Any], model: str, headers: Dict[str, str], 
                          runnable, grunnable) -> Dict[str, Any]:
    """
    Process a single article - extract content, generate summary, and save to DynamoDB
    
    Args:
        article: Dictionary containing article data with 'link' key
        model: Model to use ('openai' or 'gemini')
        headers: Headers for web requests
        runnable: OpenAI runnable instance
        grunnable: Gemini runnable instance
    
    Returns:
        Dictionary with processing result
    """
    url = article['link']
    table = get_aws_resources()
    
    try:
        # 1. Extract article content
        title, content, main_image_url, _ = get_article_content_and_images_aj(url, headers)
        article['content'] = content
        article['source'] = 'BBC'

        # 2. Check if the title already exists in the table
        response = table.get_item(Key={'title': title})
        if 'Item' in response:
            return {
                'status': 'skipped',
                'title': title,
                'url': url,
                'message': 'Article already exists'
            }

        # 3. Generate summary using the selected model
        if model == 'openai':
            llm_output = runnable.invoke({'content': content})
        elif model == 'gemini':
            llm_output = grunnable.invoke({'content': content})
        else:
            return {
                'status': 'error',
                'title': title,
                'url': url,
                'message': f'Unsupported model: {model}'
            }

        # 4. Extract structured fields from the LLM response
        try:
            insights = _extract_text_between_last_tag_pair(xml_text=llm_output, tag='insights')
            summary = _extract_text_between_last_tag_pair(xml_text=llm_output, tag='thumbnail_snippet')
            gen_title = _extract_text_between_last_tag_pair(xml_text=llm_output, tag='title')
        except Exception as parsing_error:
            return {
                'status': 'parsing_error',
                'title': title,
                'url': url,
                'message': f'Error extracting fields from LLM response: {str(parsing_error)}',
                'llm_output': llm_output[:500] + "..." if len(llm_output) > 500 else llm_output  # First 500 chars for debugging
            }
        
        # 4a. Validate that all required fields were extracted
        if not all([insights, summary, gen_title]):
            missing_fields = []
            if not insights: missing_fields.append('insights')
            if not summary: missing_fields.append('thumbnail_snippet')
            if not gen_title: missing_fields.append('title')
            
            return {
                'status': 'parsing_error',
                'title': title,
                'url': url,
                'message': f'Missing or empty fields: {", ".join(missing_fields)}',
                'llm_output': llm_output[:500] + "..." if len(llm_output) > 500 else llm_output,
                'extracted_data': {
                    'insights': insights if insights else '',
                    'summary': summary if summary else '',
                    'gen_title': gen_title if gen_title else ''
                }
            }

        # 5. Prepare item for insertion (with fallback values)
        item = {
            'title': title,
            'url': article.get('link'),
            'publisheddate': article.get('pubDate'),
            'thumbnail': main_image_url,
            'content': content,
            'source': 'AJ',
            'generated_title': gen_title or title,  # Fallback to original title
            'summary': summary or content[:500] + "...",  # Fallback to truncated content
            'insights': insights or "No insights available"  # Fallback message
        }

        # 6. Insert into DynamoDB
        table.put_item(Item=item)
        
        return {
            'status': 'success',
            'title': title,
            'url': url,
            'message': 'Article processed successfully'
        }

    except Exception as e:
        return {
            'status': 'error',
            'title': article.get('title', 'Unknown'),
            'url': url,
            'message': str(e)
        }

def process_articles_parallel_aj(articles: List[Dict[str, Any]], 
                            batch_size: int, 
                            model: str, 
                            headers: Dict[str, str],
                            runnable=None, 
                            grunnable=None,
                            max_workers: int = 5,
                            delay_between_batches: float = 2.0) -> List[Dict[str, Any]]:
    """
    Process articles in parallel batches
    
    Args:
        articles: List of article dictionaries
        batch_size: Number of articles to process in each batch
        model: Model to use ('openai' or 'gemini')
        headers: Headers for web requests
        runnable: OpenAI runnable instance (required if model='openai')
        grunnable: Gemini runnable instance (required if model='gemini')
        max_workers: Maximum number of threads per batch
        delay_between_batches: Delay in seconds between batches
    
    Returns:
        List of processing results for all articles
    """
    
    if model == 'openai' and runnable is None:
        raise ValueError("runnable is required when model='openai'")
    if model == 'gemini' and grunnable is None:
        raise ValueError("grunnable is required when model='gemini'")
    
    # Split articles into batches
    batches = [articles[i:i + batch_size] for i in range(0, len(articles), batch_size)]
    all_results = []
    
    print(f"Processing {len(articles)} articles in {len(batches)} batches of {batch_size}")
    
    for batch_idx, batch in enumerate(batches, 1):
        print(f"\nProcessing batch {batch_idx}/{len(batches)} ({len(batch)} articles)...")
        
        batch_results = []
        
        # Process batch in parallel
        with ThreadPoolExecutor(max_workers=min(max_workers, len(batch))) as executor:
            # Submit all tasks in the batch
            future_to_article = {
                executor.submit(
                    process_single_article_aj, 
                    article, 
                    model, 
                    headers, 
                    runnable, 
                    grunnable
                ): article for article in batch
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_article):
                article = future_to_article[future]
                try:
                    result = future.result()
                    batch_results.append(result)
                    
                    # Print progress
                    if result['status'] == 'success':
                        print(f"✓ {result['title']}")
                    elif result['status'] == 'skipped':
                        print(f"→ Skipped: {result['title']}")
                    elif result['status'] == 'parsing_error':
                        print(f"⚠ Parsing error: {result['title']} - {result['message']}")
                    else:
                        print(f"✗ Error: {result['title']} - {result['message']}")
                        
                except Exception as e:
                    error_result = {
                        'status': 'error',
                        'title': article.get('title', 'Unknown'),
                        'url': article.get('link', 'Unknown'),
                        'message': f'Future execution error: {str(e)}'
                    }
                    batch_results.append(error_result)
                    print(f"✗ Future error: {article.get('link', 'Unknown')} - {str(e)}")
        
        all_results.extend(batch_results)
        
        # Print batch summary
        success_count = sum(1 for r in batch_results if r['status'] == 'success')
        skipped_count = sum(1 for r in batch_results if r['status'] == 'skipped')
        error_count = sum(1 for r in batch_results if r['status'] == 'error')
        
        print(f"Batch {batch_idx} complete: {success_count} success, {skipped_count} skipped, {error_count} errors")
        
        # Delay between batches (except for the last batch)
        if batch_idx < len(batches):
            print(f"Waiting {delay_between_batches}s before next batch...")
            time.sleep(delay_between_batches)
    
    return all_results

