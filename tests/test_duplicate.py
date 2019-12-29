import pytest
from manki.duplicate import Deduplicator
from manki.note import Note, NoteSide


@pytest.fixture
def deduplicator():
    yield Deduplicator(entity_type="question")


def test_deduplicates_simple_objects(deduplicator):
    location = "file x"
    a = "a"
    b = "b"
    c = "a"
    assert not deduplicator.is_duplicate(a, location)
    assert not deduplicator.is_duplicate(b, location)
    assert deduplicator.is_duplicate(c, location)


def test_deduplicates_notes(deduplicator):
    a_side = NoteSide("-def")
    tags = []
    title = ""
    context = ""
    origin_path = "."
    a = Note(NoteSide("abc?"), a_side, tags, title, context, origin_path)
    b = Note(NoteSide("def?"), a_side, tags, title, context, origin_path)
    c = Note(NoteSide("abc?"), a_side, tags, title, context, origin_path)
    assert not deduplicator.is_duplicate(a, origin_path)
    assert not deduplicator.is_duplicate(b, origin_path)
    assert deduplicator.is_duplicate(c, origin_path)
