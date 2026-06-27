"""doc_reader — read named documents from a base directory."""

import os


def read_doc(base_dir, name):
    """Return the text contents of the document `name` located in `base_dir`.

    Args:
        base_dir: Path to the directory containing documents.
        name: Filename of the document to read.

    Returns:
        The file's text contents as a string.

    Raises:
        ValueError: If base_dir or name are not non-empty strings.
        FileNotFoundError: If the document does not exist in base_dir.
        OSError: If the file cannot be read.
    """
    # Barricade: validate external inputs before touching the filesystem.
    if not isinstance(base_dir, str) or not base_dir:
        raise ValueError(f"base_dir must be a non-empty string, got {base_dir!r}")
    if not isinstance(name, str) or not name:
        raise ValueError(f"name must be a non-empty string, got {name!r}")

    path = os.path.join(base_dir, name)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()
