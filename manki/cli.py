from typing import List
from pathlib import Path
import click
import genanki
from .io import (
    check_path_exists,
    check_path_is_dir,
)
from .note import NotesFile, NotesDirectory, Note
from .model import MODEL, FirstFieldGUIDNote, DECK


def resolve_media_file_paths(media_dir_path: Path, note: Note):
    # TODO check that paths actually resolve and exist
    img_paths = note.q_side.img_src_paths + note.a_side.img_src_paths
    # if media_dir_path is provided, combine that with the filename
    if media_dir_path is not None:
        return [media_dir_path / p.name for p in img_paths]
    # else keep absolute paths, preprend relative ones with note location
    else:
        abs_paths = [p for p in img_paths if p.is_absolute()]
        rel_paths = [
            (note.origin_note_file_path / ".." / p).resolve()
            for p in img_paths
            if not p.is_absolute()
        ]
        return abs_paths + rel_paths


def generate_cards(
    notes_path: Path,
    out_path: Path,
    media_path: Path,
    tag_whitelist: List[str],
    title_blacklist: List[str],
    file_type: List[str],
):
    media_file_paths = []
    notes_dir = NotesDirectory(notes_path, file_type, tag_whitelist, title_blacklist)
    for note in notes_dir.yield_notes():
        media_file_paths.extend(resolve_media_file_paths(media_path, note))
        genanki_note = FirstFieldGUIDNote(
            model=MODEL,
            fields=[note.q_side.html, note.a_side.html, note.context],
            tags=note.tags + [note.title],
        )
        DECK.add_note(genanki_note)

    click.echo(media_file_paths)
    pkg = genanki.Package(deck_or_decks=DECK, media_files=media_file_paths)
    out_path = Path(out_path) if out_path is not None else notes_path
    pkg.write_to_file(out_path / "genanki.apkg")


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
    # TODO move this to where the paths are actually being used
    try:
        for p in [notes_path, out_path, media_path]:
            if p is not None:
                check_path_exists(Path(p))
                check_path_is_dir(Path(p))
    except ValueError as e:
        click.echo(str(e))
        return

    generate_cards(
        Path(notes_path),
        Path(out_path) if out_path is not None else out_path,
        Path(media_path) if media_path is not None else media_path,
        tag_whitelist,
        title_blacklist,
        file_type,
    )
