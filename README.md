# Obsidian Github Pages Sync

This project automatically updates your github pages blog with files from your Obsidian vault.

## Configuration

Configuration is in a bad state right now. There are directories and arguemnts that need to be configured in container_manager.sh, copy_and_commit.sh, and Dockerfile. You also need to add your github token in a github_token.txt file.

## Running the docker

To run, simply execute `./container_manager.sh start`

You can stop the docker container with `./container_manager.sh stop`

container_manager also has utilities for troubleshooting the container. Run './container_manager' for more info.

# How it works

## Periodically identify Obsidian pages to upload

1) The Dockerfile creates a cron job which periodically runs copy_and_commit.sh
2) copy_and_commit.sh compares the Obsidian dir to a staging directory. If there is no difference, exit
3) If there is a difference, clear the staging directory and copy the obsidian dir into staging

## Parse and upload Obsidian new pages

1) Parse the staging dir into blog-compatible markdown and output to the a parsed staging directory
2) Copy all images from Obsidian image dir to the user-specified github pages directory.
3) Update image references in markdown
4) Parse the staging dir into blog-compatible markdown and output to the user-specififed github pages directory
5) Commit the changes to github