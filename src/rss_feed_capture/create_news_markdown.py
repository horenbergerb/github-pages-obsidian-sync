from os import path
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from feeds import feed_list


def create_news_markdown(out_dir):
    md_output = ''
    for feed in feed_list:
        feed.update()

        md_output += '### ' + feed.title + '\n\n'
        md_output += feed.retrieve_entries_as_markdown()
        md_output += '\n'

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
