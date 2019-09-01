import markdown


def markdown_to_html(markdown_text: str):
    return markdown.markdown(
        markdown_text,
        extensions=["fenced_code", "codehilite"],
        extension_configs={"codehilite": {"linenums": True}},
    )
