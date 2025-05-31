# markdown text converter
# .
# Markdown text escape utilities for Telegram bot messages.
# This module provides functions to escape special characters for safe Telegram message formatting.
# .
# .


def markdownES(text):
    special_chars = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    escaped_text = str(text)
    for char in special_chars:
        escaped_text = escaped_text.replace(char, f"\\{char}")
    return escaped_text
