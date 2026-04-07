#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


SOURCE_DIR = Path(
    "/home/piperofthedawn/Insync/kumarshan25@gmail.com/Google Drive/KumarsNotes/CFA Notes"
)
OUTPUT_DIR = Path("NOTES")
EXCLUDED_FILES = {"Preamble.md", "AGENT.md", "Read these again.md"}
HEADING_PATTERN = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


def slugify_heading(heading: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", heading, flags=re.UNICODE).strip().lower()
    slug = re.sub(r"[-\s]+", "_", slug)
    return slug or "untitled"


def split_sections(markdown: str) -> list[tuple[str, str]]:
    matches = list(HEADING_PATTERN.finditer(markdown))
    sections: list[tuple[str, str]] = []

    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        content = markdown[start:end].strip()
        sections.append((heading, content))

    return sections


def write_sections(source_file: Path, destination_root: Path) -> int:
    destination_dir = destination_root / source_file.name
    destination_dir.mkdir(parents=True, exist_ok=True)

    markdown = source_file.read_text(encoding="utf-8")
    sections = split_sections(markdown)

    if not sections:
        return 0

    used_names: dict[str, int] = {}
    for heading, content in sections:
        base_name = slugify_heading(heading)
        count = used_names.get(base_name, 0) + 1
        used_names[base_name] = count
        file_stem = base_name if count == 1 else f"{base_name}_{count}"
        output_file = destination_dir / f"{file_stem}.md"
        output_file.write_text(content + "\n", encoding="utf-8")

    return len(sections)


def rebuild_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def iter_source_files(source_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in source_dir.glob("*.md")
        if path.is_file() and path.name not in EXCLUDED_FILES
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split Markdown notes into per-file directories and per-H3 Markdown files."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=SOURCE_DIR,
        help=f"Directory containing source Markdown files. Default: {SOURCE_DIR}",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Directory to recreate and populate. Default: {OUTPUT_DIR}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_dir = args.source_dir.expanduser().resolve()
    output_dir = args.output_dir

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source_dir}")

    rebuild_output_dir(output_dir)

    total_files = 0
    total_sections = 0
    for source_file in iter_source_files(source_dir):
        total_files += 1
        total_sections += write_sections(source_file, output_dir)

    print(
        f"Processed {total_files} Markdown files into {output_dir.resolve()} "
        f"with {total_sections} H3 sections."
    )


if __name__ == "__main__":
    main()
