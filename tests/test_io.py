import pytest
from manki.io import (
    yield_files_from_dir_recursively,
    filter_paths_by_extension,
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
