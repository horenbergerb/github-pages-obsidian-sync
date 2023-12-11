#!/bin/bash

IMAGE_NAME="obsidian-github-sync"
CONTAINER_NAME="obsidian_sync_container"

create_container() {
    # Stop the container
    docker stop $CONTAINER_NAME
    # Delete the existing container
    docker rm $CONTAINER_NAME
	# Build the Docker image
	docker build -t $IMAGE_NAME . \
        --build-arg GITHUB_TOKEN="$(cat github_token.txt)"

    # Run the Docker container
	docker run --init -d \
		--name $CONTAINER_NAME \
		-v /home/captdishwasher/Documents/Blog\ Vault:/obsidian \
        -v ./src:/src \
		$IMAGE_NAME
}

start_container() {
    echo "Checking if container exists..."
    if [ $(docker ps -a | grep -w $CONTAINER_NAME) ]; then
        echo "Container exists. Starting container..."
        docker start $CONTAINER_NAME
        echo "Container started."
    else
        echo "Container does not exist. Creating container..."
        create_container
    fi
}

stop_container() {
    echo "Stopping container..."
    docker stop $CONTAINER_NAME
    echo "Container stopped."
}

restart_container() {
    stop_container
    start_container
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
    restart)
        restart_container
        ;;
    create)
        create_container
        ;;
    logs)
        print_container_logs
        ;;
    bash)
        enter_container_bash
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|create|logs|bash}"
        exit 1
esac
