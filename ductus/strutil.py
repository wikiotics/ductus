"""Import this file to aid with Python 2.6/3.0 string transition"""

try:
    bytes
except NameError:
    bytes = str
