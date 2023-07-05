from openai_function_call import openai_function
from pydantic import BaseModel
from om import om
from documentation_agent import modelica_documentation_lookup


# functions = [
#     {
#         'name': 'modelica_documentation_lookup',
#         'description': 'Consult the documentation for the Modelica Standard Library. Use keywords (like specific function or object names) to find examples and best practices.',
#         'parameters': {
#             'type': 'object',
#             'properties': {
#                 'search_query': {
#                     'type': 'string',
#                     'description': 'The search query to use when searching the documentation.',
#                 },
#             },
#             'required': ['search_query'],
#         },
#     },

#     {
#         'name': 'define_model',
#         'description': 'Define a Modelica model object',
#         'parameters': {
#             'type': 'object',
#             'properties': {
#                 'name': {
#                     'type': 'string',
#                     'description': 'The name of the NonlinearIOSystem object.',
#                 },
#                 'parameters': {
#                     'type': 'string',
#                     'description': 'The parameters of the model object. All named variables or parameters MUST be defined here. Example:\nparameter Modelica.Units.SI.Distance s = 100;\nparameter Modelica.Units.SI.Velocity v = 10;\nReal x(start = s, fixed = true);',
#                 },
#                 'equation': {
#                     'type': 'string',
#                     'description': 'The equation of the model object. MUST NOT contain any variable declarations. Example:\nder(x) = v;\nx = s + v * t;',
#                 },
#             },
#             'required': ['name', 'parameters', 'equation'],
#         },
#     },

#     {
#         'name': 'simulate',
#         'description': 'Run a simulation on a given model object',
#         'parameters': {
#             'type': 'object',
#             'properties': {
#                 'modelName': {
#                     'type': 'string',
#                     'description': 'The name of the model object to simulate.',
#                 },
#                 'stopTime': {
#                     'type': 'number',
#                     'description': 'The time at which to stop the simulation.',
#                 },
#             },
#             'required': ['modelName', 'stopTime'],
#         },
#     },

#     {
#         'name': 'plot',
#         'description': 'Plot the results of a simulation',
#         'parameters': {
#             'type': 'object',
#             'properties': {
#                 'variable_list': {
#                     'type': 'string',
#                     'description': 'A comma-separated string representing the list of variables to plot. Example:\nx,der(x),v',
#                 },
#             },
#             'required': ['variable_list'],
#                 #     'type': 'array',
#                 #     'description': 'The list of variables to plot. Example:\n{ x, der(x) }',
#                 #     'items': {
#                 #         'type': 'string',
#                 #     },
#                 # },
#         },
#     },
# ]


class ModelicaModel(BaseModel):
    '''
    parameters: The parameters of the model object. All named variables or parameters MUST be defined here.
    Example:
    [parameter Modelica.Units.SI.Distance s = 100, parameter Modelica.Units.SI.Velocity v = 10, Real x(start = s, fixed = true)]

    equation: The equations relating the parameters of the model object. This section defines an ordinary differential equation governing the behavior of the model. It MUST NOT contain any variable declarations. MAKE SURE ALL VARIABLES USED ARE IN SCOPE!
    Example:
    [der(x) = v, x = s + v * t]
    '''
    name: str
    parameters: list[str]
    equations: list[str]


@openai_function
def define_model(model_spec: ModelicaModel) -> str:
    '''Define a Modelica model object'''
    from pyparsing.exceptions import ParseException
    try:
        parameters = ';\n'.join(model_spec.parameters)
        equations = ';\n'.join(model_spec.equations)
        model = f'''
        model {model_spec.name}
        {parameters};
        equation
        {equations};
        end {model_spec.name};
        '''
        print(model)
        output = om(model)
        print(output)
        return str(output)
    except ParseException as e:
        print(e)
        return str(e)


@openai_function
def simulate(model_name: str, stopTime: float) -> str:
    '''
    Run a simulation on a given model object

    model_name: Name of the model object to simulate
    stopTime: Time (s) at which to stop the simulation
    '''
    print(om(f'list({model_name})'))
    output = om(f'simulate({model_name}, stopTime={stopTime})')
    print(output)
    return str(output)


@openai_function
def plot(variable_list: str) -> str:
    '''
    Plot the results of a Modelica simulation.

    variable_list: A comma-separated string representing the list of variables to plot. Example: x,der(x),v
    '''
    output = om('plot({' + variable_list + '})')
    print(output)
    return str(output)


@openai_function
def modelica_documentation(search_query: str) -> str:
    '''
    Consult the documentation for the Modelica Standard Library. Use keywords (like specific function or object names) to find examples and best practices.
    '''
    return modelica_documentation_lookup(search_query)



functions = {
    'define_model': define_model,
    'simulate': simulate,
    'plot': plot,
    'modelica_documentation': modelica_documentation,
}

function_schemas = [f.openai_schema for f in functions.values()]


def dispatch_function(response) -> dict[str, str]:
    try:
        name = response.choices[0].message.function_call.name
        result = functions[name].from_response(response)
        # match name:
        #     case 'modelica_documentation':
        #         return modelica_documentation.from_response(response)
        #     case 'define_model':
        #         result = define_model.from_response(response)
        #     case 'simulate':
        #         result = simulate.from_response(response)
        #     case 'plot':
        #         result = plot.from_response(response)
        #     case _:
        #         raise ValueError(f'Function "{response}" not found.')
        return {
            'role': 'function',
            'name': name,
            'content': result,
        }
    except:
        import pdb; pdb.set_trace()
