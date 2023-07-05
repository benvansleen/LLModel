import requests
from os import getenv, system
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored, cprint
from dotenv import load_dotenv
load_dotenv()


# MODEL = 'gpt-3.5-turbo-0613'
MODEL = 'gpt-4-0613'


def llm(
        messages,
        functions=None,
        function_call=None,
        model=MODEL,
):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {getenv("OPENAI_API_KEY")}'
    }
    json_data = {'model': model, 'messages': messages}
    if functions is not None:
        json_data.update({'functions': functions})
    if function_call is not None:
        json_data.update({'function_call': function_call})

    for n in range(3):
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
            return response

        except requests.exceptions.HTTPError as e:
            cprint(e, 'red', attrs=['bold'])
            import time; time.sleep(n + 0.5)

    raise Exception('Unable to generate ChatCompletion response')


def print_conversation(messages, clear=True):
    if clear:
        system('clear')

    role_to_color = {
        'system': 'red',
        'user': 'green',
        'assistant': 'blue',
        'function_call': 'yellow',
        'function': 'magenta',
    }

    def format_message(message):
        match message['role']:
            case 'system':
                return (
                    f'system: {message["content"]}',
                    role_to_color['system'],
                )

            case 'user':
                return (
                    f'user: {message["content"]}',
                    role_to_color['user'],
                )

            case 'assistant':
                if 'function_call' in message:
                    message = message['function_call']
                    return (
                        f'assistant ({message["name"]}): {message["arguments"]}',
                        role_to_color['function_call'],
                    )
                else:
                    return (
                        f'assistant: {message["content"]}',
                        role_to_color['assistant'],
                    )

            case 'function':
                return (
                    f'function ({message["name"]}): {message["content"]}',
                    role_to_color['function'],
                )

            case _:
                raise ValueError(f'Unknown role: {message["role"]}')

    for message in messages:
        print(colored(*format_message(message)))

    return
