import sys

import pyaml
from pydantic import BaseModel
import yaml


def deep_format(a: dict, mapping: dict[str, str]) -> dict:
    def aux(x):
        if isinstance(x, str):
            return x.format_map(mapping)
        elif isinstance(x, dict):
            return format_dict(x)
        elif isinstance(x, list):
            return format_list(x)
        else:
            return x

    def format_list(x: list) -> list:
        return [aux(v) for v in x]

    def format_dict(x: dict) -> dict:
        return {k: aux(v) for k, v in x.items()}

    return format_dict(a)


def deep_get(a: dict, keys: list[str], default=None):
    if keys[0] in a:
        if len(keys) > 1:
            return deep_get(a[keys[0]], keys[1:], default)
        else:
            return a[keys[0]]
    else:
        return default


def deep_merge(a: dict, b: dict, merge_list=None) -> dict:
    c = dict(a)
    for k, v in b.items():
        if k in c:
            if all(isinstance(x, dict) for x in [c[k], v]):
                c[k] = deep_merge(c[k], v, merge_list)
            elif all(isinstance(x, list) for x in [c[k], v]) and merge_list:
                c[k] = merge_list(c[k], v)
            else:
                c[k] = v
        else:
            c[k] = v
    return c


def get_by_name(a: list, name: str):
    for v in a:
        if isinstance(v, dict) and v["name"] == name:
            return v
        elif isinstance(v, BaseModel) and v.name == name:
            return v
    raise ValueError(f"could not get item (name={name})")


def get_index_by_name(a: list, name: str) -> int:
    for i, v in enumerate(a):
        if isinstance(v, dict) and v["name"] == name:
            return i
        elif isinstance(v, BaseModel) and v.name == name:
            return i
    return -1


def strategic_merge(a: dict, b: dict) -> dict:
    def merge_list(a: list, b: list) -> list:
        if not all(all("name" in y for y in x) for x in [a, b]):
            return b
        c = list(a)
        for x in b:
            i = get_index_by_name(c, x["name"])
            if i >= 0:
                c[i] = deep_merge(c[i], x, merge_list)
            else:
                c.append(x)
        return c

    return deep_merge(a, b, merge_list)


def yaml_dump(a) -> str:
    return pyaml.dump(a, width=sys.maxsize).rstrip()


def yaml_load(a: str):
    return yaml.safe_load(a)
