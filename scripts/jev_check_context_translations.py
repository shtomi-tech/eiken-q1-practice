"""Jevで文脈推測2文目の英日対応を点検する。"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from typesafe_sdk import AsyncTypeSafeClient, Noul

ROOT = Path(__file__).resolve().parent.parent


def load_items() -> list[dict]:
    manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))["q1"]
    rows: list[dict] = []
    for dataset_id, dataset in manifest.items():
        url = dataset.get("contextTranslationUrl")
        if not url:
            continue
        payload = json.loads((ROOT / url).read_text(encoding="utf-8"))
        contexts = json.loads((ROOT / dataset["contextUrl"]).read_text(encoding="utf-8"))["contexts"]
        for index, item in enumerate(payload["items"]):
            rows.append({"datasetId": dataset_id, "context": " ".join(contexts[index]["fullEnglish"]), **item})
    return rows


QUESTIONS = {
    "accurate": Noul(
        instructions=(
            "`japanese` is a natural and accurate Japanese translation of `english` in `context`. "
            "It preserves the subject, action, objects, negation, quantities, tense, and logical relationships."
        )
    ),
    "has_error": Noul(
        instructions=(
            "`japanese` contains a mistranslation, omitted important detail, added unsupported claim, "
            "wrong referent, or contradiction compared with `english` in `context`."
        )
    ),
}


async def check(client: AsyncTypeSafeClient, item: dict, sem: asyncio.Semaphore) -> dict:
    state = {
        "english": item["english"],
        "japanese": item["japanese"],
        "context": item.get("context", ""),
    }
    async with sem:
        response = await client.system_one(state=state, questions=QUESTIONS)
    return {
        **item,
        "accurate": round(response.nouls["accurate"].noul, 3),
        "has_error": round(response.nouls["has_error"].noul, 3),
    }


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int)
    parser.add_argument("--concurrency", type=int, default=12)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    if not os.environ.get("TYPESAFE_API_KEY"):
        raise SystemExit("TYPESAFE_API_KEY が設定されていません。")

    items = load_items()
    if args.sample:
        step = max(1, len(items) // args.sample)
        items = items[::step][: args.sample]
    sem = asyncio.Semaphore(args.concurrency)
    async with AsyncTypeSafeClient() as client:
        results = await asyncio.gather(*(check(client, item, sem) for item in items))

    # 中間値は表現差や文脈補完でも出るため、明確な不一致だけを要確認に回す。
    flagged = [item for item in results if item["accurate"] < 0.5 or item["has_error"] > 0.7]
    output = ROOT / "out/jev-context-second-translations.json"
    output.write_text(
        json.dumps({"total": len(results), "flagged": len(flagged), "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Jev translation check: {len(results)}件中 {len(flagged)}件が要確認 -> {output}")
    if not args.quiet:
        for item in flagged:
            print(
                f"{item['datasetId']} Q{item['q']} {item['target']}: "
                f"accurate={item['accurate']} error={item['has_error']}\n"
                f"  EN: {item['english']}\n  JA: {item['japanese']}"
            )


if __name__ == "__main__":
    asyncio.run(main())
