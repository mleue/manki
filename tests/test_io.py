import pytest
from manki.io import (
    yield_files_from_dir_recursively,
    filter_paths_by_extension,
    read_frontmatter,
    parse_frontmatter,
    resolve_nested_tags,
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


def test_read_frontmatter(datadir):
    expected = "title: test\ntags: [Notebooks/flashcards/learning/unix]\n"
    frontmatter_text = read_frontmatter(datadir / "test.md")
    assert expected == frontmatter_text


def test_parse_frontmatter(datadir):
    expected = {
        "title": "test",
        "tags": ["Notebooks/flashcards/learning/unix"],
    }
    frontmatter_obj = parse_frontmatter(read_frontmatter(datadir / "test.md"))
    print(frontmatter_obj)
    assert expected == frontmatter_obj


def test_resolve_nested_tags(datadir):
    expected = {
        "title": "test",
        "tags": ["Notebooks", "flashcards", "learning", "unix"],
    }
    assert expected == resolve_nested_tags(
        parse_frontmatter(read_frontmatter(datadir / "test.md"))
    )
