# Use Debian slim image
FROM debian:bullseye-slim

# Install git and cron
RUN apt-get update \
    && apt-get install -y git cron wget\
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /staging
RUN mkdir /parsed_staging

# Copy the script that handles file copying and git operations
COPY copy_and_commit.sh /usr/local/bin/copy_and_commit.sh
RUN chmod +x /usr/local/bin/copy_and_commit.sh

# Download the script for converting Obsidian files to markdown
RUN wget https://github.com/zoni/obsidian-export/releases/download/v22.11.0/obsidian-export_Linux-x86_64.bin -O /usr/local/bin/obsidian-export
RUN chmod +x /usr/local/bin/obsidian-export

# Set environment variables
# Login credentials for pushing changes
ENV GITHUB_EMAIL="horenbergerbeau@gmail.com"
ENV GITHUB_USERNAME="horenbergerb"
RUN export GITHUB_TOKEN="$(cat github_token.txt)"
# The repo you will be updating
ENV GITHUB_REPO_OWNER="horenbergerb"
ENV GITHUB_REPO_NAME="horenbergerb.github.io"
ENV REPO_DEST_DIR="_posts"
ENV REPO_IMAGE_DIR="images/obsidian"

# Clone and set up the GitHub repository
RUN git clone https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO_OWNER}/${GITHUB_REPO_NAME} /repo

# Make output directories if they don't exist
RUN mkdir -p /repo/${REPO_IMAGE_DIR}
RUN mkdir -p /repo/${REPO_DEST_DIR}

# Set up the cron job
RUN echo "* * * * * /bin/bash -c '/usr/local/bin/copy_and_commit.sh >> /proc/1/fd/1'" > /etc/cron.d/obsidian_sync_cron
RUN chmod 0644 /etc/cron.d/obsidian_sync_cron
RUN crontab /etc/cron.d/obsidian_sync_cron

# Entrypoint
CMD ["cron", "-f"]