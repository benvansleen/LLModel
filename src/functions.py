import openai
from openai_function_call import openai_function
from pydantic import BaseModel, Field
from om import om
from documentation_agent import modelica_documentation_lookup
from openai_models import OpenAIMessage, OpenAIResponse
from chain import Chain


class ModelicaModel(BaseModel):
    '''
Modelica model definition. These models are used to simulate and plot real-life systems. Your model definition will be loaded into the OMEdit GUI, so make sure it includes annotations. PLEASE refer to the Modelica documentation (using the "modelica_documentation_lookup" tool) for more information or when otherwise uncertain.
    '''

    name: str = Field(
        description='Name of the model. Example: Vehicle',
    )

    definition: str = Field(
        description='''Complete Modelica model definition. DO NOT include any commentary. ALWAYS include "annotations" to ensure your model can be drawn in the OMEdit connection editor. Never use a "within" clause when defining a model.
Bad Example (NEVER do this):
within Modelica.Electrical.Analog.Examples.OpAmps;

Example:
model Vehicle
    parameter Real m = 1000 "Mass of the vehicle";
    parameter Real F = 3000 "Force applied to the vehicle";
    Real v(start = 0) "Velocity of the vehicle";
    Real a "Acceleration of the vehicle";
equation
    m * der(v) = F;
    a = der(v);
end Vehicle;'''
    )

#     parameters: list[str] = Field(
#         description='''The parameters of the model object. All named variables or parameters MUST be defined here. DO NOT include any semicolons (;) or docstring comments. This is where ALL components (resistors, capacitors, ...), variables, inputs, etc must be declared!
# Example: [parameter Modelica.Units.SI.Distance s = 100, parameter Modelica.Units.SI.Velocity v = 10, Real x(start = s, fixed = true)]''',
#     )

#     equations: list[str] = Field(
#         description='''The equations relating the parameters of the model object. This section defines an ordinary differential equation governing the behavior of the model. It MUST NOT contain any component (resistors, capacitors, etc), variable, or input declarations!
# Example: [der(x) = v, x = s + v * t] ''',
#     )


def dump_model(filename: str, model: str):
    with open(filename, 'w') as f:
        f.write(model)
    return


@openai_function
def define_model(model_spec: ModelicaModel) -> str:
    '''Define a Modelica model object'''
    from pyparsing.exceptions import ParseException
    try:
        model = model_spec.definition
        model = model.replace(';;', ';')
        model = '\n'.join([
            line for line in model.split('\n')
            if not line.startswith('within')
        ])

        print(model)
        output = om(model)
        print(output)

        if output.startswith('('):
            valid = om(f'instantiateModel({model_spec.name})')
            print(valid)
        if 'Error:' in valid:
            raise ParseException(valid)
        dump_model(f'../llm_{model_spec.name}.mo', model)

        return str(output)

    except ParseException as e:
        print('\nModel feedback > ', end='')
        user_feedback = input().strip()
        error_message = f'Parsing error: {str(e)}'
        if len(user_feedback) > 1:
            error_message += f'\nUser feedback: {user_feedback}'
        return error_message
#         return f'''
# Parsing error: {str(e)}
# User feedback (if any): {input().strip()}'''


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

schemas = [f.openai_schema for f in functions.values()]


def dispatch_function(
        response: OpenAIResponse,
) -> OpenAIMessage:
    name, response = response.prepare_for_function_call()
    result = functions[name].from_response(response)
    return OpenAIMessage(
        role='function',
        name=name,
        content=result,
    )


def llm(
        chain: Chain,
        model: str = 'gpt-3.5-turbo-0613',
        temperature: float = 0.0,
) -> OpenAIResponse:
    return OpenAIResponse(
        **openai.ChatCompletion.create(
            model=model,
            messages=chain.serialize(),
            functions=schemas,
            temperature=temperature,
        ).to_dict()
    )
