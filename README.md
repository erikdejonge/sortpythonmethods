# sortpythonmethods
Rearrange methods alphabetically in a Python source file.
- Python3


## sortorder
1. docstring
2. future imports
3. imports first on alphabet then on length (apo, alpha-pipe-organ)
4. from, modules on apo, imports on alpa
5. classes sorted on classname alpha (internals of class unchanged)
6. methods sorted on methodname alpha


## example

Source file before sort
```python
"""
Docstring is required
"""
import sys
import httplib
import email
import concurrent.futures
import os

class Zorro(object):
    pass

def foobar():
    pass
    
def helloworld():
    pass
    
def applemethod():
    pass
   
class Alpha(object):
    pass
```

Run command
```bash
sortpythonmethods -f myfile.py
```


Sorted source file
```python
#!/usr/bin/env python3
# coding=utf-8
"""
Docstring is required
"""

import email
import http
import os
import sys
import concurrent.futures


class Alpha(object):
    pass


class Zorro(object):
    pass


def applemethod():
    pass


def foobar():
    pass


def helloworld():
    pass

```