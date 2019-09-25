import pytest
from manki.note import NotesDirectory, NotesFile


@pytest.fixture
def notes_dir(datadir):
    yield NotesDirectory(datadir, [".md", ".markdown"])


def test_notes_dir_yields_expected_paths(notes_dir: NotesDirectory):
    paths = [notes_file.path for notes_file in notes_dir.yield_note_files()]
    assert len(paths) == 1
    assert "test.md" in str(paths[0])


@pytest.fixture
def notes_file(notes_dir: NotesDirectory):
    notes_files = list(notes_dir.yield_note_files())
    yield notes_files[0]


def test_notes_file_parses_frontmatter_correctly(notes_file: NotesFile):
    assert notes_file.title == "test_notes"
    assert notes_file.tags == ["Notebooks", "flashcards", "learning", "unix"]
    assert notes_file.context == "unix, test_notes"
