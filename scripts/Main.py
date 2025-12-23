import os
import feedparser
import time
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from deep_translator import GoogleTranslator


# Feeds de interés: 
''' Specific RSS urls (these are the equivalent to an XML made link) '''

AP_news_url = "https://news.google.com/rss/search?q=https%3A%2F%2Fapnews.com%2Fnoticias&hl=es-419&gl=US&ceid=US%3Aes-419" #AP news google news funnel
Reuters_url = "https://news.google.com/rss/search?q=latin%20america%20site%3Ahttps%3A%2F%2Fwww.reuters.com%2Fworld%2Famericas&hl=es-419&gl=US&ceid=US%3Aes-419" #Reuters Americas - Needs translation - google news funnel
Inforbae_url = "https://news.google.com/rss/search?q=site%3Ahttps%3A%2F%2Fwww.infobae.com%2Famerica&hl=es-419&gl=US&ceid=US%3Aes-419" # Infobae google news funnel


scrap_list = [AP_news_url,Reuters_url,Inforbae_url]

#Generate list with all of the URLs for the scrapper element, prioritize obtaining the URL to original post and scale up from there
def scrape_article(target_url, output_file="rss_feed.txt"):
    try:
        print(f"Obteniendo feed desde {target_url}. . .")
        feed = feedparser.parse(target_url)

        if feed.bozo:
            print(f"Feed parsing error (recovered): {feed.bozo_exception}")

        print(f"Found {len(feed.entries)} entries")

        with open(output_file, "a", encoding="utf-8") as file:
            for entry in feed.entries[:10]:
                title = entry.title
                link = entry.link

                if target_url == Reuters_url:
                    
                    trans_title = GoogleTranslator(source='auto', target='es').translate(title)

                    file.write(f"Title: {trans_title}\n")
                else:
                    file.write(f"Link: {link}\n")
                
                file.write(f"Link: {link}\n\n")
                print(f"Saved: {title}")
        print(f"Done! Saved to {output_file}")
    except Exception as e:
        print(f"Error scraping {target_url}: {e}")
        return None

for i in scrap_list:
    scrape_article(i)