#!/bin/bash

OBSIDIAN_SOURCE_DIR="/obsidian"
OBSIDIAN_NEWS_POSTS_DIR="news"

# Run the python script to generate the news
# inputs: out directory (i.e. ${OBSIDIAN_SOURCE_DIR}/${OBSIDIAN_NEWS_POSTS_DIR})

python3 /src/rss_feed_capture/create_news_markdown.py ${OBSIDIAN_SOURCE_DIR}/${OBSIDIAN_NEWS_POSTS_DIR}