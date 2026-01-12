from __future__ import annotations

import json
from pathlib import Path
from typing import Any

def load_dso_catalog() -> dict[str, Any]:
    path = Path(__file__).parent / "data" / "no_dsos.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
