from reactpy import component, html, hooks


@component
def ModelDisplay():
    return html.div(
        html.h1("Model Display"),
        html.p("This is a model display"),
    )
