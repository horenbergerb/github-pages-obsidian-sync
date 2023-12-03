# Use Debian slim image
FROM debian:bullseye-slim

# Install git and cron
RUN apt-get update \
    && apt-get install -y git cron wget python3.9 python3-pip\
    && rm -rf /var/lib/apt/lists/*

RUN pip install markdownify feedparser

RUN mkdir /staging
RUN mkdir /parsed_staging

# Copy the script that handles file copying and git operations
COPY src/github_blog_sync/copy_and_commit.sh /usr/local/bin/copy_and_commit.sh
RUN chmod +x /usr/local/bin/copy_and_commit.sh

COPY src/rss_feed_capture/update_news_feed.sh /usr/local/bin/update_news_feed.sh
RUN chmod +x /usr/local/bin/update_news_feed.sh

COPY src/rss_feed_capture/create_news_markdown.py /usr/local/bin/create_news_markdown.py
RUN chmod +x /usr/local/bin/create_news_markdown.py

# Download the script for converting Obsidian files to markdown
RUN wget https://github.com/zoni/obsidian-export/releases/download/v22.11.0/obsidian-export_Linux-x86_64.bin -O /usr/local/bin/obsidian-export
RUN chmod +x /usr/local/bin/obsidian-export

# Set environment variables
# Login credentials for pushing changes
ENV GITHUB_EMAIL="horenbergerbeau@gmail.com"
ENV GITHUB_USERNAME="horenbergerb"
ARG GITHUB_TOKEN
# The repo you will be updating
ENV GITHUB_REPO_OWNER="horenbergerb"
ENV GITHUB_REPO_NAME="horenbergerb.github.io"
ENV REPO_DEST_DIR="_posts"
ENV REPO_IMAGE_DIR="images/obsidian"

RUN env >> /etc/environment

# Clone and set up the GitHub repository
RUN git clone https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO_OWNER}/${GITHUB_REPO_NAME} /repo

# Make output directories if they don't exist
RUN mkdir -p /repo/${REPO_IMAGE_DIR}
RUN mkdir -p /repo/${REPO_DEST_DIR}

# Set up the cron job
RUN echo "0 */2 * * * /usr/local/bin/copy_and_commit.sh >> /cronlog_blog.txt 2>&1" > /etc/cron.d/obsidian_sync_cron
RUN echo "0 */2 * * * /usr/local/bin/update_news_feed.sh >> /cronlog_news.txt 2>&1" > /etc/cron.d/obsidian_sync_cron
RUN chmod 0644 /etc/cron.d/obsidian_sync_cron
RUN crontab /etc/cron.d/obsidian_sync_cron

# Entrypoint
CMD ["cron", "-f"]