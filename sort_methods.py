# coding=utf-8
"""
cryptoboxcli
-
Active8 (30-03-15)
author: erik@a8.nl
license: GNU-GPL2
"""
import os
import ast
import inspect
import imp


def remove_breaks(source):
    """
    @type source: str
    @return: None
    """
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
    fname = os.path.expanduser("~") + "/workspace/pip/k8svag/k8svag/__init__.py"
    module_name = "k8svag"

    globals()[module_name] = __import__(module_name)
    print(globals().keys())

    imp.load_module(fname, os.path.basename(fname), os.path.dirname(fname))
    tree = ast.parse(open(fname).read(), os.path.basename(fname), 'exec')
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
