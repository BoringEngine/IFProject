from pathlib import Path
from engine.parser import load_syntax

SYNTAX_FILE = Path("src/engine/syntax.yaml")


def test_load_syntax():
    syntax = load_syntax(SYNTAX_FILE)
