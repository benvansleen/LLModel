import os
from OMPython import OMCSessionZMQ


omc = OMCSessionZMQ()
omc.sendExpression('loadModel(Modelica)')


def om(expr: str):
    cwd = os.getcwd()
    os.chdir('/tmp')

    result = omc.sendExpression(expr)
    error = omc.sendExpression('getErrorString()')
    if error != '""\n':
        print(error)

    os.chdir(cwd)
    return f'{result}\n{error}'
