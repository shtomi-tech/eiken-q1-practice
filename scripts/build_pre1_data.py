"""公式PDFから設問抽出に使う小さな共通ヘルパー。

1級Q1の生成器は、準1級用の生成器と同じ名前の処理を参照していたが、
このチェックアウトにはその補助モジュールが存在しなかった。PDFは公開物へ
含めず、ローカルの ``data/eiken_1`` に置いた入力だけを読み取る。
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path


_CHARACTER_MAP = str.maketrans(
    {
        "\u00a0": " ",
        # 既存の公式Q1 JSONと同じく、PDFの禁則用ハイフンは語中から除く。
        "\u00ad": "",
        "\u2010": "",
        "\u2011": "",
        "\u2012": "",
        "\u2013": "",
        "\u2014": "",
        "\u2212": "",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
)


def clean_text(value: str) -> str:
    """PDF抽出で混ざるUnicode表記と改行を教材用の空白へ正規化する。"""

    normalized = unicodedata.normalize("NFKC", str(value or ""))
    normalized = normalized.translate(_CHARACTER_MAP)
    return re.sub(r"\s+", " ", normalized).strip()


def page_texts(path: Path) -> list[str]:
    """PDFのページ順テキストを返す。pdfplumberを優先して段組みを崩さない。"""

    try:
        import pdfplumber
    except ImportError:
        pdfplumber = None

    if pdfplumber is not None:
        with pdfplumber.open(str(path)) as pdf:
            return [page.extract_text() or "" for page in pdf.pages]

    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise RuntimeError("PDF抽出には pdfplumber または pypdf が必要です") from error

    reader = PdfReader(str(path))
    return [page.extract_text() or "" for page in reader.pages]


def parse_numbered_blocks(text: str) -> list[tuple[int, str]]:
    """``(1)`` 形式の設問ブロックを番号順に切り出す。"""

    markers = list(re.finditer(r"(?m)^\s*\((\d{1,2})\)\s*", text))
    if not markers:
        markers = list(re.finditer(r"(?<![A-Za-z0-9])\((\d{1,2})\)\s*", text))

    blocks: list[tuple[int, str]] = []
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        blocks.append((int(marker.group(1)), text[marker.end() : end].strip()))
    return blocks


def parse_choices(block: str) -> tuple[str, list[str]]:
    """設問ブロックから空所前の本文と1〜4の選択肢を返す。"""

    markers = list(re.finditer(r"(?<![A-Za-z0-9])([1-4])(?=\s+)", block))
    for start_index, marker in enumerate(markers):
        expected = ["1", "2", "3", "4"]
        candidate = markers[start_index : start_index + 4]
        if len(candidate) != 4 or [item.group(1) for item in candidate] != expected:
            continue

        stem = clean_text(block[: marker.start()])
        choices = []
        for index, choice_marker in enumerate(candidate):
            end = (
                candidate[index + 1].start()
                if index + 1 < len(candidate)
                else len(block)
            )
            choices.append(clean_text(block[choice_marker.end() : end]))
        return stem, choices

    raise ValueError(f"4択の番号列を抽出できません: {block[:120]!r}")


def answer_key(path: Path) -> dict[int, int]:
    """解答PDFの``(設問番号) 正答番号``を0始まりへ変換する。"""

    text = "\n".join(page_texts(path))
    return {
        int(number): int(choice) - 1
        for number, choice in re.findall(r"\((\d{1,2})\)\s*([1-4])", text)
    }
