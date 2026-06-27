"""doc_reader — read a named document from a documents directory."""

import os


def read_doc(base_dir, name):
    """Return the text contents of the document `name` located in `base_dir`.

    Args:
        base_dir: Path to the directory containing documents.
        name: Filename of the document to read.

    Returns:
        The file's contents as a string.

    Raises:
        ValueError: If `name` attempts to traverse outside `base_dir`.
        FileNotFoundError: If the document does not exist.
        PermissionError: If the document cannot be read.
    """
    base = os.path.realpath(base_dir)
    target = os.path.realpath(os.path.join(base_dir, name))
    if not target.startswith(base + os.sep) and target != base:
        raise ValueError(
            f"Document name {name!r} escapes base directory: {base_dir!r}"
        )
    with open(target) as f:
        return f.read()
