#!/bin/bash
# Wait for LocalStack to be ready by checking DynamoDB availability

set -e

MAX_ATTEMPTS=30
ATTEMPT=0
DELAY=1

echo "Waiting for LocalStack DynamoDB to be ready..."

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  if curl -s http://localhost:4566/health > /dev/null 2>&1; then
    # Check if DynamoDB is actually responding
    if aws dynamodb list-tables --endpoint-url http://localhost:4566 --region us-east-1 > /dev/null 2>&1; then
      echo "✓ LocalStack is ready"
      exit 0
    fi
  fi

  ATTEMPT=$((ATTEMPT + 1))
  if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
    echo "  Attempt $ATTEMPT/$MAX_ATTEMPTS - waiting for LocalStack..."
    sleep $DELAY
  fi
done

echo "⚠ LocalStack health check timed out after ${MAX_ATTEMPTS} attempts, proceeding anyway..."
exit 0
