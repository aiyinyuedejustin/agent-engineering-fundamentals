"""Locate the book's published original lab without copying its implementation."""
from pathlib import Path
import importlib.util
import os
import sys


def load_loop_lab():
    explicit = os.environ.get("BOOK_PUBLICATION")
    roots = [Path(explicit)] if explicit else []
    if not explicit:
        for parent in Path(__file__).resolve().parents:
            roots.extend((parent, parent / "publication"))
    for root in roots:
        path = root / "04-Extracted-Core-Code-And-Scripts/core-code-lab/loop-cowork/model.py"
        if path.is_file():
            name = "book_original_loop_lab"
            if name in sys.modules:
                return sys.modules[name]
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            return module
    raise FileNotFoundError("Set BOOK_PUBLICATION to the book root containing 04-Extracted-Core-Code-And-Scripts")
