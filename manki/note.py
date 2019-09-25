from typing import List
from pathlib import Path
import time
import click
import genanki
from .io import (
    get_frontmatter_and_body,
    parse_frontmatter,
    resolve_nested_tags,
    yield_question_and_answer_pairs_from_body,
    yield_files_from_dir_recursively,
    filter_paths_by_extension,
)
from .html import markdown_to_html, get_img_src_paths, prune_img_src_paths
from .model import MODEL


TIME_OF_RUN = int(time.time())


class NoteSide:
    def __init__(self, markdown_text: str):
        self.markdown = markdown_text
        self.html = markdown_to_html(markdown_text)
        self.img_src_paths = list(get_img_src_paths(self.html))
        self.html = prune_img_src_paths(self.html)


class Note:
    def __init__(
        self,
        q_side: NoteSide,
        a_side: NoteSide,
        tags: List[str],
        title: str,
        context: str,
        origin_note_file_path: Path,
    ):
        self.q_side = q_side
        self.a_side = a_side
        self.tags = tags
        self.title = title
        self.context = context
        self.origin_note_file_path = origin_note_file_path

    # TODO refactor this out into a media resolver class
    def resolve_media_file_paths(self, media_dir_path: Path):
        # TODO check that paths actually resolve and exist
        img_paths = self.q_side.img_src_paths + self.a_side.img_src_paths
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

    def to_genanki_note(self):
        return genanki.Note(
            model=MODEL,
            fields=[self.q_side.html, self.a_side.html, self.context],
            tags=self.tags + [self.title] + [str(TIME_OF_RUN)],
            # custom guid, instead of based on all fields (genanki default)
            # we base it on the markdown of the question
            guid=genanki.guid_for(self.q_side.markdown),
        )

    def __hash__(self):
        return hash(self.q_side.markdown)

    def __eq__(self, other):
        return self.q_side.markdown == other.q_side.markdown

    def __str__(self):
        return f"Note('{self.q_side.markdown}')"


class NotesFile:
    def __init__(self, note_file_path: Path):
        self.path = note_file_path
        self.front_text, self.body_text = get_frontmatter_and_body(self.path)
        self.frontmatter = parse_frontmatter(self.front_text)
        self.frontmatter = resolve_nested_tags(self.frontmatter)
        self.tags = self.frontmatter["tags"]
        self.title = self.frontmatter["title"].replace(" ", "_")
        self.context = self._build_context()

    def yield_notes(
        self,
        tag_whitelist: List[str],
        title_blacklist: List[str],
        question_regex: List[str],
        question_regex_removal: List[str],
    ):
        i = 0
        if self._has_whitelist_tags(
            tag_whitelist
        ) and self._title_is_not_blacklisted(title_blacklist):
            for q_md, a_md in yield_question_and_answer_pairs_from_body(
                self.body_text,
                question_regex,
                question_regex_removal,
            ):
                yield Note(
                    NoteSide(q_md),
                    NoteSide(a_md),
                    self.tags,
                    self.title,
                    self.context,
                    self.path,
                )
                i += 1
        click.echo(f"{i} notes found in file {self.path}")

    def _build_context(self) -> str:
        return f"{self.tags[-1]}, {self.title}"

    def _has_whitelist_tags(self, tag_whitelist: List[str]):
        return tag_whitelist and set(tag_whitelist).intersection(self.tags)

    def _title_is_not_blacklisted(self, title_blacklist: List[str]):
        return self.title not in title_blacklist


class NotesDirectory:
    def __init__(self, notes_dir_path: Path, file_type: List[str]):
        self.path = notes_dir_path
        self.file_type = file_type

    def yield_note_files(self):
        files = yield_files_from_dir_recursively(self.path)
        for filepath in filter_paths_by_extension(files, self.file_type):
            notes_file = NotesFile(filepath)
            yield notes_file
