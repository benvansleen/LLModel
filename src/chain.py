import os
import documentation_agent as docs
from openai_models import OpenAIMessage
from sys import argv
from termcolor import colored
from pydantic import BaseModel, Field


class Chain(BaseModel):
    messages: list[OpenAIMessage] = Field(default=[])

    @staticmethod
    def wrap_prompt_in_context(prompt):
        # context = consult_modelica_documentation(prompt)
        context = docs.modelica_documentation_lookup(prompt)
        return f'{context}\n\nGOAL: {prompt}'

    def __init__(self, system=None):
        super().__init__()
        self.messages = [OpenAIMessage(
            role='system',
            content=system or "You are an expert in the field of model-based design. Your goal is to help the user simulate a given experiment in the OpenModelica software package. You have access to the standard Modelica library and its associated documentation. Do NOT assume the existence of any other libraries or packages. PLEASE consult the library's documentation to ensure proper usage. Define only ONE model object at a time. Respond ONLY with code -- no commentary whatsoever. Please note that the 'Modelica.SIUnits' module has been moved to 'Modelica.Units.SI'."
        )]

        if len(argv) > 1:
            self.messages.append(OpenAIMessage(
                role='user',
                content=self.wrap_prompt_in_context(
                    ' '.join(argv[1:])
                ),
            ))
        return

    def add(self, message):
        if not isinstance(message, OpenAIMessage):
            message = OpenAIMessage(**message)
        self.messages.append(message)
        return

    def serialize(self):
        return [
            m.dict(exclude_unset=True)
            for m in self.messages
        ]

    def __len__(self):
        return len(self.messages)

    def print(self, clear=True):
        if clear:
            os.system('clear')

        role_to_color = {
            'system': 'red',
            'user': 'green',
            'assistant': 'blue',
            'function_call': 'yellow',
            'function': 'magenta',
        }

        def format_message(message):

            match message.role:
                case 'system':
                    return (
                        f'system: {message.content}',
                        role_to_color['system'],
                    )

                case 'user':
                    return (
                        f'user: {message.content}',
                        role_to_color['user'],
                    )

                case 'assistant':
                    if message.function_call:
                        message = message.function_call
                        return (
                            f'assistant ({message.name}): {message.arguments}',
                            role_to_color['function_call'],
                        )
                    else:
                        return (
                            f'assistant: {message.content}',
                            role_to_color['assistant'],
                        )

                case 'function':
                    return (
                        f'function ({message.name}): {message.content}',
                        role_to_color['function'],
                    )

                case _:
                    raise ValueError(f'Unknown role: {message.role}')

        for message in self.messages:
            print(colored(*format_message(message)))

        return
