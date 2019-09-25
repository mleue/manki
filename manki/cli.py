from typing import List
from pathlib import Path
import click
import genanki
from .io import read_file_with_default
from .note import NotesDirectory, Note, TIME_OF_RUN
from .model import DECK, MODEL
from .duplicate import Deduplicator

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
@click.option("-q", "--question-regex", type=str, default=r"(.*\?)$")
@click.option("-r", "--question-regex-removal", type=str, default=r"^\?(.*)")
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
    click.echo(tag_whitelist)
    click.echo(title_blacklist)
    # load resources
    MODEL.css += read_file_with_default(css_file, "style.css")
    MODEL.css += read_file_with_default(pygments_css_file, "pygments.css")

    # generate cards and add to deck
    notes_path = Path(notes_path)
    media_path = Path(media_path) if media_path is not None else media_path
    media_file_paths = []
    d = NotesDirectory(notes_path, file_type)
    deduplicator = Deduplicator(entity_type="question")
    for notes_file in d.yield_note_files():
        for note in notes_file.yield_notes(tag_whitelist, title_blacklist):
            if not deduplicator.is_duplicate(note, str(notes_file.path)):
                media_file_paths.extend(
                    note.resolve_media_file_paths(media_path)
                )
                DECK.add_note(note.to_genanki_note())

    # create and save a package
    click.echo(media_file_paths)
    out_path = Path(out_path) if out_path is not None else Path.cwd()
    pkg = genanki.Package(deck_or_decks=DECK, media_files=media_file_paths)
    pkg.write_to_file(out_path / "genanki.apkg")
    click.echo(f"time tag for this run: {TIME_OF_RUN}")
