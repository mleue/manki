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
from .convert import markdown_to_html, get_image_sources
from .model import MODEL, FirstFieldGUIDNote, DECK


def generate_cards(notes_path: Path):
    files = yield_files_from_dir_recursively(notes_path)
    # TODO sort media file collection out
    media_files = []
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
            context = frontmatter["tags"][-1]
            # TODO this too is an implementation detail for when "title" is available
            frontmatter["tags"].append(frontmatter["title"])
            # TODO put this in parse_frontmatter
            frontmatter["tags"] = [tag.replace(" ", "_") for tag in frontmatter["tags"]]
            click.echo(frontmatter)
            for q, a in yield_question_and_answer_pairs_from_body(body_text):
                click.echo(q)
                click.echo(a)
                markdown_q = markdown_to_html(q)
                markdown_a = markdown_to_html(a)
                # TODO this should be built into some own note class
                markdown_a = markdown_a.replace("@attachment/", "")
                media_files.extend(get_image_sources(markdown_a))
                # TODO untangle this
                note = FirstFieldGUIDNote(
                    model=MODEL,
                    fields=[markdown_q, markdown_a, context],
                    tags=frontmatter["tags"],
                )
                DECK.add_note(note)
    # TODO media reference resolution
    media_path = notes_path.parent / "attachments"
    media_files = [media_path / f for f in media_files]
    click.echo(media_files)
    pgk = genanki.Package(deck_or_decks=DECK, media_files=media_files)
    # TODO specifiy out path as cli option, default to current cli path
    pgk.write_to_file(Path.home() / "Downloads" / "genanki.apkg")


@click.command()
@click.argument("notes_path")
def manki_cli(notes_path):
    p = Path(notes_path)
    if not p.exists():
        click.echo(f"Path {p.absolute()} does not exist.")
    elif not p.is_dir():
        click.echo(f"Path {p.absolute()} is not a dir.")
    else:
        click.echo(p.absolute())
        generate_cards(p)
