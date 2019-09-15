from selectolax.parser import HTMLParser
import markdown


def markdown_to_html(markdown_text: str):
    return markdown.markdown(
        markdown_text,
        extensions=["fenced_code", "codehilite"],
        extension_configs={"codehilite": {"linenums": True}},
    )


# TODO this should go into some html module
def get_image_sources(html: str):
    selector = "img"
    sources = []
    for node in HTMLParser(html).css(selector):
        if "src" in node.attributes:
            sources.append(node.attributes["src"])
    return sources
