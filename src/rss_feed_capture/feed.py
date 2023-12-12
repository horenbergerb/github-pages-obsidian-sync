import feedparser
import sqlite3

from datetime import datetime
from zoneinfo import ZoneInfo


class Feed:
    '''
    This manages a single RSS feed.
    Use update() to retrieve the feed and store to a sqlite database
    Use retrieve_entries() to get the feed from the sqlite database
    Use retrieve_entries_as_markdown() to get the feed formatted into markdown
    '''
    def __init__(self, url, title, field_dict, parse_to_markdown_func, sql_table, retrieve_recent_query, date_format_string=None):
        self.url = url
        self.title = title
        self.sql_table = sql_table

        # Map raw feed labels (keys) to database labels (values), ex 'about' -> 'description'
        self.field_dict = field_dict
        # Function for taking a database item and rendering the information in markdown
        self.parse_to_markdown_func = parse_to_markdown_func
        # String to express the date format used by the raw RSS feed
        self.date_format_string = date_format_string
        # Default query to retrieve recent news
        self.retrieve_recent_query = retrieve_recent_query
        if self.retrieve_recent_query is not None:
            self.retrieve_recent_query = self.retrieve_recent_query.format(self.sql_table)

        # Connect to SQLite database
        self.db_connection = sqlite3.connect('feeds.db')
        self.cursor = self.db_connection.cursor()

        # Create table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS {}
                          (id TEXT PRIMARY KEY, title TEXT, link TEXT, description TEXT, published TEXT)'''.format(sql_table))
        self.db_connection.commit()

    def _retrieve_raw_feed(self):
        return feedparser.parse(self.url)

    def update(self):
        '''Retrieves the feed from the URL and adds entries to the database'''
        feed = self._retrieve_raw_feed()

        for item in feed.entries:
            item_id = item.get('id', item.link)
            
            new_item = {'title': '', 'link': '', 'description': '', 'published': datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M:%S")}

            for feed_key, db_key in self.field_dict.items():
                new_item[db_key] = item[feed_key]

            if 'published' in self.field_dict.values():
                parsed_date = datetime.strptime(new_item['published'], self.date_format_string)
                iso_format_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                new_item['published'] = iso_format_date

            # Check if the item already exists to avoid duplicates
            self.cursor.execute('SELECT id FROM {} WHERE id = ?'.format(self.sql_table), (item_id,))
            if self.cursor.fetchone() is None:
                self.cursor.execute('INSERT INTO {} (id, title, link, description, published) VALUES (?, ?, ?, ?, ?)'.format(self.sql_table),
                                (item_id, new_item['title'], new_item['link'], new_item['description'], new_item['published']))
        
        self.db_connection.commit()

    def retrieve_entries(self, query):
        self.cursor.execute(query.format(self.sql_table))
        return self.cursor.fetchall()

    def retrieve_entries_as_markdown(self, query=None):
        if query is None:
            query = self.retrieve_recent_query
        items = self.retrieve_entries(query)

        return self.parse_to_markdown_func(items)
