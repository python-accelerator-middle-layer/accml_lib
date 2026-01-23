from typing import Any, Dict, Union


def deserialse_value(value: Dict[str, Union[str, int, float]]):
    d = dict(int=int, float=float)
    ins = d[value["type"]]
    r = ins(value["value"])
    return r


def serialize_value(value) -> dict[str, Any]:
    if isinstance(value, int):
        return dict(type="int", value=value)
    elif isinstance(value, float):
        return dict(type="float", value=value)
    else:
        raise AssertionError(
            f"Don't know how to seralize {value} of type {type(value)}"
        )
