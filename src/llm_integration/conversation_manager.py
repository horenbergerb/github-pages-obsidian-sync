import sys
import openai
import os


def parse_markdown_conversation(file_path):
    '''Opens a markdown file and converts it into a format
    which is compatible with the standard OpenAI API format for
    conversations. Returns the formatted conversation and the
    status marked in the file'''
    with open(file_path, 'r') as file:
        lines = file.readlines()

    messages = []
    current_speaker = None
    current_message = []
    status = ""

    for line in lines:
        if line.startswith("####"):
            if current_speaker and current_message:
                messages.append({
                    "role": current_speaker.lower(),
                    "content": '\n'.join(current_message).strip()
                })
                current_message = []

            current_speaker = "assistant" if "LLM" in line else "user"
        # The last line starting with a hashtag is the status
        elif line.startswith("#") and not line.startswith("####"):
            status = line[1:].strip()
        elif current_speaker:
            current_message.append(line.rstrip('\n'))

    # Reset the status if it's garbage
    if status not in ['r', 'g']:
        status = ''

    # Add the last message if it exists
    if current_speaker and current_message:
        messages.append({
            "role": current_speaker.lower(),
            "content": '\n'.join(current_message).strip()
        })

    return messages, status


def retrieve_conversations_and_paths_from_directory(directory):
    '''Iterates over all files in a directory, parsing each one into
    the OpenAI API conversation format. Returns all conversations, statuses,
    and the corresponding filepaths'''
    conversations_and_paths = []

    # Loop through each file in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        if os.path.isfile(filepath):
            messages, status = parse_markdown_conversation(filepath)
            conversations_and_paths.append((messages, filepath, status))

    return conversations_and_paths


def convert_llama_cpp_format_to_markdown(messages):
    '''Converts the OpenAI API format for conversations back into
    the markdown format which is rendered in Obsidian.'''
    markdown_content = []

    for message in messages:
        if message["role"] == 'system':
            continue
        speaker = "User" if message["role"] == "user" else "LLM"
        content = message["content"]

        markdown_content.append(f"#### {speaker}\n{content}\n")
    markdown_content.append('#### User\n')
    return ''.join(markdown_content)


def check_if_update_needed():
    directory = '/obsidian/conversation'
    conversations_and_paths = retrieve_conversations_and_paths_from_directory(directory)

    # Loop through each file in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        if os.path.isfile(filepath):
            if 'DONE' in filepath:
                continue
            with open(filepath, 'r') as file:
                content = file.read()
                if content.strip().endswith('#g'):
                    print('True')
                    return
    print('False')
    return


def update_all_conversations():
    client = openai.OpenAI(
    base_url="http://localhost:8080/v1", # "http://<Your api-server IP>:port"
    api_key = "sk-no-key-required"
)
    
    directory = '/obsidian/conversation'
    conversations_and_paths = retrieve_conversations_and_paths_from_directory(directory)

    for messages, filepath, status in conversations_and_paths:
        if status == 'g':
            completion = client.chat.completions.create(model="gpt-3.5-turbo",messages=messages,extra_body={'cache_prompt': True})
            messages.append({'role': 'assistant', 'content': completion.choices[0].message.content})
            updated_file_content = convert_llama_cpp_format_to_markdown(messages)
            with open(filepath, 'w') as file:
                file.write(updated_file_content)


if __name__ == '__main__':
    # Check if any arguments were provided
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'check':
            # Call check_if_update_needed method
            check_if_update_needed()
        elif command == 'update':
            # Call update_all_conversations method
            update_all_conversations()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    else:
        print("No command provided")
        sys.exit(1)