from reactpy import component, html, hooks
from .model import ModelDisplay
from .plot import PlotDisplay
from ..utils import Selector


@component
def Display():
    selected, set_selected = hooks.use_state('Model')

    return html.div(
        {'style': dict(height='50vh')},

        html.div({'style': dict(height='1vh')}),
        Selector(['Model', 'Plot'], selected, set_selected),
        {'Model': ModelDisplay, 'Plot': PlotDisplay}[selected](),
    )
