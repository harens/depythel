"""Updates the version number of both the API and CLT automatically.

Does this for both manually selected toml and python files.
"""

import fileinput
import re

# Process based on https://stackoverflow.com/a/11898226

VERSION_NUMBER = "0.1.0"
FILES = (
    "pyproject.toml",
    "depythel_api/pyproject.toml",
    "depythel_api/depythel/__init__.py",
    "depythel_clt/__init__.py",
)

# Determines type of file being modified
# Based on https://stackoverflow.com/a/36801287
# Replace version number surrounded in quotation marks
toml = re.compile('version = ".(.*)"')
python = re.compile('__version__ = ".(.*)"')

for file in FILES:
    for line in fileinput.input(file, inplace=True):
        # Double quotes since version number is string in file
        print(
            f'version = "{VERSION_NUMBER}"'
            if toml.match(line)
            else f'__version__ = "{VERSION_NUMBER}"'
            if python.match(line)
            else line.replace("\n", "")
        )
