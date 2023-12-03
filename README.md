# Obsidian Github Pages Sync

This project automatically updates your github pages blog with files from your Obsidian vault.

![Example showing an Obsidian note and the corresponding page on my blog.](README/example_blog_upload.png)

I am also tentatively expanding the vision of this project. I recently added support for parsing RSS feeds into Obsidian notes.

![Example showing an RSS feed which was automatically uploaded into Obsidian.](README/example_rss_feed.png)

# Setup

## Configuration

Configuration is in a bad state right now. There are directories and arguments that need to be configured in container_manager.sh, copy_and_commit.sh, and Dockerfile. You also need to add your github token in a github_token.txt file.

## Running the docker

To run, simply execute `./container_manager.sh start`

You can stop the docker container with `./container_manager.sh stop`

container_manager also has utilities for troubleshooting the container. Run './container_manager' for more info.

# How it works

## How Obsidian is synchronized with a Github Pages blog

### Periodically identify Obsidian pages to upload

1) The Dockerfile creates a cron job which periodically runs copy_and_commit.sh
2) copy_and_commit.sh compares the Obsidian dir to a staging directory. If there is no difference, exit
3) If there is a difference, clear the staging directory and copy the obsidian dir into staging

### Parse and upload Obsidian new pages

1) Parse the staging dir into blog-compatible markdown and output to the a parsed staging directory
2) Copy all images from Obsidian image dir to the user-specified github pages directory.
3) Update image references in markdown
4) Parse the staging dir into blog-compatible markdown and output to the user-specififed github pages directory
5) Commit the changes to github

## How RSS feeds are uploaded to Obsidian notes

This is pretty simple. Cron job periodically runs a python script to retrieve news from RSS feeds. This is stored and organized in a sqlite database. Then the titles of the most recent news articles are parsed into a markdown format and added to Obsidian.

# FAQ

#### I want to synchronize Obsidian with my blog, but I don't want the news feed stuff. What should I do?

Create an issue in the GitHub repo. To my knowledge, I'm the only one using this code, but I'd happily make accomodations if anyone else wanted to use this. Make me aware and I'll see what I can do