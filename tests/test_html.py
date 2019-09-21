import pytest
from manki.io import (
    get_frontmatter_and_body,
    yield_question_and_answer_pairs_from_body,
)
from manki.html import get_img_src_paths, prune_img_src_paths


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
