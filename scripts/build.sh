#!/bin/bash

if [ -z "$1" ]; then
  TAG="latest"
  echo "Tag ('$TAG' by default):"
  read tag
  if [ "$tag" != "" ]; then
    TAG="$tag"
  fi
else
  TAG="$1"
fi

source .env
docker build -t $DOCKER_IMAGE_REPO_NAME:$TAG .

echo "Push image to Docker Hub? (y/n)"
read push_image
if [ "$push_image" == "y" ]; then
    docker push $DOCKER_IMAGE_REPO_NAME:$TAG
fi
