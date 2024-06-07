#!/bin/bash
# Save the current directory name
current_dir=$(basename "$PWD")

# Run the push script and ensure it completes successfully
if ./push.sh; then
    # If the push script completes successfully, delete the repository
    cd ..
    rm -rf $current_dir
else
    # If the push script fails, do not delete the repository
    echo "Push failed. Repository not deleted."
fi
# Streamline the process of deleting the repo only after push is finished

# Push Backout Delete (PBD) script
