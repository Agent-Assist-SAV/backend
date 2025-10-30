#!/bin/bash

set -a
source .env
set +a

# Create a temporary values file with environment variable substitution 
TEMP_VALUES=$(mktemp)
envsubst < ./helm/backend-chart/values.yaml > "$TEMP_VALUES"

# Deploy with the temporary file
helm upgrade --install backend ./helm/backend-chart -n default -f "$TEMP_VALUES"

# Clean up the temporary file
rm "$TEMP_VALUES"