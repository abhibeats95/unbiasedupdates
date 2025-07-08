import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import boto3
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import threading
import os

from unbiasedupdates.utils import (
    lg_runnable, gemini_runnable, get_article_content_and_images_bbc, parse_rss_feed_bbc,
    get_aws_resources, process_articles_parallel_bbc, print_final_summary,
    parse_aljazeera_news_sitemap, process_articles_parallel_aj
)
from unbiasedupdates.prompts import SUMMARY_GEN_SYS_TEMP
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

# Constants and Setup
DAYS_BACK = 10
model = 'openai'

import boto3
import json
from boto3.session import Session

def get_secret():
    secret_name = "llmapikeys"
    region_name = "us-east-1"

    # Use a specific profile (locally only — not needed in Lambda)
    #session = Session(profile_name="root-access")
    #client = session.client(service_name='secretsmanager', region_name=region_name)
    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise

# Example usage
secrets = get_secret()
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]
GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]

llm_g_2_5 = ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=GOOGLE_API_KEY)
llm_g_2_5_f = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)
llm_4o = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

runnable = lg_runnable(llm=llm_4o, system_message=SUMMARY_GEN_SYS_TEMP)
grunnable = gemini_runnable(llm_g_2_5_f, template=SUMMARY_GEN_SYS_TEMP)

# Headers to mimic a real browser request
headers_bbc = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Headers to mimic a real browser request
headers_aj = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

rss_urls_bbc = [
    "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/business/rss.xml",
    "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/front_page/rss.xml",
    "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/entertainment/rss.xml",
    "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/health/rss.xml",
    "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/education/rss.xml",
    "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/uk_politics/rss.xml",
    "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/england/rss.xml",
    "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/technology/rss.xml",
    "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/world/rss.xml"
]

def lambda_handler(event, context):
    all_articles_bbc = []

    for url in rss_urls_bbc:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            articles = parse_rss_feed_bbc(response.content, days_back=DAYS_BACK)
            all_articles_bbc.extend(articles)
        except Exception as e:
            print(f"Error processing {url}: {e}")

    results_bbc = process_articles_parallel_bbc(
        articles=all_articles_bbc,
        batch_size=100,
        model=model,
        headers=headers_bbc,
        runnable=runnable,
        grunnable=grunnable,
        max_workers=5,
        delay_between_batches=2.0
    )

    print_final_summary(results_bbc)

    try:
        response = requests.get("https://www.aljazeera.com/news-sitemap.xml")
        aljazeera_articles = parse_aljazeera_news_sitemap(response.content, days_back=DAYS_BACK)

        results_aj = process_articles_parallel_aj(
            articles=aljazeera_articles,
            batch_size=100,
            model=model,
            headers=headers_aj,
            runnable=runnable,
            grunnable=grunnable,
            max_workers=5,
            delay_between_batches=2.0
        )

        print_final_summary(results_aj)
    except Exception as e:
        print(f"Error processing Al Jazeera: {e}")