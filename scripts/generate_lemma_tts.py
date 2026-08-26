"""Generate one Azure Speech MP3 for each learning lemma entry."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from generate_tts_1 import DEFAULT_VOICE, request_audio


ROOT = Path(__file__).resolve().parents[1]
LEMMA_PATH = ROOT / "data" / "lemmas.json"


def verify_audio_files(entries: dict[str, dict]) -> None:
    paths: dict[str, str] = {}
    missing: list[str] = []
    for lemma, entry in entries.items():
        audio_path = str(entry.get("audio", ""))
        if audio_path in paths:
            raise SystemExit(f"音声パスが衝突しています: {paths[audio_path]} / {lemma} -> {audio_path}")
        paths[audio_path] = lemma
        target = ROOT / audio_path
        if not target.is_file() or target.stat().st_size == 0:
            missing.append(lemma)
    if missing:
        raise SystemExit(f"原形MP3が不足しています: {len(missing)}/{len(entries)}件。先頭: {', '.join(missing[:5])}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice", default=os.environ.get("AZURE_SPEECH_VOICE", DEFAULT_VOICE))
    parser.add_argument("--limit", type=int, help="先頭から指定件数だけ処理する")
    parser.add_argument("--force", action="store_true", help="既存音声を上書きする")
    parser.add_argument("--dry-run", action="store_true", help="Azureへ送信せず対象だけ確認する")
    args = parser.parse_args()

    data = json.loads(LEMMA_PATH.read_text(encoding="utf-8"))
    entries = data.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise SystemExit("data/lemmas.json に entries がありません")
    jobs = sorted(entries.items())
    if args.limit:
        jobs = jobs[: args.limit]

    key = os.environ.get("AZURE_SPEECH_KEY", "").strip()
    region = os.environ.get("AZURE_SPEECH_REGION", "japaneast").strip()
    if not args.dry_run and not key:
        raise SystemExit(
            "AZURE_SPEECH_KEY が見つかりません。"
            "キーはチャットへ貼らず、実行するPowerShellに設定してください。"
        )

    generated = 0
    skipped = 0
    for lemma, entry in jobs:
        audio_path = entry.get("audio", "") if isinstance(entry, dict) else ""
        if not audio_path:
            raise SystemExit(f"{lemma}: audio パスがありません")
        target = ROOT / audio_path
        if target.exists() and not args.force:
            skipped += 1
            continue
        if args.dry_run:
            print(f"[dry-run] {lemma} -> {audio_path}")
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        audio = request_audio(key, region, lemma, args.voice)
        if not audio:
            raise SystemExit(f"{lemma}: Azure Speechが空の音声を返しました")
        temporary = target.with_suffix(".mp3.tmp")
        temporary.write_bytes(audio)
        temporary.replace(target)
        generated += 1
        print(f"生成: {lemma}")

    mode = "確認" if args.dry_run else "生成"
    if not args.dry_run:
        verify_audio_files(dict(jobs))
    print(f"{mode}対象 {len(jobs)}件 / 新規{generated}件 / 既存スキップ{skipped}件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
