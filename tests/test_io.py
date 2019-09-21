import pytest
from manki.io import (
    yield_files_from_dir_recursively,
    filter_paths_by_extension,
    get_frontmatter_and_body,
    parse_frontmatter,
    resolve_nested_tags,
    is_question,
    yield_question_and_answer_pairs_from_body,
)


def test_get_files_from_dir_recursively(datadir):
    expected = [datadir / "test.txt", datadir / "test.md"]
    assert expected == list(yield_files_from_dir_recursively(datadir))


@pytest.mark.parametrize(
    "extensions,exp_files",
    [
        ([".md"], ["test.md"]),
        ([".txt"], ["test.txt"]),
        ([], ["test.txt", "test.md"]),
    ],
)
def test_filter_paths_by_extension(datadir, extensions, exp_files):
    expected = [datadir / file for file in exp_files]
    paths = yield_files_from_dir_recursively(datadir)
    assert expected == list(filter_paths_by_extension(paths, extensions))


def test_get_frontmatter_and_body(datadir):
    front = "title: test\ntags: [Notebooks/flashcards/learning/unix]\n"
    frontmatter, body = get_frontmatter_and_body(datadir / "test.md")
    assert front == frontmatter
    assert body[:4] == "what"
    assert body[-4:] == "ng)\n"


def test_parse_frontmatter(datadir):
    expected = {
        "title": "test",
        "tags": ["Notebooks/flashcards/learning/unix"],
    }
    frontmatter_text, _ = get_frontmatter_and_body(datadir / "test.md")
    frontmatter_obj = parse_frontmatter(frontmatter_text)
    assert expected == frontmatter_obj


def test_resolve_nested_tags(datadir):
    expected = {
        "title": "test",
        "tags": ["Notebooks", "flashcards", "learning", "unix"],
    }
    frontmatter_text, _ = get_frontmatter_and_body(datadir / "test.md")
    frontmatter_obj = parse_frontmatter(frontmatter_text)
    assert expected == resolve_nested_tags(frontmatter_obj)


def test_detect_question():
    assert is_question("is this a question?")
    assert not is_question("this is not a question")


def test_yield_question_and_answer_pairs_from_body(datadir):
    _, body = get_frontmatter_and_body(datadir / "test.md")
    pairs = list(yield_question_and_answer_pairs_from_body(body))
    assert len(pairs) == 4
    assert pairs[0][0] == "what is `dmesg`?"
    assert pairs[1][1] == "`dmesg --follow`"
    assert pairs[2][0] == "is it possible to use python here as well?"
    assert pairs[2][1][-3:] == "```"
