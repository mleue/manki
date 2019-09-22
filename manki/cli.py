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
)
from .note import NotesFile, NoteSide
from .model import MODEL, FirstFieldGUIDNote, DECK


# TODO notify when duplicate questions are encountered
def generate_cards(
    notes_path: Path,
    out_path: Path,
    media_path: Path,
    tag_whitelist: List[str],
    title_blacklist: List[str],
):
    files = yield_files_from_dir_recursively(notes_path)
    img_paths = []
    # TODO file types as cli option
    for filepath in filter_paths_by_extension(files, ".md"):
        click.echo(filepath)
        notes_file = NotesFile(
            filepath,
            tag_whitelist=tag_whitelist,
            title_blacklist=title_blacklist,
        )
        i = 0
        for q_side, a_side in notes_file.yield_qa_pairs():
            img_paths.extend(q_side.img_src_paths + a_side.img_src_paths)
            note = FirstFieldGUIDNote(
                model=MODEL,
                fields=[q_side.html, a_side.html, notes_file.context],
                tags=notes_file.tags + [notes_file.title],
            )
            DECK.add_note(note)
            i += 1
        click.echo(f"{i} notes from file {filepath}")

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
def manki_cli(notes_path, out_path, media_path, tag_whitelist, title_blacklist):
    # TODO also check for media_path availability if used
    p = Path(notes_path)
    if not p.exists():
        click.echo(f"Path {p.absolute()} does not exist.")
    elif not p.is_dir():
        click.echo(f"Path {p.absolute()} is not a dir.")
    else:
        click.echo(p.absolute())
        generate_cards(p, out_path, media_path, tag_whitelist, title_blacklist)
