import openai
from openai_function_call import openai_function
from pydantic import BaseModel, Field
from om import om
from documentation_agent import modelica_documentation_lookup
from openai_models import OpenAIMessage, OpenAIResponse
from chain import Chain


class ModelicaModel(BaseModel):
    '''
    Modelica model definition. These models are used to simulate and plot real-life systems. Example:
    model Vehicle
        parameter Real m = 1000 "Mass of the vehicle";
        parameter Real F = 3000 "Force applied to the vehicle";
        Real v(start = 0) "Velocity of the vehicle";
        Real a "Acceleration of the vehicle";
    equation
        m * der(v) = F;
        a = der(v);
    end Vehicle;
    '''
    name: str = Field(
        description='Name of the model. Example: Vehicle',
    )

    parameters: list[str] = Field(
        description='''The parameters of the model object. All named variables or parameters MUST be defined here. DO NOT include any semicolons (;)
Example: [parameter Modelica.Units.SI.Distance s = 100, parameter Modelica.Units.SI.Velocity v = 10, Real x(start = s, fixed = true)]''',
    )

    equations: list[str] = Field(
        description='''The equations relating the parameters of the model object. This section defines an ordinary differential equation governing the behavior of the model. It MUST NOT contain any variable declarations. MAKE SURE ALL VARIABLES USED ARE IN SCOPE! DO NOT include any semicolons (;)
Example: [der(x) = v, x = s + v * t] ''',
    )


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
        model = model.replace(';;', ';')
        print(model)
        import pdb; pdb.set_trace()
        output = om(model)
        print(output)
        return str(output)
    except ParseException as e:
        print(e)
        return f'Parsing error! Invalid code! {e}'

# print(define_model.openai_schema)
# import sys; sys.exit()


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
    response = response.copy(deep=True)
    name = response.choices[0].message.function_call.name
    for choice in response.choices:
        choice.message.function_call = dict(
            choice.message.function_call,
        )
        choice.message = dict(choice.message)
    result = functions[name].from_response(response)
    return OpenAIMessage(**{
        'role': 'function',
        'name': name,
        'content': result,
    })


def llm(
        chain: Chain,
        model: str = 'gpt-3.5-turbo-0613',
) -> OpenAIResponse:
    return OpenAIResponse(
        **openai.ChatCompletion.create(
            model=model,
            messages=chain.serialize(),
            functions=schemas,
        ).to_dict()
    )
