from typing import Any

import click
from rich.highlighter import RegexHighlighter

STYLE_OPTION: str
STYLE_SWITCH: str
STYLE_METAVAR: str
STYLE_METAVAR_APPEND: str
STYLE_HEADER_TEXT: str
STYLE_FOOTER_TEXT: str
STYLE_USAGE: str
STYLE_USAGE_COMMAND: str
STYLE_DEPRECATED: str
STYLE_HELPTEXT_FIRST_LINE: str
STYLE_HELPTEXT: str
STYLE_OPTION_HELP: str
STYLE_OPTION_DEFAULT: str
STYLE_REQUIRED_SHORT: str
STYLE_REQUIRED_LONG: str
STYLE_OPTIONS_PANEL_BORDER: str
ALIGN_OPTIONS_PANEL: str
STYLE_COMMANDS_PANEL_BORDER: str
ALIGN_COMMANDS_PANEL: str
STYLE_ERRORS_PANEL_BORDER: str
ALIGN_ERRORS_PANEL: str
STYLE_ERRORS_SUGGESTION: str
STYLE_ABORTED: str
MAX_WIDTH: Any
COLOR_SYSTEM: str
HEADER_TEXT: Any
FOOTER_TEXT: Any
DEPRECATED_STRING: str
DEFAULT_STRING: str
REQUIRED_SHORT_STRING: str
REQUIRED_LONG_STRING: str
RANGE_STRING: str
APPEND_METAVARS_HELP_STRING: str
ARGUMENTS_PANEL_TITLE: str
OPTIONS_PANEL_TITLE: str
COMMANDS_PANEL_TITLE: str
ERRORS_PANEL_TITLE: str
ERRORS_SUGGESTION: Any
ERRORS_EPILOGUE: Any
ABORTED_TEXT: str
SHOW_ARGUMENTS: bool
SHOW_METAVARS_COLUMN: bool
APPEND_METAVARS_HELP: bool
GROUP_ARGUMENTS_OPTIONS: bool
USE_MARKDOWN: bool
USE_RICH_MARKUP: bool
COMMAND_GROUPS: Any
OPTION_GROUPS: Any
USE_CLICK_SHORT_HELP: bool

class OptionHighlighter(RegexHighlighter):
    highlights: Any

highlighter: Any

def rich_format_help(
    obj, ctx: click.Context, formatter: click.HelpFormatter
) -> None: ...
def rich_format_error(self) -> None: ...
def rich_abort_error() -> None: ...

class RichCommand(click.Command):
    standalone_mode: bool
    def main(self, *args, standalone_mode: bool = ..., **kwargs): ...
    def format_help(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None: ...

class RichGroup(click.Group):
    command_class: Any
    group_class: Any
    def main(self, *args, standalone_mode: bool = ..., **kwargs): ...
    def format_help(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None: ...
