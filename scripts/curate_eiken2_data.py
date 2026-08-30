"""英検2級Q1の既存データへ共通メタデータと例文補正を再適用する。"""

from __future__ import annotations

from q1_eiken2_metadata import ROUND_IDS, apply_round


def main() -> int:
    for round_id in ROUND_IDS:
        apply_round(round_id)
        print(f"{round_id}: 英検2級Q1の整備を適用しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
