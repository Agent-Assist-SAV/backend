#!/bin/bash

TEMPLATE_FILE=".env.template"
TARGET_FILE=".env"

if [ -f "$TARGET_FILE" ]; then
    echo "$TARGET_FILE already exists. Please delete it if you want to recreate it."
    exit 1
fi

echo "Creating $TARGET_FILE from $TEMPLATE_FILE..."
# for each line in the template file, ask the user for the value
while read line; do
    if [[ $line == \#* || -z $line ]]; then
        # comment or empty line, copy as is
        echo "$line" >> "$TARGET_FILE"
    else
        VAR_NAME=$(echo "$line" | cut -d '=' -f 1)
        echo "Enter value for $VAR_NAME:"
        read VAR_VALUE </dev/tty
        echo "$VAR_NAME=$VAR_VALUE" >> "$TARGET_FILE"
    fi
done < "$TEMPLATE_FILE"