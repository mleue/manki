from typing import List
from pathlib import Path
import re
import yaml


def yield_files_from_dir_recursively(base_dir: Path):
    dirs = []
    for p in base_dir.iterdir():
        if p.is_file():
            yield base_dir / p
        else:
            dirs.append(p)
    for d in dirs:
        yield from yield_files_from_dir_recursively(base_dir / d)


def filter_paths_by_extension(paths: List[Path], extensions: List[str]):
    if not extensions:
        yield from paths
    for p in paths:
        if p.suffix in extensions:
            yield p


def get_frontmatter_and_body(filepath: Path):
    text = filepath.read_text()
    _, frontmatter, body = re.split("---\n", text)
    return frontmatter, body


def parse_frontmatter(frontmatter_text: str):
    return yaml.safe_load(frontmatter_text)


def resolve_nested_tags(frontmatter):
    """Resolve notable-style nested tags (nested via / separators)."""
    if "tags" not in frontmatter:
        return frontmatter
    else:
        new_tags = []
        for tag in frontmatter["tags"]:
            new_tags.extend(tag.split("/"))
        frontmatter["tags"] = new_tags
        return frontmatter


def is_question(line: str):
    match = re.match(r".*\?$", line.strip())
    return match is not None


def yield_question_and_answer_pairs_from_body(body_text: str):
    pass
