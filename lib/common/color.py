__author__ = 'RongShun'

import os
import sys

def color(text, color_code):
    if sys.platform == "win32" and os.getenv("TERM") != "xterm":
        return text
    return "\x1b[%dm%s\x1b[0m" % (color_code, text)

def green(text):
    return color(text, 32)

def yellow(text):
    return color(text, 33)

def white(text):
    return color(text, 37)

def bold(text):
    return color(text, 1)

def black(text):
    return color(text, 30)

def red(text):
    return color(text, 31)

def blue(text):
    return color(text, 34)

def magenta(text):
    return color(text, 35)

def cyan(text):
    return color(text, 36)
