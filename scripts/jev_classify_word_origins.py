#!/usr/bin/env python3
"""Use Jev to classify what kind of explanation each word-origin entry gives.

data/word_origins.json の各項目（derivation / parts / chain / note）を読み、
「どういう由来の説明になっているか」を1つの型に分類する。表示データは変更しない。
結果は参考分類で、確信度の低い項目は人の確認に回す。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
from collections import Counter
from pathlib import Path

from typesafe_sdk import AsyncTypeSafeClient, Choice

ROOT = Path(__file__).resolve().parents[1]
ORIGINS_PATH = ROOT / "data" / "word_origins.json"
CONCURRENCY = 6
# Choice の確信度がこれ未満なら「要確認」として報告する
LOW_CONFIDENCE = 0.5

CATEGORIES = {
    "affix_root": (
        "The explanation builds the meaning by combining prefixes, a root, and/or "
        "suffixes (e.g. 'retro- back + spect look -> retrospect'). The parts, not "
        "a story or image, carry the explanation."
    ),
    "concrete_image": (
        "The explanation starts from a concrete physical action, object, or scene "
        "and extends it figuratively to the present meaning (e.g. 'hanging over "
        "and about to cover -> imminent')."
    ),
    "semantic_shift": (
        "The explanation traces how an earlier meaning broadened, narrowed, "
        "weakened, or moved through several senses over time, without relying "
        "mainly on a vivid physical image or on affix analysis."
    ),
    "direct_borrowing": (
        "The word is explained as taken from another language (Latin, French, "
        "Greek, etc.) with essentially the same meaning; the explanation is mainly "
        "'from source word X meaning Y' with little change in sense."
    ),
    "proper_name": (
        "The word comes from a person, place, people, literary work, myth, or "
        "brand name."
    ),
    "compound_clipping": (
        "The word is explained as an English compound of two words, a shortening "
        "(clipping), or a blend of existing English words."
    ),
    "english_base_only": (
        "The note only points to an English base word it is inflected or derived "
        "from (often the same word, e.g. 'from English churn; inflected form of "
        "churn'), giving no further origin, image, or part-by-part meaning."
    ),
    "imitative": "The word is explained as imitating a sound or motion (onomatopoeia).",
    "uncertain": (
        "The explanation says the origin is unknown, disputed, or only probable, "
        "and does not commit to one account."
    ),
}

LABELS_JA = {
    "affix_root": "接辞・語根の組み立て",
    "concrete_image": "具体的イメージからの比喩",
    "semantic_shift": "意味の変遷",
    "direct_borrowing": "他言語からの借用（意味ほぼ同じ）",
    "proper_name": "固有名詞由来",
    "compound_clipping": "英語内の複合・短縮・混成",
    "english_base_only": "英語の原形・派生元を示すだけ",
    "imitative": "擬音・擬態",
    "uncertain": "由来不詳・諸説",
}

QUESTIONS = {
    "kind": Choice(
        instructions=(
            "`entry` is a Japanese flashcard note explaining the origin of the English "
            "word `word`, shown to Japanese learners to help them remember its meaning. "
            "Classify the main way this note explains the origin. Judge the note as "
            "written (`entry.derivation`, plus `entry.parts`, `entry.chain`, and "
            "`entry.note` when present); do not judge whether the etymology is "
            "historically correct. If several apply, choose the one that carries most "
            "of the explanation."
        ),
        criteria=CATEGORIES,
    ),
}


def entry_state(word: str, entry: dict) -> dict:
    kept = {k: entry[k] for k in ("derivation", "parts", "chain", "note") if k in entry}
    return {"word": word, "entry": kept}


async def classify(client: AsyncTypeSafeClient, word: str, entry: dict, sem: asyncio.Semaphore) -> dict:
    async with sem:
        res = await client.system_one(state=entry_state(word, entry), questions=QUESTIONS)
    kind = res.choices["kind"]
    return {
        "word": word,
        "dataType": entry.get("type"),
        "hasChain": "chain" in entry,
        "kind": kind.choice,
        "kindJa": LABELS_JA.get(kind.choice, kind.choice),
        "confidence": round(kind.confidence, 3),
        "probabilities": {k: round(v, 3) for k, v in sorted(kind.probabilities.items(), key=lambda x: -x[1])},
        "derivation": entry.get("derivation", ""),
    }


async def main_async(args: argparse.Namespace) -> int:
    if not os.environ.get("TYPESAFE_API_KEY"):
        raise SystemExit("TYPESAFE_API_KEY が設定されていません。")
    origins = json.loads(ORIGINS_PATH.read_text(encoding="utf-8"))["origins"]
    items = sorted(origins.items())
    if args.sample:
        items = random.Random(args.seed).sample(items, min(args.sample, len(items)))

    out = args.output.resolve()
    if out.exists() and not args.overwrite:
        raise SystemExit(f"出力先がすでに存在します（上書きしません）: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)

    sem = asyncio.Semaphore(args.concurrency)
    async with AsyncTypeSafeClient() as client:
        tasks = [classify(client, w, e, sem) for w, e in items]
        results, errors = [], []
        for coro in asyncio.as_completed(tasks):
            try:
                results.append(await coro)
            except Exception as exc:  # 1件の失敗で全体を止めない
                errors.append(repr(exc))
            if len(results) % 200 == 0:
                print(f"  {len(results)}/{len(items)}", flush=True)

    results.sort(key=lambda r: r["word"])
    counts = Counter(r["kind"] for r in results)
    by_type = Counter((r["dataType"], r["kind"]) for r in results)
    low = [r["word"] for r in results if r["confidence"] < LOW_CONFIDENCE]
    summary = {
        "source": str(ORIGINS_PATH),
        "evaluationType": "heuristic_classification",
        "warning": "Jevの参考分類。語源の正誤は判定していません。",
        "total": len(results),
        "errors": errors,
        "counts": {LABELS_JA[k]: counts[k] for k in CATEGORIES},
        "countsByDataType": {f"{t}:{LABELS_JA[k]}": n for (t, k), n in sorted(by_type.items())},
        "lowConfidenceThreshold": LOW_CONFIDENCE,
        "lowConfidenceWords": low,
        "results": results,
    }
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("total", "counts")}, ensure_ascii=False, indent=2))
    print(f"要確認（確信度<{LOW_CONFIDENCE}）: {len(low)}件, エラー: {len(errors)}件 -> {out}")
    return 0 if not errors else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Jevで語源・なりたちの記載内容を分類します")
    p.add_argument("--output", type=Path, default=ROOT / "out" / "jev-word-origin-kinds.json")
    p.add_argument("--overwrite", action="store_true", help="既存の出力を上書きする")
    p.add_argument("--sample", type=int, default=None, help="無作為にN件だけ処理する")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--concurrency", type=int, default=CONCURRENCY)
    return asyncio.run(main_async(p.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
