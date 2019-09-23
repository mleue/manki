from typing import List
from pathlib import Path
import click
from .io import (
    get_frontmatter_and_body,
    parse_frontmatter,
    resolve_nested_tags,
    yield_question_and_answer_pairs_from_body,
    yield_files_from_dir_recursively,
    filter_paths_by_extension,
)
from .html import markdown_to_html, get_img_src_paths, prune_img_src_paths


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


class NotesFile:
    def __init__(
        self,
        note_file_path: Path,
        tag_whitelist: List[str],
        title_blacklist: List[str],
    ):
        self.path = note_file_path
        self.front_text, self.body_text = get_frontmatter_and_body(self.path)
        self.frontmatter = parse_frontmatter(self.front_text)
        self.frontmatter = resolve_nested_tags(self.frontmatter)
        self.tags = self.frontmatter["tags"]
        self.title = self.frontmatter["title"]
        self.tag_whitelist = tag_whitelist
        self.title_blacklist = title_blacklist
        self.context = self._build_context()

    def yield_notes(self):
        click.echo(self.path)
        i = 0
        if self._use_notes_from_this_file():
            for q_md, a_md in yield_question_and_answer_pairs_from_body(
                self.body_text
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
        click.echo(f"{i} notes from file {self.path}")

    def _build_context(self) -> str:
        return f"{self.tags[-1]}, {self.title}"

    def _use_notes_from_this_file(self):
        return self._has_whitelist_tags() and self._title_is_not_blacklisted()

    def _has_whitelist_tags(self):
        return self.tag_whitelist and set(self.tag_whitelist).intersection(
            self.frontmatter["tags"]
        )

    def _title_is_not_blacklisted(self):
        return not self.frontmatter["title"] in self.title_blacklist


class NotesDirectory:
    def __init__(
        self,
        notes_dir_path: Path,
        file_type: List[str],
        tag_whitelist: List[str],
        title_blacklist: List[str],
    ):
        self.path = notes_dir_path
        self.file_type = file_type
        self.tag_whitelist = [] if tag_whitelist is None else tag_whitelist
        self.title_blacklist = (
            [] if title_blacklist is None else title_blacklist
        )
        self.questions = dict()

    def yield_notes(self):
        files = yield_files_from_dir_recursively(self.path)
        for filepath in filter_paths_by_extension(files, self.file_type):
            notes_file = NotesFile(
                filepath,
                tag_whitelist=self.tag_whitelist,
                title_blacklist=self.title_blacklist,
            )
            for note in notes_file.yield_notes():
                if self._is_duplicate_question(note):
                    continue
                else:
                    yield note

    def _is_duplicate_question(self, note: Note):
        # TODO check against hash here
        if note.q_side.markdown in self.questions:
            l1 = f"Duplicate question encountered: '{note.q_side.markdown}'."
            initial_file_occurence = self.questions[note.q_side.markdown]
            l2 = f"First seen in file '{initial_file_occurence}'."
            l3 = "Disregarding."
            click.echo(f"{l1}\n{l2}\n{l3}")
            return True
        else:
            return False
