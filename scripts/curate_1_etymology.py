"""公式1級Q1の既存生成JSONへ共有語源説明を適用する。"""

from __future__ import annotations

import json
from pathlib import Path

from q1_official_etymology import ETYMOLOGY_BY_ROUND


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    applied = 0
    for round_id, etymologies in ETYMOLOGY_BY_ROUND.items():
        path = DATA_DIR / f"vocab_1_{round_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        seen: set[str] = set()
        for item in [*data.get("words", []), *data.get("idioms", [])]:
            surface = str(item.get("phrase") or item.get("word") or "").strip()
            if surface not in etymologies:
                raise ValueError(f"語源情報がありません: {path.name} / {surface}")
            item["etymology"] = etymologies[surface]
            seen.add(surface)
            applied += 1
        extra = set(etymologies) - seen
        if extra:
            raise ValueError(f"データにない語源情報があります: {path.name} / {sorted(extra)}")
        write_json(path, data)
        print(f"{path.name}: {len(seen)}件")
    print(f"適用した語源: {applied}件")


if __name__ == "__main__":
    main()
