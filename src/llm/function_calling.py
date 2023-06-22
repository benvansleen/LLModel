import json
from sys import argv
from documentation_agent import consult_control_documentation
from utils import llm, print_conversation
from semantic_search import search_embeddings


messages = [{
    'role': 'system',
    'content': "You are an expert in the field of model-based design. Your goal is to help the user design a model of interacting NonlinearIOSystem objects from the Python Control Library. Do NOT assume the existence of any other libraries or packages. PLEASE consult the library's documentation to ensure proper usage. Define only ONE system object at a time.",
}]


def wrap_prompt_in_context(prompt):
    # context = '\n'.join(search_embeddings(prompt))
    context = consult_control_documentation(prompt)
    return f'{context}\n\nGOAL: {prompt}'


if len(argv) > 1:
    messages.append({
        'role': 'user',
        'content': wrap_prompt_in_context(' '.join(argv[1:])),
    })


functions = [
    # {
    #     'name': 'consult_control_documentation',
    #     'description': 'Consult the documentation for the Python Control Library. Use keywords (like specific function or object names) to find examples and best practices.',
    #     'parameters': {
    #         'type': 'object',
    #         'properties': {
    #             'search_query': {
    #                 'type': 'string',
    #                 'description': 'The search query to use when searching the documentation.',
    #             },
    #         },
    #         'required': ['search_query'],
    #     },
    # },

    {
        'name': 'define_system',
        'description': 'Define a NonlinearIOSystem object.',
        'parameters': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'The name of the NonlinearIOSystem object.',
                },
                'update_fn': {
                    'type': 'string',
                    'description': 'The python definition of the update function of the NonlinearIOSystem object.',
                },
            },
            'required': ['name', 'update_fn'],
        },
    },
]


def define_system(**arguments):
    print('Attempting to define NonlinearIOSystem object...')
    print(arguments)
    return 'system created'


def dispatch_function(name, arguments):
    arguments = json.loads(arguments)
    match name:
        case 'consult_control_documentation':
            return consult_control_documentation(**arguments)
        case 'define_system':
            return define_system(**arguments)
        case _:
            raise ValueError(f'Function "{name}" not found.')


def handle_response(response, messages):
    if response and 'function_call' in response:
        call = response['function_call']
        result = dispatch_function(**call)
        messages.append({
            'role': 'function',
            'name': call['name'],
            'content': result,
        })
    else:
        print('> ', end='')
        messages.append({
            'role': 'user',
            'content': wrap_prompt_in_context(input()),
        })
    return messages


def prompt_step(functions=functions):
    global messages
    response = None
    if len(messages) > 1:
        response = llm(
            messages,
            functions=functions,
        ).json()['choices'][0]['message']
        messages.append(response)

    print_conversation(messages)
    messages = handle_response(response, messages)
    print_conversation(messages)
    return
