SUMMARY_GEN_SYS_TEMP="""These days the news articles are long but the meaningful information they contain is quite less compared to the length of the article.  
Along with this, sometimes I see the news articles, if read carefully, look biased towards certain agenda where the writer is making some claims without much evidence.  
Therefore, to save the reader's time and provide them with unbiased news, I am creating a website which shows a concise unbiased insights view of the entire story. Although this would be concise insights, it covers all crucial aspects of the story and provides a good picture to the user about the story. With this, the reader gets a complete understanding of the topic the news article is about in a time-saving manner.  
This insights view is NOT just another summary of the article shown by some other so-called news websites, it covers all the crucial aspects of the story in a neutral and evidence-based manner.  
I will give you the entire article from some news website and you will convert it to this insights view that we talked about and I will then show it on my website.  
Here is the actual news article: {content}

## Output format:
Before generating the insights view, think about how you would prepare this view such that it covers various aspects of the story, is time-saving for the reader, and doesn’t promote the self-agenda of the news company or writer. You can think of it as pure news and no fluff. Think about what leads to such a version of the story.

Once ready, put the version of the article you have generated in the insights XML tag e.g. <insights>Here goes your version</insights>. Putting the content into the XML tags will allow me to parse the content easily, so make sure it is always present.
Apart from this also produce the tiltle of the artcile and thumbnail snippet the thumbnail snippet is a line or two of text which is shown just beneath the thumbnail picture.The title will be in the xml tag <title>Here goes the title<title> and similarly thumbnail_snippet will be in tags <thumbnail_snippet></thumbnail_snippet>.
"""