import pytest
from manki.io import (
    get_frontmatter_and_body,
    yield_question_and_answer_pairs_from_body,
)
from manki.convert import markdown_to_html


@pytest.mark.xfail
def test_markdown_to_html(datadir):
    _, body = get_frontmatter_and_body(datadir / "test.md")
    for q, a in yield_question_and_answer_pairs_from_body(body):
        print(q)
        print(markdown_to_html(q))
        print("---")
        print(a)
        print(markdown_to_html(a))
        print()
    assert False
