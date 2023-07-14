from reactpy import run, html
from reactpy.backend.starlette import configure, Options
from starlette.applications import Starlette
from .frontend import App


app = Starlette()
configure(app, App, Options(head=html.head(
    html.title('LLModel'),
    html.link(dict(
        rel='stylesheet',
        href='https://cdn.jsdelivr.net/npm/daisyui@3.1.1/dist/full.css',
        type='text/css',
    )),
    html.script(dict(
        src='https://cdn.tailwindcss.com',
    )),
)))
