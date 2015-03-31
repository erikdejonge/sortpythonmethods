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
from argparse import ArgumentParser


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


def arg_parse():
    """
    arg_parse
    @return: @rtype:
    """
    parser = ArgumentParser()
    parser.add_argument("-m", dest="modulename", help="module name on which to sort globalmethods", required=True)
    parser.add_argument("-w", dest="write", help="write output to file", action="store_true")
    args = parser.parse_args()
    return args.modulename, args.write


def main():
    """
    main
    """
    module_name, writefile = arg_parse()

    # load module
    globals()[module_name] = __import__(module_name)

    # get filepath of module implementation
    fname = globals()[module_name].__file__

    # get all function names on global scope
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

    # sort names and request source code from module
    names = sorted(names)
    source = open(fname).read()
    codes = []

    for n in names:
        code = "".join(inspect.getsourcelines(getattr(globals()[module_name], n))[0])
        codes.append(code)
        source = source.replace(code, "")

    # replace code block in original file, and pasted sorted functions back in
    lastfind, source = remove_breaks(source)
    first = source[:lastfind]
    last = source[lastfind:]
    middle = ""

    for code in codes:
        middle += code
        middle += "\n\n\n"

    source = first + "\n\n\n" + middle + "\n\n" + last
    lastfind, source = remove_breaks(source)

    # write new source
    if writefile:
        nw = open(fname + ".sorted", "wt")
        nw.write(source)
        nw.close()
    else:
        # try printing to terminal with syntax coloring
        try:
            from pygments import highlight
            from pygments.lexers import PythonLexer
            from pygments.formatters import TerminalFormatter
            print(highlight(source, PythonLexer(), TerminalFormatter()))
        except:
            print(source)


if __name__ == "__main__":
    main()
