#!/bin/bash

# Path to the server manager script
SERVER_MANAGER_SCRIPT="/src/llm_integration/llama_cpp_server_manager.sh"

# File to track the last update time
LAST_UPDATE_FILE="/tmp/last_conversation_update"

# Function to update the last update time
update_last_update_time() {
    date +%s > "$LAST_UPDATE_FILE"
}

# Check if the conversations need to be updated
needs_update=$(python3 /src/llm_integration/conversation_manager.py check)

# If conversations need to be updated
if [[ $needs_update == "True" ]]; then
    # Start the LLM server
    "$SERVER_MANAGER_SCRIPT" start

    # Run the update
    python3 /src/llm_integration/conversation_manager.py update

    # Update the last update time
    update_last_update_time
else
    # Get the current time and the last update time
    current_time=$(date +%s)
    last_update_time=$(cat "$LAST_UPDATE_FILE" 2>/dev/null || echo 0)

    # Calculate the time difference in minutes
    time_diff=$(( (current_time - last_update_time) / 60 ))

    # If an update has not been needed in over 30 minutes
    if [[ $time_diff -gt 30 ]]; then
        # Stop the LLM server
        "$SERVER_MANAGER_SCRIPT" stop
    fi
fi
