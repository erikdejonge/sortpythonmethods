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
from consoleprinter import running_in_debugger


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
    classes = {}

    imports = []
    importfrom = {}
    moduledocstring = None
    cnt = 0

    for n in ast.walk(tree):
        try:
            if moduledocstring is None and cnt < 5:
                moduledocstring = n.value.s
        except:
            pass

        cnt += 1

        if isinstance(n, ast.FunctionDef):
            if prev is not None:
                if not isinstance(prev, ast.FunctionDef):
                    if not isinstance(prev, ast.ClassDef):
                        continue

            names.add(n.name)
        elif isinstance(n, ast.ClassDef):
            classes[n.name] = []

            for i in ast.walk(n):
                if isinstance(i, ast.FunctionDef):

                    classes[n.name].append(i.name)

        elif isinstance(n, ast.Import):
            for i in n.names:
                imports.append(i.name)

        elif isinstance(n, ast.ImportFrom):
            if n.module not in importfrom:
                importfrom[n.module] = []
            importfrom[n.module].append(n.names)
        else:
            pass

        prev = n

    for k in importfrom:
        nl = []
        for l in importfrom[k]:
            for i in l:
                nl.append(i.name)
        importfrom[k] = nl

    if moduledocstring is None:
        if writefile:
            print("not written, no module docstring")
        else:
            print(open(fname).read())

    # sort names and request source code from module
    names = sorted(names)
    source = open(fname).read()
    codes = []

    importsout = []
    imports.sort(key=lambda x: (x.count("."), x, len(x)))

    for n in imports:
        code = "import " + n

        importsout.append((code, 1))
    importfromlist = list(importfrom.keys())
    importfromlist.sort(key=lambda x: (x.count("."), len(x), x))

    for n in importfromlist:
        code = "from " + n + " import "
        numspaces = len(code)

        importlist = importfrom[n]
        importlist.sort(key=lambda x: (x, len(x)))
        first = True

        for m in importlist:
            if not first:
                code += (numspaces - 1) * " "

            code += m + ", \\\n "
            first = False

        code = code.strip().strip(", \\")

        importsout.append((code, 1))

    source = source.split("\n")
    source = [x for x in source if not x.startswith("import ") and not x.startswith("from ")]
    source = "\n".join(source)
    classnames = sorted(classes.keys())

    for k in classnames:
        code = "".join(inspect.getsourcelines(getattr(globals()[module_name], k))[0])
        codes.append((code, 3))
        source = source.replace(code, "")

    for n in names:
        code = "".join(inspect.getsourcelines(getattr(globals()[module_name], n))[0])
        codes.append((code, 3))
        source = source.replace(code, "")

    # replace code block in original file, and pasted sorted functions back in
    lastfind, source = remove_breaks(source)
    firstsource = source[:lastfind]
    last = source[lastfind:]
    middle = ""
    first = "#!/usr/bin/env python3\n# coding=utf-8\n"
    first += '"""'
    first += moduledocstring
    first += '"""\n\n'
    fromdetected = False

    for code in importsout:
        if code[0].startswith("from"):
            if not fromdetected:
                first += "\n"

            fromdetected = True

        first += code[0]
        first += code[1] * "\n"

    first += firstsource.split(moduledocstring)[1].lstrip().lstrip('"""')

    
    for code in codes:
        middle += code[0]
        middle += code[1] * "\n"

    source = first + "\n\n\n" + middle + "\n\n" + last
    lastfind, source = remove_breaks(source)

    # write new source
    if writefile:
        nw = open(fname + ".sorted", "wt")
        nw.write(source)
        nw.close()
    else:
        if running_in_debugger(include_tests=True):
            print(source)
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
