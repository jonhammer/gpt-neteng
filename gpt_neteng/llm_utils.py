import logging

from anthropic import Anthropic
from dotenv import load_dotenv

from gpt_neteng.prompts import SYSTEM_PROMPT, TOPOLOGY_PROMPT

load_dotenv()


def create_initial_prompt(topology_type, topology_data, task):
    task = f"Task: {task}"
    topology_prompt = TOPOLOGY_PROMPT
    topology_prompt = f"{topology_prompt}\n{task}"

    message = {"role": "user", "content": None}

    if topology_type == "image":
        message["content"] = [  # noqa
            {"type": "text", "text": topology_prompt},
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": topology_data,
                },
            },
        ]
    else:
        message["content"] = f"{topology_data}\n{topology_prompt}"

    return [message]


def send_message_to_claude(messages, device_type):
    client = Anthropic()  # Must set ANTHROPIC_API_KEY environment variable
    logging.debug(f"Sending message to Claude: {messages}")
    system_prompt = (
        SYSTEM_PROMPT
        + f"\nThe commands you run should always use {device_type} syntax."
    )
    try:
        response = client.messages.create(
            system=system_prompt,
            max_tokens=1024,
            messages=messages,
            model="claude-3-opus-20240229",
        )
        logging.debug(f"Response received from Claude: {response}")
    except Exception as e:
        print(f"messages : {messages}")
        raise

    return response
