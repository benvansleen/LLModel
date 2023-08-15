import os
import documentation_agent as docs
from openai_models import OpenAIMessage
from sys import argv
from termcolor import colored
from pydantic import BaseModel, Field
from om import om


class Chain(BaseModel):
    messages: list[OpenAIMessage] = Field(default=[])
    testbench: str | None = Field(default=None)

    @staticmethod
    def wrap_prompt_in_context(prompt):
        context = docs.modelica_documentation_lookup(prompt)
        return f'{context}\n\nGOAL: {prompt}'

    def __init__(self, system: str | None = None):
        super().__init__()
        self.messages = [OpenAIMessage(
            role='system',
            content=system or "You are an expert in the field of model-based design. Your goal is to help the user simulate a given experiment in the OpenModelica software package. You have access to the standard Modelica library and its associated documentation. Do NOT assume the existence of any other libraries or packages. PLEASE consult the library's documentation to ensure proper usage. Define only ONE model object at a time. Respond ONLY with code -- no commentary whatsoever. Please note that the 'Modelica.SIUnits' module has been moved to 'Modelica.Units.SI'."
        )]

        if len(argv) > 1:
            self.prepare_testbench(argv[1])

        return

    def prepare_testbench(self, testbench: str):
        with open(f'tests/{testbench}.mo', 'r') as f:
            lines = f.readlines()
            to_be_implemented = lines[0].strip()
            desired_behavior = lines[1].strip()
            final_command = lines[-1].strip()
            usage = ''.join(lines[2:-1])
        om(usage)
        self.testbench = final_command

        prompt = f'''
The user wants to run the following model with this desired behavior:
{desired_behavior}
DO NOT attempt to redefine it:
{usage}
{final_command}

Implement the following model:
{to_be_implemented}'''

        self.add(OpenAIMessage(
            role='user',
            content=self.wrap_prompt_in_context(prompt),
        ))
        return

    def add(self, message: OpenAIMessage | dict[str, str]):
        if not isinstance(message, OpenAIMessage):
            message = OpenAIMessage(**message)
        self.messages.append(message)
        return

    def serialize(self) -> list[dict[str, str]]:
        return [
            m.dict(exclude_unset=True)
            for m in self.messages
        ]

    def reload_context(self):
        self.messages = self.messages[:2] + self.messages[-2:]

        try:
            root = '../'
            model_file = [
                f for f in os.listdir(root)
                if f.startswith('llm_')
            ][0]
            with open(f'{root}{model_file}', 'r') as f:
                self.add(OpenAIMessage(
                    role='user',
                    content=f'Current model definition:\n{f.read()}',
                ))

        except FileNotFoundError as e:
            pass

        finally:
            return

    def __len__(self) -> int:
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
