from manki.io import yield_files_from_dir_recursively, filter_paths_by_extension


def test_get_files_from_dir_recursively(datadir):
    expected = [datadir / "test.txt", datadir / "test.md"]
    assert expected == list(yield_files_from_dir_recursively(datadir))


def test_filter_paths_by_extension(datadir):
    expected = [datadir / "test.md"]
    paths = yield_files_from_dir_recursively(datadir)
    assert expected == list(filter_paths_by_extension(paths, [".md"]))
