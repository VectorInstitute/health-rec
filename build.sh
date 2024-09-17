#!/bin/bash

# Set PROJECT_NAME
PROJECT_NAME="health-rec"

# Set BUILD_ID
export BUILD_ID=$(date +%Y%m%d)

# Build development images
docker compose --env-file .env.development -f docker-compose.dev.yml build

# # Build production images
# docker compose --env-file .env.production -f docker-compose.yml build
#
# # Tag development images as latest
docker tag vectorinstitute/${PROJECT_NAME}:frontend-dev-${BUILD_ID} vectorinstitute/${PROJECT_NAME}:frontend-dev-latest
docker tag vectorinstitute/${PROJECT_NAME}:backend-dev-${BUILD_ID} vectorinstitute/${PROJECT_NAME}:backend-dev-latest
#
# # Tag production images as latest
# docker tag vectorinstitute/${PROJECT_NAME}:frontend-${BUILD_ID} vectorinstitute/${PROJECT_NAME}:frontend-latest
# docker tag vectorinstitute/${PROJECT_NAME}:backend-${BUILD_ID} vectorinstitute/${PROJECT_NAME}:backend-latest

# Push all images (uncomment when ready to push)
# docker push vectorinstitute/${PROJECT_NAME}:frontend-dev-${BUILD_ID}
# docker push vectorinstitute/${PROJECT_NAME}:backend-dev-${BUILD_ID}
# docker push vectorinstitute/${PROJECT_NAME}:frontend-${BUILD_ID}
# docker push vectorinstitute/${PROJECT_NAME}:backend-${BUILD_ID}
# docker push vectorinstitute/${PROJECT_NAME}:frontend-dev-latest
# docker push vectorinstitute/${PROJECT_NAME}:backend-dev-latest
# docker push vectorinstitute/${PROJECT_NAME}:frontend-latest
# docker push vectorinstitute/${PROJECT_NAME}:backend-latest
