from dotenv import load_dotenv
load_dotenv()
import openai
from sys import argv
from om import om
from documentation_agent import consult_modelica_documentation
from functions import dispatch_function, function_schemas
from utils import print_conversation



print(om('getVersion()'))

messages = [{
    'role': 'system',
    'content': "You are an expert in the field of model-based design. Your goal is to help the user simulate a given experiment in the OpenModelica software package. You have access to the standard Modelica library and its associated documentation. Do NOT assume the existence of any other libraries or packages. PLEASE consult the library's documentation to ensure proper usage. Define only ONE model object at a time. Respond ONLY with code -- no commentary whatsoever. Please note that the 'Modelica.SIUnits' module has been moved to 'Modelica.Units.SI'.",
}]


def wrap_prompt_in_context(prompt):
    context = consult_modelica_documentation(prompt)
    return f'{context}\n\nGOAL: {prompt}'


if len(argv) > 1:
    messages.append({
        'role': 'user',
        'content': wrap_prompt_in_context(' '.join(argv[1:])),
    })


def prompt_user():
    print('> ', end='')
    return {
        'role': 'user',
        'content': input(),
        # 'content': wrap_prompt_in_context(input()),
    }


def handle_response(response, messages):
    first_choice = response['choices'][0]
    finish_reason = first_choice.get('finish_reason')
    messages.append(first_choice.get('message'))

    match finish_reason:
        case 'function_call':
            result = dispatch_function(response)
        case _:
            result = prompt_user()

    messages.append(result)
    return messages


def prompt_step(messages=messages):
    if len(messages) == 1:
        messages.append(prompt_user())

    response = openai.ChatCompletion.create(
        # model='gpt-3.5-turbo-0613',
        model='gpt-4-0613',
        messages=messages,
        functions=function_schemas,
    )
    print_conversation(messages, clear=True)
    messages = handle_response(response, messages)
    print_conversation(messages, clear=True)
    return


while True:
    try:
        prompt_step()
    except KeyboardInterrupt:
        # import pdb; pdb.set_trace()
        import sys; sys.exit()
