from feed import Feed
from datetime import datetime
from zoneinfo import ZoneInfo

feed_list = []

###############
# ARXIV CS.lg #
###############
def create_arxiv_cs_lg_feed():
    feed_url = 'http://arxiv.org/rss/cs.LG'
    title = 'Arxiv cs.LG'
    field_dict = {'title': 'title', 'link': 'link', 'description': 'description'}
    sql_table = 'arxiv_cs_lg'

    query = 'SELECT title, link, description, published FROM {} ORDER BY published DESC LIMIT 10'

    def parse_arxiv_items_to_markdown(items):
        md_output = ''
        for item in items:
            title, link, description, published = item
            md_output += '### [' + title + '](' + link + ')\n'
            md_output += description
            md_output += '\n'

        return md_output

    return Feed(feed_url, title, field_dict, parse_arxiv_items_to_markdown, sql_table, query)

###############
# Hacker News #
###############

def create_hacker_news_front_page_feed():
    feed_url = 'https://hnrss.org/frontpage'
    title = 'Hacker News Front Page'
    field_dict = {'title': 'title', 'link': 'link', 'description': 'description'}
    sql_table = 'hacker_news_front_page'

    today_date = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
    query = "SELECT title, link, description, published FROM {} WHERE date(published) = '" + today_date + "' ORDER BY published DESC"

    def parse_hacker_news_items_to_markdown(items):
        md_output = ''
        for item in items:
            title, link, description, published = item
            published = datetime.strptime(published, "%Y-%m-%d %H:%M:%S")
            md_output += published.strftime("%H:%M") + ' [' + title + '](' + link + ')\n'

        return md_output

    return Feed(feed_url, title, field_dict, parse_hacker_news_items_to_markdown, sql_table, query, "%a, %d %b %Y %H:%M:%S %z")

#############
# Feed List #
#############

feed_list.append(create_hacker_news_front_page_feed())
feed_list.append(create_arxiv_cs_lg_feed())

if __name__ == '__main__':
    for feed in feed_list:
        feed.update()
        print(feed.retrieve_entries_as_markdown())