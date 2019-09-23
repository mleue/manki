from typing import List
from pathlib import Path
import click
import genanki
from .io import check_path_exists, check_path_is_dir
from .note import NotesDirectory, Note
from .model import DECK
# TODO add logging


@click.command()
@click.argument("notes_path")
@click.option("-o", "--out-path", default=None, type=str)
@click.option("-m", "--media-path", default=None, type=str)
@click.option("-w", "--tag-whitelist", type=str, multiple=True)
@click.option("-b", "--title-blacklist", type=str, multiple=True)
@click.option("-f", "--file-type", type=str, default=(".md",), multiple=True)
def manki_cli(
    notes_path, out_path, media_path, tag_whitelist, title_blacklist, file_type
):
    notes_path = Path(notes_path)
    out_path = Path(out_path) if out_path is not None else out_path
    media_path = Path(media_path) if media_path is not None else media_path
    try:
        for p in [notes_path, out_path, media_path]:
            if p is not None:
                check_path_exists(p)
                check_path_is_dir(p)
    except ValueError as e:
        click.echo(str(e))
        return

    media_file_paths = []
    notes_dir = NotesDirectory(
        notes_path, file_type, tag_whitelist, title_blacklist
    )
    for note in notes_dir.yield_notes():
        media_file_paths.extend(note.resolve_media_file_paths(media_path))
        DECK.add_note(note.to_genanki_note())

    click.echo(media_file_paths)
    pkg = genanki.Package(deck_or_decks=DECK, media_files=media_file_paths)
    out_path = Path(out_path) if out_path is not None else notes_path
    pkg.write_to_file(out_path / "genanki.apkg")
