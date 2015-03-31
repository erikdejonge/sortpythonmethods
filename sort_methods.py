# coding=utf-8
"""
cryptoboxcli
-
Active8 (30-03-15)
author: erik@a8.nl
license: GNU-GPL2
"""
import ast
import inspect

fname = "__init__"
from __init__ import *


def remove_breaks(source):
    lastfind = -1
    while True:
        source = source.replace("\n\n\n\n", "\n\n\n")

        if source.count("\n\n\n\n") == 0:
            break

        lastfind = source.find("\n\n\n\n")
    return lastfind, source


def main():
    """
    main
    """
    tree = ast.parse(open("__init__.py").read(), '__init__.py', 'exec')
    names = set()
    prev = None

    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef):
            if prev is not None:
                if not isinstance(prev, ast.FunctionDef):
                    if not isinstance(prev, ast.ClassDef):
                        continue

            names.add(n.name)

        prev = n

    names = sorted(names)
    source = open("__init__.py").read()
    nw = open("newfile.py", "wt")
    codes = []

    for n in names:
        code = "".join(inspect.getsourcelines(globals()[n])[0])
        codes.append(code)
        source = source.replace(code, "")

    lastfind, source = remove_breaks(source)

    first = source[:lastfind]
    last = source[lastfind:]
    middle = ""
    for code in codes:
        middle += code
        middle += "\n\n\n"
    source = first + "\n\n\n" + middle + "\n\n" + last
    lastfind, source = remove_breaks(source)
    print(source)


if __name__ == "__main__":
    main()
