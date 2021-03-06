import re
from pathlib import Path
from selectolax.parser import HTMLParser
import markdown


def markdown_to_html(markdown_text: str):
    # markdown parser
    html = markdown.markdown(
        markdown_text,
        extensions=["fenced_code", "codehilite", "pymdownx.arithmatex"],
        extension_configs={
            "codehilite": {"linenums": True},
            "pymdownx.arithmatex": {"generic": True},
        },
    )
    return html


def get_img_src_paths(html: str):
    for node in HTMLParser(html).css("img"):
        if "src" in node.attributes:
            yield Path(node.attributes["src"])


def prune_img_src_paths(html: str):
    tree = HTMLParser(html)
    for node in tree.css("img"):
        if "src" in node.attributes:
            path = Path(node.attributes["src"])
            node.attrs["src"] = path.name
    html = "\n".join([c.html for c in tree.body.iter()])
    return html
