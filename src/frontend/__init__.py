from reactpy import component, html
from .display import Display
from .input import Input


@component
def App():
    return html.div(
        {'class': 'flex flex-col w-full border-opacity-50 place-items-center',},

        Display(),
        Input(),
    )
