import pytest
from manki.note import NotesDirectory


@pytest.fixture
def notes_dir(datadir):
    yield NotesDirectory(datadir, [".md", ".markdown"])


def test_notes_dir_yields_expected_paths(notes_dir: NotesDirectory):
    paths = [notes_file.path for notes_file in notes_dir.yield_note_files()]
    assert len(paths) == 1
    assert "test.md" in str(paths[0])
