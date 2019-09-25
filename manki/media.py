from typing import List
from pathlib import Path
import click
from .note import Note


def filter_paths_existing(paths: List[Path]):
    existing_paths = []
    for path in paths:
        if not path.exists():
            click.echo(f"Path {path} does not exist. Ignoring.")
        else:
            existing_paths.append(path)
    return existing_paths


def resolve_media_file_paths(notes: List[Note], media_path: Path):
    media_path = Path(media_path) if media_path is not None else media_path
    media_file_paths = []
    for note in notes:
        img_paths = note.q_side.img_src_paths + note.a_side.img_src_paths
        # if media_path is provided, combine that with the filename
        if media_path is not None:
            media_file_paths.extend(media_path / p.name for p in img_paths)
        # else keep absolute paths, preprend relative ones with note location
        else:
            abs_paths = [p for p in img_paths if p.is_absolute()]
            rel_paths = [
                (note.path / ".." / p).resolve()
                for p in img_paths
                if not p.is_absolute()
            ]
            media_file_paths.extend(abs_paths + rel_paths)
    return filter_paths_existing(media_file_paths)
