from pathlib import Path


def yield_files_from_dir_recursively(base_dir: Path):
    dirs = []
    for p in base_dir.iterdir():
        if p.is_file():
            yield base_dir / p
        else:
            dirs.append(p)
    for d in dirs:
        yield from yield_files_from_dir_recursively(base_dir / d)
