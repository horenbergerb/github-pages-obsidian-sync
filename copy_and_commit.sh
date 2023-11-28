#!/bin/bash

# Config to handle empty directories with the for loops
shopt -s nullglob

# Set the source directory for Obsidian files (mounted volume)
OBSIDIAN_SOURCE_DIR="/obsidian"
OBSIDIAN_BLOG_POSTS_DIR="blog"
OBSIDIAN_IMAGES_DIR="attachments"
STAGING_DIR="/staging"
PARSED_STAGING_DIR="/parsed_staging"

# Don't run if there are no new changes
diff -r $OBSIDIAN_SOURCE_DIR/$OBSIDIAN_BLOG_POSTS_DIR $STAGING_DIR
diff_exit_code=$?
if [[ $diff_exit_code -eq 0 ]]; then
	echo "No changes to upload. copy_and_commit.sh exiting..."
	exit 1
fi

# Navigate to the repository directory
cd /repo

# Copy files which are marked as ready to staging
# Also parses each file to markdown and sends to parsed staging
for file in ${OBSIDIAN_SOURCE_DIR}/${OBSIDIAN_BLOG_POSTS_DIR}/*; do
    # Check if the file ends with '#ready'
    if tail -n1 "$file" | grep -q '#ready$'; then

		# Copy to the staging directory
		cp -r "$file" ${STAGING_DIR}/

		# Parse to parsed staging directory
		obsidian-export ${OBSIDIAN_SOURCE_DIR} ${PARSED_STAGING_DIR} --start-at "$file"
	fi
done

# Copy Obsidian images to the GitHub pages repo
cp -r ${OBSIDIAN_SOURCE_DIR}/${OBSIDIAN_IMAGES_DIR}/* /repo/${REPO_IMAGE_DIR}

# Add front matter and such
find ${PARSED_STAGING_DIR} -type f -exec sh -c 'echo "---\ntag: diary\n---\n\n$(cat {})" > {}' \;

# Fix image links to reference the correct path
# WARNING: This NEEDS TO BE CONFIGURED if you change the directories used for images
# I was too lazy to make this automatic and nice
find ${PARSED_STAGING_DIR} -type f -exec sed -i 's|\.\./attachments|/images/obsidian|g' {} +

for file in ${PARSED_STAGING_DIR}/*; do
	# Remove the last line (presumably '#ready') from the end of the file
	sed -i '$ d' "$file"

	# Copy the modified file to the output directory
	cp "$file" /repo/${REPO_DEST_DIR}
done

# Git operations
git config --global user.email $GITHUB_EMAIL
git config --global user.name $GITHUB_USERNAME
git add ${REPO_DEST_DIR}/*
git add ${REPO_IMAGE_DIR}/*
git commit -m "Journal Update"
git push origin master