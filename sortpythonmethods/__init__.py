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
from argparse import ArgumentParser
from consoleprinter import running_in_debugger


def remove_breaks(source):
    """
    @type source: str
    @return: None
    """
    lastfind = -1
    cnt = 0
    source = "\n".join([x.rstrip() for x in source.split("\n")])
    while True:
        cnt += 1
        source = source.replace("\n\n\n\n", "\n\n\n")

        if source.count("\n\n\n\n") == 0:
            break

        lastfind = source.find("\n\n\n\n")

    while cnt < 20:
        source = source.replace("\n\n\n\n", "\n\n\n")
        cnt += 1

    return lastfind, source


def arg_parse():
    """
    arg_parse
    @return: @rtype:
    """

    parser = ArgumentParser()
    parser.add_argument("-m", dest="modulename", help="module name on which to sort globalmethods")
    parser.add_argument("-f", dest="filename", help="file name on which to sort globalmethods")
    parser.add_argument("-w", dest="write", help="write output to file", action="store_true")
    args = parser.parse_args()
    return parser, args.modulename, args.filename, args.write


def sortmethods(filename=None, module_name=None, writefile=False):
    """
    @type filename: str, None
    @type module_name: str, None
    @type writefile: bool
    @return: None
    """
    if filename is None and module_name is None:
        raise AssertionError("filename and module_name can't both be None")

    if filename is not None:
        filename = os.path.expanduser(filename)

        if not os.path.expanduser(filename):
            print("file does not exist:", filename)
            return

        if os.path.basename(filename) == "__init__.py":
            module_name = os.path.basename(os.path.dirname(filename))

        if module_name is None:
            module_name = os.path.basename(filename).split(".")[0]
        os.sys.path.append(os.path.dirname(filename))
        os.sys.path.append(os.path.dirname(os.path.dirname(filename)))

    # load module
    globals()[module_name] = __import__(module_name)

    # get filepath of module implementation
    fname = globals()[module_name].__file__

    # get all function names on global scope
    tree = ast.parse(open(fname).read(), os.path.basename(fname))
    names = set()
    prev = None
    classes = {}

    imports = []
    importfrom = {}
    moduledocstring = None
    cnt = 0

    for n in ast.walk(tree):
        # noinspection PyBroadException
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
                if "builtins" not in i.name:
                    imports.append(i.name)

        elif isinstance(n, ast.ImportFrom):
            if "builtins" not in n.module:
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
            print("#\n# not written, no module docstring\n#\n")
            print(open(fname).read())

        return

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

        importlist = importfrom[n]
        importlist.sort(key=lambda x: (x, len(x)))

        for m in importlist:
            code += m + ", "

        code = code.strip().strip(",")

        importsout.append((code, 1))

    sourcesplit = source.split("\n")
    source = [x for x in sourcesplit if not x.startswith("import ") and not x.startswith("from ")]
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

    for line in [x for x in source.split("\n") if len(x.strip()) > 0]:
        if "# noinspection" in line:
            source = source.replace(line, "")

    # replace code block in original file, and pasted sorted functions back in
    lastfind, source = remove_breaks(source)
    firstsource = source[:lastfind]
    last = source[lastfind:]
    middle = ""
    first = ""
    header = "#!/usr/bin/env python3\n# coding=utf-8\n"
    header += '"""'
    header += moduledocstring
    header += '"""'
    fromdetected = False

    for code in importsout:
        if code[0].startswith("from"):
            if not fromdetected:
                first += "\n"

            fromdetected = True

        if "future " in code[0] or "__future__" in code[0]:
            first = code[0] + "\n\n" + first
        else:
            first += code[0]
            first += "\n"

    first += firstsource.split(moduledocstring)[1].lstrip().lstrip('"""')
    for code in codes:
        codesplit = code[0].split("\n")

        if len(codesplit) > 0:
            cnt = 0

            for line in sourcesplit:
                if codesplit[0] in line:
                    if (cnt - 1) > 0:
                        if len(sourcesplit[cnt - 1]) > 0:
                            if sourcesplit[cnt - 1].strip().startswith("#"):
                                middle += sourcesplit[cnt - 1] + "\n"
                                break

                cnt += 1

        middle += code[0]
        middle += code[1] * "\n"

    source = header + "\n\n" + first.strip() + "\n\n\n" + middle + "\n\n" + last
    lastfind, source = remove_breaks(source)

    # write new source
    if writefile:
        nw = open(fname, "wt")
        nw.write(source)
        nw.close()
    else:
        if running_in_debugger(include_tests=True):
            print(source)
        else:

            # noinspection PyBroadException
            try:
                from pygments import highlight

                # noinspection PyUnresolvedReferences
                from pygments.lexers import PythonLexer

                # noinspection PyUnresolvedReferences
                from pygments.formatters import TerminalFormatter
                print(highlight(source, PythonLexer(), TerminalFormatter()))
            except:
                print(source)


def main():
    """
    main
    """
    parser, module_name, filename, writefile = arg_parse()

    if module_name is None and filename is None:
        print(parser.format_help())
        print("-f filename or -m modulename is required\n")
        return
    sortmethods(filename, module_name, writefile)


if __name__ == "__main__":
    main()
