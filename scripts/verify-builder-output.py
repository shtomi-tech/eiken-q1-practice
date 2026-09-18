"""セット単位の生成スクリプトの出力が、基準コミットと作業ツリーで同一か検証する。

data/ の語彙JSONには生成後に別工程（IPA取得・原形登録など）で追記された項目があるため、
生成スクリプト単体では data/ を再現しない。そこでリファクタリングの前後比較として、
基準コミット（既定 HEAD）の scripts/ と作業ツリーの scripts/ を、同じ HEAD の data/ の上で
それぞれ実行し、書き出されたファイルがバイト一致（改行コードは正規化）するかを調べる。

一時 git worktree の中だけで実行し、作業ツリーの data/ には書き込まない。

  python scripts/verify-builder-output.py                  # 全対象
  python scripts/verify-builder-output.py mock_10 p2_mock  # 名前に含む対象のみ
  python scripts/verify-builder-output.py --base <commit>  # 基準の scripts/ を指定
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# 引数なしで data/ だけを書き換える、セット単位の生成スクリプト。
TARGET_GLOBS = [
    "build_q1_mock_*_data.py",
    "build_q1_eiken2_mock_*_data.py",
    "build_q1_p2_mock_*_data.py",
    "build_q1_iuhw_set_*_data.py",
]


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout


def targets(filters: list[str]) -> list[str]:
    names = sorted({p.name for g in TARGET_GLOBS for p in (ROOT / "scripts").glob(g)})
    return [n for n in names if not filters or any(f in n for f in filters)]


def run_builder(wt: Path, scripts: Path, name: str) -> dict[str, bytes] | str:
    """scripts/ を差し替えて name を実行し、変化した data/ ファイルの内容を返す。"""
    shutil.rmtree(wt / "scripts")
    shutil.copytree(scripts, wt / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    try:
        if not (wt / "scripts" / name).exists():
            return "スクリプトが存在しない"
        run = subprocess.run([sys.executable, str(wt / "scripts" / name)], cwd=wt,
                             capture_output=True, text=True, encoding="utf-8")
        if run.returncode != 0:
            return f"exit {run.returncode}: {run.stderr.strip()[-600:]}"
        changed = git("diff", "--ignore-cr-at-eol", "--name-only", "--", "data", cwd=wt).split()
        added = git("ls-files", "--others", "--exclude-standard", "--", "data", cwd=wt).split()
        return {p: (wt / p).read_bytes().replace(b"\r\n", b"\n") for p in sorted(changed + added)}
    finally:
        git("checkout", "--", "data", "scripts", cwd=wt)
        git("clean", "-fdq", "--", "data", "scripts", cwd=wt)


def main() -> int:
    args = sys.argv[1:]
    base = "HEAD"
    if "--base" in args:
        i = args.index("--base")
        base = args[i + 1]
        del args[i:i + 2]
    names = targets(args)
    if not names:
        print("対象スクリプトがありません", file=sys.stderr)
        return 2

    tmp = Path(tempfile.mkdtemp(prefix="verify-builder-"))
    wt, base_scripts = tmp / "wt", tmp / "base-scripts"
    git("-c", "core.autocrlf=false", "worktree", "add", "--detach", str(wt), "HEAD")
    failures: list[str] = []
    try:
        git("config", "core.autocrlf", "false", cwd=wt)
        git("checkout", "--", ".", cwd=wt)
        # 基準の scripts/ を展開しておく（HEAD 以外も指定できるように）。
        git("-c", "core.autocrlf=false", "worktree", "add", "--detach", str(tmp / "base"), base)
        shutil.copytree(tmp / "base" / "scripts", base_scripts,
                        ignore=shutil.ignore_patterns("__pycache__"))
        git("worktree", "remove", "--force", str(tmp / "base"))

        for name in names:
            before = run_builder(wt, base_scripts, name)
            after = run_builder(wt, ROOT / "scripts", name)
            if isinstance(before, str) or isinstance(after, str):
                failures.append(name)
                print(f"ERROR {name}: base={before if isinstance(before, str) else 'ok'}"
                      f" / work={after if isinstance(after, str) else 'ok'}")
            elif before != after:
                failures.append(name)
                diff = sorted(p for p in before.keys() | after.keys()
                              if before.get(p) != after.get(p))
                print(f"DIFF  {name}: {', '.join(diff)}")
            else:
                print(f"OK    {name} ({len(after)} files)")
    finally:
        git("worktree", "remove", "--force", str(wt))
        git("worktree", "prune")
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{len(names) - len(failures)}/{len(names)} 一致（基準: {base}）")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
