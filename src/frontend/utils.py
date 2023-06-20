from reactpy import component, html


@component
def Selector(options, selected, on_selection):
    button_width = f'{50 // len(options)}vw'
    return html.div(
        {'class': 'flex w-full place-items-center'},
        *[[html.button(
            {'on_click': lambda _: on_selection(_['currentTarget']['value']),
             'class': 'btn btn-sm',
             'style': dict(
                 background_color='gray' if option == selected else 'white',
                 width=button_width,
             ),
             'value': option},
            option,
        ), html.div({'style': dict(width='1vw')})] for option in options],
    )
