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


def test_markdown_to_html(datadir):
    _, body = get_frontmatter_and_body(datadir / "test.md")
    matchers_no_removal = [r"(.*\?)$"]
    matchers_removal = [r"^\?(.*)"]
    pairs = list(yield_question_and_answer_pairs_from_body(body, matchers_no_removal, matchers_removal))
    pairs = [(markdown_to_html(q), markdown_to_html(a)) for q, a in pairs]
    assert len(pairs) == 5
