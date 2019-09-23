from typing import List
from pathlib import Path
import click
import genanki
from .io import check_path_exists, check_path_is_dir
from .note import NotesDirectory, Note
from .model import DECK, MODEL

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
@click.option("-p", "--pygments-css-file", type=file_path_type, default=None)
def manki_cli(
    notes_path,
    out_path,
    media_path,
    tag_whitelist,
    title_blacklist,
    file_type,
    pygments_css_file,
):
    # handle paths
    notes_path = Path(notes_path)
    out_path = Path(out_path) if out_path is not None else Path.cwd()
    media_path = Path(media_path) if media_path is not None else media_path
    pygments_css_file = (
        Path(__file__).parent / "pygments_default.css"
        if pygments_css_file is None
        else Path(pygments_css_file)
    )
    MODEL.css += pygments_css_file.read_text()

    # generate cards and add to deck
    media_file_paths = []
    notes_dir = NotesDirectory(
        notes_path, file_type, tag_whitelist, title_blacklist
    )
    for note in notes_dir.yield_notes():
        media_file_paths.extend(note.resolve_media_file_paths(media_path))
        DECK.add_note(note.to_genanki_note())

    # create and save a package
    click.echo(media_file_paths)
    pkg = genanki.Package(deck_or_decks=DECK, media_files=media_file_paths)
    pkg.write_to_file(out_path / "genanki.apkg")
