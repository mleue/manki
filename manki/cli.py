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
from .convert import NoteSide
from .model import MODEL, FirstFieldGUIDNote, DECK


# TODO notify when duplicate questions are encountered
def generate_cards(notes_path: Path, media_path: Path = None):
    files = yield_files_from_dir_recursively(notes_path)
    img_paths = []
    # TODO file types as cli option
    for file in filter_paths_by_extension(files, ".md"):
        click.echo(file)
        frontmatter_text, body_text = get_frontmatter_and_body(file)
        frontmatter = parse_frontmatter(frontmatter_text)
        frontmatter = resolve_nested_tags(frontmatter)
        # TODO tag whitelisting via options
        # TODO title blacklisting via options
        # TODO refactor out the tag whitelisting and title blacklisting
        if "flashcards" in frontmatter["tags"] and frontmatter[
            "title"
        ] not in ("goals", "questions"):
            # TODO this is an implementation detail for notable
            frontmatter["tags"].remove("Notebooks")
            # TODO make this explicit somewhere
            # TODO context should be both last tag AND title
            context = frontmatter["tags"][-1]
            # TODO this too is an implementation detail for when "title" is available
            frontmatter["tags"].append(frontmatter["title"])
            # TODO put this in parse_frontmatter
            frontmatter["tags"] = [
                tag.replace(" ", "_") for tag in frontmatter["tags"]
            ]
            click.echo(frontmatter)
            for q, a in yield_question_and_answer_pairs_from_body(body_text):
                click.echo(q)
                click.echo(a)
                q_side = NoteSide(q)
                a_side = NoteSide(a)
                img_paths.extend(q_side.img_src_paths + a_side.img_src_paths)
                # TODO untangle this
                note = FirstFieldGUIDNote(
                    model=MODEL,
                    fields=[q_side.html, a_side.html, context],
                    tags=frontmatter["tags"],
                )
                DECK.add_note(note)

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
    # TODO specifiy out path as cli option, default to current cli path
    pgk.write_to_file(Path.home() / "Downloads" / "genanki.apkg")


@click.command()
@click.argument("notes_path")
@click.option("-m", "--media-path", default=None, type=str)
def manki_cli(notes_path, media_path):
    # TODO also check for media_path availability if used
    p = Path(notes_path)
    if not p.exists():
        click.echo(f"Path {p.absolute()} does not exist.")
    elif not p.is_dir():
        click.echo(f"Path {p.absolute()} is not a dir.")
    else:
        click.echo(p.absolute())
        generate_cards(p, media_path)
