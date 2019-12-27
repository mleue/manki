import pytest
from manki.io import (
    get_frontmatter_and_body,
    yield_question_and_answer_pairs_from_body,
)
from manki.html import get_img_src_paths, prune_img_src_paths, markdown_to_html


@pytest.mark.parametrize(
    "html,exp",
    [
        ('<div><img src="abc"></div>', ["abc"]),
        ('<div><img src="abc"><img src="def"></div>', ["abc", "def"]),
    ],
)
def test_get_img_src_paths(html, exp):
    assert exp == list(str(p) for p in get_img_src_paths(html))


@pytest.mark.parametrize(
    "html,exp",
    [
        ('<div><img src="abc/def"></div>', '<div><img src="def"></div>'),
        (
            '<div><img src="abc/def"><img src="def/ghi"></div>',
            '<div><img src="def"><img src="ghi"></div>',
        ),
    ],
)
def test_get_img_src_paths(html, exp):
    assert exp == prune_img_src_paths(html)


def test_markdown_multiple():
    html = "- first an ul\n```python\nthen some code\n```"
    assert markdown_to_html(html) == "test"


def test_markdown_to_html(datadir):
    _, body = get_frontmatter_and_body(datadir / "test.md")
    matchers_no_removal = [r"(.*\?)$"]
    matchers_removal = [r"^\?(.*)"]
    pairs = list(yield_question_and_answer_pairs_from_body(body, matchers_no_removal, matchers_removal))
    pairs = [(markdown_to_html(q), markdown_to_html(a)) for q, a in pairs]
    assert len(pairs) == 6
    assert pairs[5][0] == "<p>easiest way to set the http response and/or headers manually?</p>"
    assert pairs[5][1] == '<ul>\n<li>return a tuple from an endpoint</li>\n</ul>\n<table class="codehilitetable"><tr><td class="linenos"><div class="linenodiv"><pre>1</pre></div></td><td class="code"><div class="codehilite"><pre><span></span><span class="n">test</span> <span class="o">=</span> <span class="n">a</span>\n</pre></div>\n</td></tr></table>'
