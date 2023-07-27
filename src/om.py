import os
from OMPython import OMCSessionZMQ


omc = OMCSessionZMQ()
omc.sendExpression('loadModel(Modelica)')


def om(expr: str):
    cwd = os.getcwd()

    try:
        os.chdir('/tmp')
        result = omc.sendExpression(expr)
    finally:
        error = omc.sendExpression('getErrorString()')
        os.chdir(cwd)

    return f'{result}\n{error}'
