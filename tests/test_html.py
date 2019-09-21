import pytest
from manki.io import (
    get_frontmatter_and_body,
    yield_question_and_answer_pairs_from_body,
)
from manki.html import markdown_to_html


def test_markdown_to_html(datadir):
    _, body = get_frontmatter_and_body(datadir / "test.md")
    qas = list(yield_question_and_answer_pairs_from_body(body))
    assert markdown_to_html(qas[0][0]).startswith("<p>what is")
