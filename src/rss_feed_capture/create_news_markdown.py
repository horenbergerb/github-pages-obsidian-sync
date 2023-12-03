import feedparser
from markdownify import markdownify as md
from os import path
import argparse
from datetime import datetime
import sqlite3
from zoneinfo import ZoneInfo

# The URL of the RSS feed
#rss_url = 'http://arxiv.org/rss/cs.LG'
rss_urls = ['https://hnrss.org/frontpage', 'http://arxiv.org/rss/cs.LG']

class RssSource:
    def __init__(self, rss_url, feed_title, has_date):
        self.rss_url = rss_url
        self.feed_title = feed_title
        self.has_date = has_date

rss_sources = []
rss_sources.append(RssSource('https://hnrss.org/frontpage', 'Hacker News Front Page', True))
rss_sources.append(RssSource('http://arxiv.org/rss/cs.LG', 'Arxiv cs.LG', False))



def convert_to_iso_format(date_string):
    # Parsing the original date string
    parsed_date = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")
    
    # Converting to ISO 8601 format (without timezone information)
    iso_format_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
    
    return iso_format_date


def insert_new_items(db_connection, items, feed_title, has_date):
    cursor = db_connection.cursor()
    for item in items:
        # Assuming each item has 'id', 'title', 'link', and 'published' fields
        # Adjust the fields based on your RSS feed structure
        item_id = item.get('id', item.link)  # Using link as a fallback unique identifier
        title = item.title
        link = item.link
        published = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M:%S")
        if has_date:
            published = convert_to_iso_format(item.published)

        # Check if the item already exists to avoid duplicates
        cursor.execute('SELECT id FROM news_items WHERE id = ?', (item_id,))
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO news_items (id, feed_title, title, link, published) VALUES (?, ?, ?, ?, ?)',
                           (item_id, feed_title, title, link, published))

    db_connection.commit()


def get_recent_news_items(db_connection, num_items=10):
    cursor = db_connection.cursor()
    query = "SELECT title, link, published FROM news_items ORDER BY published DESC LIMIT {}".format(num_items)
    cursor.execute(query)
    return cursor.fetchall()


def get_todays_news_items(db_connection, feed_title):
    cursor = db_connection.cursor()
    today_date = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")  # Format the date as YYYY-MM-DD

    # SQL query to select articles published today
    query = "SELECT title, link, published FROM news_items WHERE date(published) = ? AND feed_title = ? ORDER BY published DESC"
    cursor.execute(query, (today_date, feed_title,))
    
    return cursor.fetchall()


def create_news_markdown(out_dir):
    # Connect to SQLite database
    db_connection = sqlite3.connect('news_feed.db')

    # Create table if it doesn't exist
    cursor = db_connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS news_items
                      (id TEXT PRIMARY KEY, feed_title TEXT, title TEXT, link TEXT, published TEXT)''')
    db_connection.commit()

    md_output = ''

    for rss_source in rss_sources:
        # Fetch and parse the RSS feed
        feed = feedparser.parse(rss_source.rss_url)

        # Insert new items into the database
        insert_new_items(db_connection, feed.entries, rss_source.feed_title, rss_source.has_date)

        # Get the 10 most recent items from the database
        recent_news = get_todays_news_items(db_connection, rss_source.feed_title)

        md_output += '### ' + rss_source.feed_title + '\n\n'

        for item in recent_news:
            if rss_source.has_date:
                title, link, published = item
                published = datetime.strptime(published, "%Y-%m-%d %H:%M:%S")

                md_output += published.strftime("%H:%M") + ' [' + title + '](' + link + ')\n'
            else:
                title, link, published = item
                if rss_source.feed_title.startswith('Arxiv'):
                    title = title.split(' (arXiv')[0]
                md_output += '04:20' + ' [' + title + '](' + link + ')\n'

    # Get the current date in the desired format (YYYY-MM-DD)
    current_date = datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%d')
    # The file name with the current date and .md extension
    filename = f"{current_date}.md"

    with open(path.join(out_dir, filename), 'w') as file:
        # Write the string to the file
        file.write(md_output)

if __name__ == '__main__':
    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Generate a markdown file with news from RSS feeds.')
    parser.add_argument('output_dir', help='The directory where the file will be saved.')

    # Parse the command line arguments
    args = parser.parse_args()

    create_news_markdown(args.output_dir)
