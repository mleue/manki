import json
from typing import List
import pytest
from manki.note import NotesDirectory, NotesFile, Note, NoteSide


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


@pytest.fixture
def notes_true(notes_dir: NotesDirectory):
    notes_true = json.loads((notes_dir.path / "test.json").read_text())
    yield notes_true


def test_notes_file_parses_frontmatter_correctly(notes_file: NotesFile):
    assert notes_file.title == "test_notes"
    assert notes_file.tags == ["Notebooks", "flashcards", "learning", "unix"]
    assert notes_file.context == "unix, test_notes"


def test_notes_file_yield_notes_no_tag_whitelist(notes_file: NotesFile):
    question_regex, question_regex_removal = [r"(.*\?)$"], [r"^\?(.*)"]
    tag_whitelist, title_blacklist = [], []
    notes = notes_file.yield_notes(
        tag_whitelist, title_blacklist, question_regex, question_regex_removal
    )
    # no notes without a tag_whitelist
    assert len(list(notes)) == 0


def test_notes_file_yield_notes_title_blacklisted(notes_file: NotesFile):
    question_regex, question_regex_removal = [r"(.*\?)$"], [r"^\?(.*)"]
    tag_whitelist, title_blacklist = [], ["test_notes"]
    notes = notes_file.yield_notes(
        tag_whitelist, title_blacklist, question_regex, question_regex_removal
    )
    # no notes if title is blacklisted
    assert len(list(notes)) == 0


def test_notes_file_yield_notes(notes_file: NotesFile):
    question_regex, question_regex_removal = [r"(.*\?)$"], [r"^\?(.*)"]
    tag_whitelist, title_blacklist = ["flashcards"], []
    notes = notes_file.yield_notes(
        tag_whitelist, title_blacklist, question_regex, question_regex_removal
    )
    # all notes if tags whitelisted and title not blacklisted
    assert len(list(notes)) == 5


def test_notes_file_yield_notes_no_question_found(notes_file: NotesFile):
    question_regex, question_regex_removal = [r"(.*!)$"], []
    tag_whitelist, title_blacklist = ["flashcards"], []
    notes = notes_file.yield_notes(
        tag_whitelist, title_blacklist, question_regex, question_regex_removal
    )
    # no notes if the regex doesn't find any questions
    assert len(list(notes)) == 0


@pytest.fixture
def notes(notes_file):
    question_regex, question_regex_removal = [r"(.*\?)$"], [r"^\?(.*)"]
    tag_whitelist, title_blacklist = ["flashcards"], []
    notes = notes_file.yield_notes(
        tag_whitelist, title_blacklist, question_regex, question_regex_removal
    )
    yield list(notes)


def test_note_attributes(notes: List[Note], notes_true):
    for note, note_true in zip(notes, notes_true):
        # print(repr(note.q_side.html).replace(r'"', r'\"'))
        # print(repr(note.a_side.html).replace(r'"', r'\"'))
        assert note.q_side.markdown == note_true["q_markdown"]
        assert note.a_side.markdown == note_true["a_markdown"]
        assert note.q_side.html == note_true["q_html"]
        assert note.a_side.html == note_true["a_html"]


def test_note_hashes_and_compares_equal():
    n1 = Note(NoteSide("a"), NoteSide("b"), ["tag"], "title", "con", "path")
    # different except for markdown question side
    n2 = Note(NoteSide("a"), NoteSide("c"), ["t2"], "t2", "con2", "path2")
    assert n1 == n2
    assert hash(n1) == hash(n2)
    assert len(set((n1, n2))) == 1
