from typing import List
from pathlib import Path
import click
import genanki
from .io import (
    yield_files_from_dir_recursively,
    filter_paths_by_extension,
    get_frontmatter_and_body,
    parse_frontmatter,
    resolve_nested_tags,
    yield_question_and_answer_pairs_from_body,
    check_path_exists,
    check_path_is_dir,
)
from .note import NotesFile, NoteSide, NotesDirectory
from .model import MODEL, FirstFieldGUIDNote, DECK


def generate_cards(
    notes_path: Path,
    out_path: Path,
    media_path: Path,
    tag_whitelist: List[str],
    title_blacklist: List[str],
    file_type: List[str],
):
    img_paths = []
    notes_dir = NotesDirectory(notes_path, file_type, tag_whitelist, title_blacklist)
    for note in notes_dir.yield_notes():
        img_paths.extend(note.q_side.img_src_paths + note.a_side.img_src_paths)
        genanki_note = FirstFieldGUIDNote(
            model=MODEL,
            fields=[note.q_side.html, note.a_side.html, note.context],
            tags=note.tags + [note.title],
        )
        DECK.add_note(genanki_note)

    # TODO check that paths actually resolve and exist
    # if media path is provided, combine that path with each img_paths filename
    if media_path is not None:
        media_path = Path(media_path)
        img_paths = [media_path / p.name for p in img_paths]
    else:
        abs_paths = [p for p in img_paths if p.is_absolute()]
        # TODO don't use notes_path but card_path here once we have a card class
        rel_paths = [
            (notes_path / p).resolve()
            for p in img_paths
            if not p.is_absolute()
        ]
        img_paths = abs_paths + rel_paths

    click.echo(img_paths)
    pgk = genanki.Package(deck_or_decks=DECK, media_files=img_paths)
    out_path = Path(out_path) if out_path is not None else notes_path
    pgk.write_to_file(out_path / "genanki.apkg")


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
