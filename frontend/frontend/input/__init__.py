from reactpy import component, html, hooks
from ..utils import Selector


@component
def Input():
    selected, set_selected = hooks.use_state('Systems')
    prompt, set_prompt = hooks.use_state('')

    def submit(prompt):
        print(prompt)

    def handle_keydown(key):
        if key == 'Enter':
            set_prompt(prompt.strip())
            submit(prompt)
        return

    return html.div(
        {'class': 'flex flex-col place-items-center'},

        Selector(
            ['Systems', 'Connections', 'Plots'],
            selected, set_selected,
        ),
        html.div({'style': dict(height='1vh')}),
        html.textarea(
            {'class': 'textarea textarea-bordered textarea-lg w-full max-w-xs',
             'style': dict(width='100vw'),
             'placeholder': 'Prompt LLModel...',
             'on_change': lambda e: set_prompt(e['currentTarget']['value']),
             'on_keydown': lambda e: handle_keydown(e['currentTarget']['value'])},
        ),
        html.div({'style': dict(height='1vh')}),
        html.button(
            {'class': 'btn btn-primary btn-sm w-full max-w-xs',
             'style': dict(width='100vw'),
             'on_click': lambda _: submit(prompt)},
            'Generate',
        ),
    )
