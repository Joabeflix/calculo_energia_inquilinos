from typing import Literal

tipo_retornos = Literal["A", "B", "C"]

def retorno(fun: tipo_retornos):
    return fun

def retorno2(fun: tipo_retornos):
    return fun


print(retorno("g"))