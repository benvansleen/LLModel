from reactpy import component, html, hooks


@component
def PlotDisplay():
    return html.div(
        html.h1("Plot Display"),
        html.p("This is a plot display"),
    )
