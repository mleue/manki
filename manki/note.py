from typing import List
from pathlib import Path
from .io import (
    get_frontmatter_and_body,
    parse_frontmatter,
    resolve_nested_tags,
    yield_question_and_answer_pairs_from_body,
)
from .html import markdown_to_html, get_img_src_paths, prune_img_src_paths


class NoteSide:
    def __init__(self, markdown_text: str):
        self.markdown = markdown_text
        self.html = markdown_to_html(markdown_text)
        self.img_src_paths = list(get_img_src_paths(self.html))
        self.html = prune_img_src_paths(self.html)


class NotesFile:
    def __init__(
        self,
        note_file_path: Path,
        tag_whitelist: List[str] = None,
        title_blacklist: List[str] = None,
    ):
        self.path = note_file_path
        self.front_text, self.body_text = get_frontmatter_and_body(self.path)
        self.frontmatter = parse_frontmatter(self.front_text)
        self.frontmatter = resolve_nested_tags(self.frontmatter)
        self.tags = self.frontmatter["tags"]
        self.title = self.frontmatter["title"]
        self.tag_whitelist = [] if tag_whitelist is None else tag_whitelist
        self.title_blacklist = (
            [] if title_blacklist is None else title_blacklist
        )
        self.context = self._build_context()

    def yield_qa_pairs(self):
        if self._use_notes_from_this_file():
            for q_md, a_md in yield_question_and_answer_pairs_from_body(
                self.body_text
            ):
                yield NoteSide(q_md), NoteSide(a_md)

    def _build_context(self) -> str:
        return f"{self.tags[-1]}, {self.title}"

    def _use_notes_from_this_file(self):
        return self._has_whitelist_tags() and self._title_is_not_blacklisted()

    def _has_whitelist_tags(self):
        return self.tag_whitelist and set(self.tag_whitelist).intersection(self.frontmatter["tags"])

    def _title_is_not_blacklisted(self):
        return not self.frontmatter["title"] in self.title_blacklist
