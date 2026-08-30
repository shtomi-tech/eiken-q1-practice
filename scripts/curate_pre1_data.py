"""準1級Q1の既存生成JSONへ共通メタデータを適用する。"""

from __future__ import annotations

from q1_pre1_metadata import ROUND_IDS, apply_round


def main() -> None:
    for round_id in ROUND_IDS:
        apply_round(round_id)
        print(f"{round_id}: 準1級Q1メタデータ・設問文訳を適用")


if __name__ == "__main__":
    main()
