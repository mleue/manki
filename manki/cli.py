from typing import List
from pathlib import Path
import click
import genanki
from .io import read_file_with_default, save_as_package
from .note import NotesDirectory, Note, TIME_OF_RUN
from .model import DECK, MODEL
from .duplicate import Deduplicator
from .media import resolve_media_file_paths

# TODO add logging
dir_path_type = click.Path(exists=True, file_okay=False)
file_path_type = click.Path(exists=True, file_okay=True)


@click.command()
@click.argument("notes_path", type=dir_path_type)
@click.option("-o", "--out-path", default=None, type=dir_path_type)
@click.option("-m", "--media-path", default=None, type=dir_path_type)
@click.option("-w", "--tag-whitelist", type=str, multiple=True)
@click.option("-b", "--title-blacklist", type=str, multiple=True)
@click.option("-f", "--file-type", type=str, default=(".md",), multiple=True)
@click.option("-c", "--css-file", type=file_path_type, default=None)
@click.option("-p", "--pygments-css-file", type=file_path_type, default=None)
@click.option("-q", "--question-regex", type=str, default=(r"(.*\?)$",))
@click.option(
    "-r", "--question-regex-removal", type=str, default=(r"^\?(.*)",)
)
def manki_cli(
    notes_path,
    out_path,
    media_path,
    tag_whitelist,
    title_blacklist,
    file_type,
    css_file,
    pygments_css_file,
    question_regex,
    question_regex_removal,
):
    # load resources
    MODEL.css += read_file_with_default(css_file, "style.css")
    MODEL.css += read_file_with_default(pygments_css_file, "pygments.css")

    # generate cards and add to deck
    notes_path = Path(notes_path)
    d = NotesDirectory(notes_path, file_type)
    deduplicator = Deduplicator(entity_type="question")
    notes = []
    for notes_file in d.yield_note_files():
        for note in notes_file.yield_notes(
            tag_whitelist,
            title_blacklist,
            question_regex,
            question_regex_removal,
        ):
            if not deduplicator.is_duplicate(
                note, str(note.origin_note_file_path)
            ):
                notes.append(note)
                DECK.add_note(note.to_genanki_note())

    media_file_paths = resolve_media_file_paths(notes, media_path)

    save_as_package(out_path, DECK, media_file_paths)
    click.echo(f"{len(deduplicator.entities)} notes put into the package.")
    click.echo(f"time tag for this run: {TIME_OF_RUN}")
