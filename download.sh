#!/bin/bash

# URL of the file
FILE_URL="https://www.aphis.usda.gov/sites/default/files/awa-hpa-actions.csv"

# Target directory
TARGET_DIR="/Users/XXXX/My Drive/IFTTT/aphis_usda_gov_actions/csv"

# Create directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Download file into the directory
curl -L "$FILE_URL" -o "$TARGET_DIR/$(basename "$FILE_URL")"