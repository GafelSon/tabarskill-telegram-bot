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
