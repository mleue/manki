import os
from pathlib import Path
import pytest


@pytest.fixture
def datadir():
    this_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    yield this_dir / "data"
