#!/bin/bash
# Save the current directory name
current_dir=$(basename "$PWD")

# Run the push script and ensure it completes successfully
./push.sh && cd .. && rm -rf "$current_dir"

# Streamline the process of deleting the repo only after push is finished

# Push Backout Delete (PBD) script
