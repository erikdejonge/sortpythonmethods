#!/usr/bin/env python3
# coding=utf-8
"""
cryptoboxcli
-
Active8 (30-03-15)
author: erik@a8.nl
license: GNU-GPL2
"""
import ast
import collections
import inspect
import os
import sys
from argparse import ArgumentParser
from pygments import highlight
from consoleprinter import console

# noinspection PyUnresolvedReferences
from pygments.lexers import PythonLexer

# noinspection PyUnresolvedReferences
from pygments.formatters import TerminalFormatter


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


def get_source_lines(codes, object_name, module_name, source):
    """
    @type codes: list
    @type object_name: str
    @type module_name: str
    @type source: str
    @return: tuple
    """
    try:
        code = "".join(inspect.getsourcelines(getattr(globals()[module_name], object_name))[0])
        codes.append((code, 3))
        source = source.replace(code, "")
        return source, codes
    except BaseException as be:
        console("==========")
        console(module_name, object_name)
        console("--")
        console(be)
        console("==========")
        raise


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
        filename = os.path.abspath(filename)

        if not os.path.expanduser(filename):
            console("file does not exist:", filename)
            return

        if os.path.basename(filename) == "__init__.py":
            module_name = os.path.basename(os.path.dirname(filename))

        if module_name is None:
            module_name = os.path.basename(filename).split(".")[0]
        os.sys.path.append(os.path.dirname(filename))
        os.sys.path.append(os.path.dirname(os.path.dirname(filename)))

    # load module
    try:
        globals()[module_name] = __import__(module_name)
    except ImportError as ie:
        if writefile:
            console("not written, import error", ie)
        else:
            console("#\n# not written, importerror " + str(ie) + "\n#\n")

            if filename is not None:
                console(open(filename).read())

        return

    # get filepath of module implementation
    fname = globals()[module_name].__file__

    if not os.path.isdir(os.path.dirname(fname)):
        if filename is None:
            raise AssertionError("not a dir")
        else:
            fname = filename

    # get all function methodnames on global scope
    tree = ast.parse(open(fname).read(), os.path.basename(fname))
    methodnames = []
    nestedmethodnames = []
    classes = {}
    linestobottom = set()

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
            methodnames.append((n.name, id(n)))

            for c in ast.walk(n):
                if isinstance(c, ast.FunctionDef):
                    if n.name != c.name:
                        nestedmethodnames.append((c.name, id(c)))

        elif isinstance(n, ast.ClassDef):
            classes[n.name] = []

            for i in n.bases:
                if i.id != "object":
                    classes[n.name].append(i.id)

            for c in ast.walk(n):
                if isinstance(c, ast.FunctionDef):
                    nestedmethodnames.append((c.name, id(c)))

        elif isinstance(n, ast.Import):
            for i in n.names:
                if "builtins" not in i.name:
                    imports.append(i.name)

        elif isinstance(n, ast.ImportFrom):
            if "builtins" not in n.module:
                if n.module not in importfrom:
                    importfrom[n.module] = []
                importfrom[n.module].append(n.names)

        elif isinstance(n, ast.Module):
            start_lineno_global = None

            for g in n.body:
                if start_lineno_global is not None:
                    # noinspection PyUnresolvedReferences
                    linestobottom.add((start_lineno_global.lineno, g.lineno))
                    start_lineno_global = None

                if isinstance(g, ast.Assign):
                    start_lineno_global = g
                elif isinstance(g, ast.Expr):
                    start_lineno_global = g

    nestedmethodnames2 = [x[0] for x in nestedmethodnames]
    nestedmethodnames2id = [x[1] for x in nestedmethodnames]
    methodnames2 = set()

    for n in methodnames:
        add = True

        if n[0] in nestedmethodnames2:
            if n[1] in nestedmethodnames2id:
                add = False

        if add is True:
            methodnames2.add(n[0])

    methodnames = methodnames2

    for k in importfrom:
        nl = []
        for l in importfrom[k]:
            for i in l:
                nl.append(i.name)
        importfrom[k] = nl

    if moduledocstring is None:
        if writefile:
            console("not written, no module docstring")
        else:
            console("#\n# not written, no module docstring\n#\n")
            console(open(fname).read())

        return

    # sort methodnames and request source code from module
    methodnames = sorted(methodnames)
    source = open(fname).read()
    sourcesplit = source.split("\n")
    linestobottom = list(linestobottom)
    linestobottom.sort(key=lambda x: x[0])
    global_lines = []

    for ln in linestobottom:
        cnt = ln[0] - 1
        cont = []
        while cnt < ln[1] - 1:
            cont.append(sourcesplit[cnt])
            cnt += 1
        global_lines.append("\n".join(cont))

    codes = []

    importsout = []
    imports = list(set(imports))
    imports.sort(key=lambda x: (x.count("."), x, len(x)))

    for n in imports:
        code = "import " + n

        importsout.append((code, 1))
    importfromlist = list(set(list(importfrom.keys())))
    importfromlist.sort(key=lambda x: (x.count("."), len(x), x))

    for n in importfromlist:
        code = "from " + n + " import "

        importlist = importfrom[n]
        importlist = list(set(importlist))
        importlist.sort(key=lambda x: (x, len(x)))

        for m in importlist:
            code += m + ", "

        code = code.strip().strip(",")

        importsout.append((code, 1))

    sourcesplit = source.split("\n")
    source = [x for x in sourcesplit if not x.startswith("import ") and not x.startswith("from ")]
    source = "\n".join(source)
    classnames = sorted(classes.keys())

    import collections
    bsort = False
    cnt = 0

    while not bsort:
        cnt += 1

        if cnt > 100:
            raise AssertionError("infinite loop")

        baseclass_seen = []
        baseclass_missing = []
        classnamesbase = collections.deque()

        for k in classnames:
            if k in classes:
                baseclass_seen.append(k)
                for k2 in classes[k]:
                    if k2 not in baseclass_seen:
                        if k2 in classes:
                            baseclass_missing.append(k2)

        if len(baseclass_missing) == 0:
            bsort = True
        else:
            for k in baseclass_missing:
                if k not in classnamesbase:
                    classnamesbase.appendleft(k)

            for k in baseclass_seen:
                if k not in classnamesbase:
                    classnamesbase.append(k)

            classnames = list(classnamesbase)

    for k in classnames:
        source, codes = get_source_lines(codes, k, module_name, source)

    for n in methodnames:
        source, codes = get_source_lines(codes, n, module_name, source)

    for n in global_lines:
        source = source.replace(n, "")

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

    fss = firstsource.split(moduledocstring)

    if len(fss) > 1:
        fssc = fss[1].lstrip().lstrip('"""')
        first += fssc

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
    global_lines.sort()

    for line in global_lines:
        middle += line
        middle += "\n"

    source = header + "\n\n" + first.strip() + "\n\n\n" + middle + "\n\n" + last
    lastfind, source = remove_breaks(source)

    # write new source
    if writefile:
        nw = open(fname, "wt")
        nw.write(source)
        nw.close()
        console("sortpythonmethods done.")
    else:
        if not sys.stdout.isatty():
            console(source)
        else:

            # noinspection PyBroadException
            try:
                console(highlight(source, PythonLexer(), TerminalFormatter()))
            except:
                console(source, plaintext=True)


def main():
    """
    main
    """
    parser, module_name, filename, writefile = arg_parse()

    if module_name is None and filename is None:
        console(parser.format_help())
        console("-f filename or -m modulename is required\n")
        return
    sortmethods(filename, module_name, writefile)


if __name__ == "__main__":
    main()
