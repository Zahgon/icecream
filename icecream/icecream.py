#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# IceCream - Never use print() to debug again
#
# Ansgar Grunseid
# grunseid.com
# grunseid@gmail.com
#
# License: MIT
#

import ast
import enum
import inspect
import pprint
import sys
from types import FrameType
from typing import (
    Optional,
    cast,
    Any,
    Callable,
    Generator,
    List,
    Sequence,
    Tuple,
    Type,
    Union,
    Literal,
)
import warnings
from datetime import datetime
import functools
from contextlib import contextmanager
from os.path import basename, realpath
from textwrap import dedent

import colorama  # type: ignore
import executing  # type: ignore
from pygments import highlight  # type: ignore

# See https://gist.github.com/XVilka/8346728 for color support in various
# terminals and thus whether to use Terminal256Formatter or
# TerminalTrueColorFormatter.
from pygments.formatters import Terminal256Formatter  # type: ignore
from pygments.lexers import Python3Lexer as Py3Lexer  # type: ignore

from .coloring import SolarizedDark


class Sentinel(enum.Enum):
    absent = object()


def bindStaticVariable(name: str, value: Any) -> Callable:
    return decorator


def has_non_ascii_chars(s: str) -> bool:
    """Check if string contains non-ASCII characters."""
    return any(ord(char) > 127 for char in s)






def stderr_print(*args: object) -> None:
    print(*args, file=sys.stderr)










def safe_pformat(obj: object, *args: Any, **kwargs: Any) -> str:
    """pprint.pformat() with a couple of small safety/usability tweaks.

    In addition to the usual TypeError handling below, we special–case
    "medium sized" flat lists. For those, the standard pprint heuristics
    sometimes choose a one-item-per-line layout which makes the order of
    values hard to visually follow in ic()'s output. For such lists we
    prefer the more compact repr()-style representation.
    """
    pass


DEFAULT_PREFIX = 'ic| '
DEFAULT_LINE_WRAP_WIDTH = 70  # Characters.
DEFAULT_CONTEXT_DELIMITER = '- '
DEFAULT_OUTPUT_FUNCTION = colorizedStderrPrint
DEFAULT_ARG_TO_STRING_FUNCTION = safe_pformat

"""
This info message is printed instead of the arguments when icecream
fails to find or access source code that's required to parse and analyze.
This can happen, for example, when

  - ic() is invoked inside a REPL or interactive shell, e.g. from the
    command line (CLI) or with python -i.

  - The source code is mangled and/or packaged, e.g. with a project
    freezer like PyInstaller.

  - The underlying source code changed during execution. See
    https://stackoverflow.com/a/33175832.
"""
NO_SOURCE_AVAILABLE_WARNING_MESSAGE = (
    'Failed to access the underlying source code for analysis. Was ic() '
    'invoked in a REPL (e.g. from the command line), a frozen application '
    '(e.g. packaged with PyInstaller), or did the underlying source code '
    'change during execution?')




class Source(executing.Source):








class _SingleDispatchCallable:
    def __call__(self, *_: object) -> str:
        # This is a marker class, not a real thing you should use
        raise NotImplementedError("This is a marker class, not a real thing you should use")

    register: Callable[[Type], Callable]




@singledispatch
def argumentToString(obj: object) -> str:
    s = DEFAULT_ARG_TO_STRING_FUNCTION(obj)
    s = s.replace('\\n', '\n')  # Preserve string newlines in output.
    return s




class IceCreamDebugger:
    _pairDelimiter = ', '  # Used by the tests in tests/.
    lineWrapWidth = DEFAULT_LINE_WRAP_WIDTH
    contextDelimiter = DEFAULT_CONTEXT_DELIMITER
    outputFunction: Callable[..., None]

    def __init__(self, prefix: Union[str, Callable[[], str]] =DEFAULT_PREFIX,
                 outputFunction: Callable[..., None]=DEFAULT_OUTPUT_FUNCTION,
                 argToStringFunction: Union[_SingleDispatchCallable, Callable[[Any], str]]=argumentToString, includeContext: bool=False,
                 contextAbsPath: bool=False,
                 noColor: bool=False):
        self.enabled = True
        self.prefix = prefix
        self.includeContext = includeContext
        self.argToStringFunction = argToStringFunction
        self.contextAbsPath = contextAbsPath
        self.noColor = noColor

        if self.noColor and outputFunction is DEFAULT_OUTPUT_FUNCTION:
            self.outputFunction = stderr_print
        else:
            self.outputFunction = outputFunction

    def __call__(self, *args: object) -> object:
        if self.enabled:
            currentFrame = inspect.currentframe()
            assert currentFrame is not None and currentFrame.f_back is not None
            callFrame = currentFrame.f_back
            self.outputFunction(self._format(callFrame, *args))

        if not args:  # E.g. ic().
            passthrough = None
        elif len(args) == 1:  # E.g. ic(1).
            passthrough = args[0]
        else:  # E.g. ic(1, 2, 3).
            passthrough = args

        return passthrough












    def configureOutput(
        self: "IceCreamDebugger",
        prefix: Union[str, Literal[Sentinel.absent]] = Sentinel.absent,
        outputFunction: Union[Callable, Literal[Sentinel.absent]] = Sentinel.absent,
        argToStringFunction: Union[Callable, Literal[Sentinel.absent]] = Sentinel.absent,
        includeContext: Union[bool, Literal[Sentinel.absent]] = Sentinel.absent,
        contextAbsPath: Union[bool, Literal[Sentinel.absent]] = Sentinel.absent,
        lineWrapWidth: Union[bool, Literal[Sentinel.absent]] = Sentinel.absent,
        noColor: Union[bool, Literal[Sentinel.absent]] = Sentinel.absent,
    ) -> None:
        noParameterProvided = all(
            v is Sentinel.absent for k, v in locals().items() if k != 'self')
        if noParameterProvided:
            raise TypeError('configureOutput() missing at least one argument')

        if noColor is not Sentinel.absent:
            self.noColor = noColor
            # Auto-swap built-in output functions when no explicit
            # outputFunction is provided alongside noColor.
            if outputFunction is Sentinel.absent:
                if self.noColor:
                    if self.outputFunction is colorizedStderrPrint:
                        self.outputFunction = stderr_print
                    elif self.outputFunction is colorizedStdoutPrint:
                        self.outputFunction = stdout_print
                else:
                    if self.outputFunction is stderr_print:
                        self.outputFunction = colorizedStderrPrint
                    elif self.outputFunction is stdout_print:
                        self.outputFunction = colorizedStdoutPrint

        if prefix is not Sentinel.absent:
            self.prefix = prefix

        if outputFunction is not Sentinel.absent:
            self.outputFunction = outputFunction

        if argToStringFunction is not Sentinel.absent:
            self.argToStringFunction = argToStringFunction

        if includeContext is not Sentinel.absent:
            self.includeContext = includeContext

        if contextAbsPath is not Sentinel.absent:
            self.contextAbsPath = contextAbsPath

        if lineWrapWidth is not Sentinel.absent:
            self.lineWrapWidth = lineWrapWidth


ic = IceCreamDebugger()
