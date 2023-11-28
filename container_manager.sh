#!/bin/bash

IMAGE_NAME="obsidian-github-sync"
CONTAINER_NAME="obsidian_sync_container"

start_container() {
    echo "Starting container..."
	
	# Build the Docker image
	docker build -t $IMAGE_NAME . \
        --build-arg GITHUB_TOKEN="$(cat github_token.txt)"

	# Run the Docker container
	docker run --init -d \
		--name $CONTAINER_NAME \
		-v /home/captdishwasher/Documents/Blog\ Vault:/obsidian \
		$IMAGE_NAME

    echo "Container started."
}

stop_container() {
    echo "Stopping container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    echo "Container stopped."
}

print_container_logs() {
    echo "Printing container logs..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    echo "Container logs printed."
}

enter_container_bash() {
    echo "Running bash in container..."
    docker exec -it $CONTAINER_NAME bash
    echo "Container bash terminated."
}


# Check the command line argument
case "$1" in
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    logs)
        print_container_logs
        ;;
    bash)
        enter_container_bash
        ;;
    *)
        echo "Usage: $0 {start|stop|logs|bash}"
        exit 1
esac
