#!/usr/bin/env python3
"""Build a linen writeoff report from Telegram messages.html."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from parse_telegram_export import Message, filter_messages, parse_messages  # noqa: E402


CATEGORIES = ["БП", "СП", "НП", "МП", "Пододеяльник", "Простынь", "Наволочка"]
CONTEXT_WINDOW = timedelta(minutes=45)
SUMMARY_WINDOW = timedelta(minutes=30)


OBJECT_PATTERNS: list[tuple[str, str]] = [
    (r"\bбелинского\s*30\b", "Белинского 30"),
    (r"\bбелинского\s*86\b", "Белинского 86"),
    (r"\bмалышева\s*42\s*а?\b", "Малышева 42а"),
    (r"\bстуденческая\s*80\b", "Студенческая 80"),
    (r"\bхохрякова\s*63(?:\s*-\s*46)?\b", "Хохрякова 63"),
    (r"\bавтовокзал\w*\b", "Автовокзал"),
    (r"\bботаник\w*\b", "Ботаника"),
    (r"\bбажовск\w*\b", "Бажовский"),
    (r"\bрадиус\w*\b", "Радиус"),
    (r"\bартек\w*\b", "Артек"),
    (r"\bазин\w*\b", "Азина"),
    (r"\bмалевич\w*\b", "Малевич"),
    (r"\bгорьк\w*\b", "Горького"),
    (r"\bэверест\w*\b", "Эверест"),
    (r"\bэврик\w*\b", "Эврика"),
    (r"\bуралмаш\w*\b", "Уралмаш"),
    (r"\bмашинист\w*\b", "Машинистов"),
    (r"\bтринити\w*\b", "Тринити"),
    (r"\bюго\s*-?\s*запад\w*\b|\bюгозапад\w*\b", "Юго-Запад"),
    (r"\bюмашев\w*(?:\s*6)?\b", "Юмашева 6"),
    (r"\bобщ(?:ий)?\s+фонд\b|\bобщ\s+фонд\b|\bоф\b", "ОФ"),
]


REJECT_MARKERS = [
    "доброе утро",
    "пока не спис",
    "на списание много",
    "не новая",
    "надеюсь",
    "почти новая",
    "не хватает",
    "стелить",
    "ничего не понимаю",
    "обратное",
]


WORD_NUMBERS = {
    "один": 1,
    "одна": 1,
    "одно": 1,
    "два": 2,
    "две": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
}


@dataclass
class Evidence:
    message_id: str
    dt: str
    object: str
    category: str
    quantity: int
    text: str
    note: str
    weak: bool = False
    applied: bool = True


def norm(text: str) -> str:
    text = text.lower().replace("ё", "е")
    text = re.sub(r"[«»\"']", " ", text)
    return text


def find_object(text: str) -> str | None:
    lowered = norm(text)
    for pattern, canonical in OBJECT_PATTERNS:
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            return canonical
    return None


def object_spans(text: str) -> list[tuple[int, int]]:
    lowered = norm(text)
    spans = []
    for pattern, _canonical in OBJECT_PATTERNS:
        for match in re.finditer(pattern, lowered, flags=re.IGNORECASE):
            spans.append(match.span())
    return spans


def overlaps(span: tuple[int, int], spans: list[tuple[int, int]]) -> bool:
    start, end = span
    return any(start < other_end and end > other_start for other_start, other_end in spans)


def is_rejected(text: str) -> bool:
    lowered = norm(text)
    if lowered.strip().startswith("на пододеяльник"):
        return True
    return any(marker in lowered for marker in REJECT_MARKERS)


def add_match_counts(
    counts: dict[str, int],
    text: str,
    category: str,
    patterns: list[str],
) -> None:
    lowered = norm(text)
    spans: list[tuple[int, int]] = []
    for pattern in patterns:
        for match in re.finditer(pattern, lowered, flags=re.IGNORECASE):
            qty = int(match.group("qty")) if match.groupdict().get("qty") else 1
            counts[category] += qty
            spans.append(match.span())


def parse_category_counts(text: str, object_explicit: bool) -> tuple[dict[str, int], set[str]]:
    lowered = norm(text)
    object_number_spans = object_spans(text)
    counts: dict[str, int] = defaultdict(int)
    numbered: set[str] = set()

    patterns: list[tuple[str, str]] = [
        ("БП", r"(?P<qty>\d+)[ \t]*(?:б\s*\.?\s*пол\.?|бп\b|б\s+пол\b|больш\w*\s+полотенц\w*|полотенц\w*\s+больш\w*)"),
        ("СП", r"(?P<qty>\d+)[ \t]*(?:сп\b|с\s*\.?\s*пол\.?|средн\w*\s+полотенц\w*)"),
        ("НП", r"(?P<qty>\d+)[ \t]*(?:нп\b|ног\w*|ножк\w*|лапк\w*|для\s+ног)"),
        ("МП", r"(?P<qty>\d+)[ \t]*(?:м\s*\.?\s*пол\.?|мп\b|м\s+пол\b|мал\w*\s+полотенц\w*|полотенц\w*\s+для\s+лица|п\s*\.?\s*мал\.?)"),
        ("Пододеяльник", r"(?P<qty>\d+)[ \t]*(?:под\s*одеяльник\w*|пододеяльник\w*|подод\b)"),
        ("Простынь", r"(?P<qty>\d+)[ \t]*(?:простын\w*)"),
        ("Наволочка", r"(?P<qty>\d+)[ \t]*(?:наволочк\w*)"),
        ("Пододеяльник", r"(?:под\s*одеяльник\w*|пододеяльник\w*|подод\b)[ \t-]*(?P<qty>\d+)"),
        ("Простынь", r"(?:простын\w*)[ \t-]*(?P<qty>\d+)"),
        ("Наволочка", r"(?:наволочк\w*)[ \t-]*(?P<qty>\d+)"),
        ("БП", r"(?:бп\b)[ \t-]*(?P<qty>\d+)"),
        ("СП", r"(?:сп\b)[ \t-]*(?P<qty>\d+)"),
        ("НП", r"(?:нп\b)[ \t-]*(?P<qty>\d+)"),
        ("МП", r"(?:мп\b)[ \t-]*(?P<qty>\d+)"),
    ]

    for category, pattern in patterns:
        for match in re.finditer(pattern, lowered, flags=re.IGNORECASE):
            if overlaps(match.span("qty"), object_number_spans):
                continue
            qty = int(match.group("qty"))
            counts[category] += qty
            numbered.add(category)

    if re.search(r"\bпол\s+под\s*одеяльник\w*|\bпол\s+пододеяльник\w*", lowered):
        counts["Пододеяльник"] += 1
        numbered.add("Пододеяльник")

    # Word-number summaries, mostly for "Итого две простыни".
    for word, qty in WORD_NUMBERS.items():
        if re.search(rf"\b{word}\s+простын\w*", lowered):
            counts["Простынь"] += qty
            numbered.add("Простынь")
        if re.search(rf"\b{word}\s+пододеяльник\w*", lowered):
            counts["Пододеяльник"] += qty
            numbered.add("Пододеяльник")
        if re.search(rf"\b{word}\s+наволочк\w*", lowered):
            counts["Наволочка"] += qty
            numbered.add("Наволочка")

    # Count clear item mentions without explicit quantity as 1.
    # Do this only when an object is explicit or the category is an abbreviated item-only message.
    no_qty_patterns = [
        ("БП", r"\bбп\b|б\s*\.?\s*пол\.?|больш\w*\s+полотенц\w*|полотенц\w*\s+больш\w*"),
        ("СП", r"\bсп\b|средн\w*\s+полотенц\w*"),
        ("НП", r"\bнп\b|ног\w*|ножк\w*|лапк\w*|для\s+ног"),
        ("МП", r"\bмп\b|м\s*\.?\s*пол\.?|полотенц\w*\s+для\s+лица|п\s*\.?\s*мал\.?"),
        ("Пододеяльник", r"под\s*одеяльник\w*|пододеяльник\w*|подод\b"),
        ("Простынь", r"простын\w*"),
        ("Наволочка", r"наволочк\w*"),
    ]
    item_only = bool(re.fullmatch(r"\s*(бп|сп|нп|мп)\s*", lowered))
    for category, pattern in no_qty_patterns:
        if category in numbered:
            continue
        if re.search(pattern, lowered) and (object_explicit or item_only):
            # Avoid adding no-quantity mentions when the text is clearly about a numbered address.
            counts[category] += 1

    return dict(counts), numbered


def is_short_item_only(text: str) -> bool:
    lowered = norm(text).strip()
    return bool(
        re.fullmatch(
            r"(?:\d+\s*)?(?:бп|сп|нп|мп|б\s*\.?\s*пол\.?|м\s*\.?\s*пол\.?|ног\w*|ножк\w*|лапк\w*|для\s+ног|простын\w*|наволочк\w*|под\s*одеяльник\w*|пододеяльник\w*|подод)",
            lowered,
        )
    )


def is_caption_duplicate(messages: list[Message], index: int, category_counts: dict[str, int]) -> bool:
    if not category_counts or not is_short_item_only(messages[index].text):
        return False
    current_dt = datetime.fromisoformat(messages[index].dt)
    current_author = messages[index].author
    for next_message in messages[index + 1 : index + 3]:
        next_dt = datetime.fromisoformat(next_message.dt)
        if next_dt - current_dt > timedelta(minutes=2):
            return False
        if next_message.author != current_author:
            continue
        if not find_object(next_message.text):
            continue
        next_counts, _ = parse_category_counts(next_message.text, object_explicit=True)
        if all(next_counts.get(category, 0) >= quantity for category, quantity in category_counts.items()):
            return True
    return False


def report_note(text: str, object_explicit: bool, object_name: str, used_context: bool) -> str:
    lowered = norm(text)
    notes = []
    if not object_explicit and object_name == "Без объекта":
        notes.append("объект не указан")
    if used_context:
        notes.append("объект взят из близкого предыдущего сообщения")
    if re.search(r"ног\w*|ножк\w*|лапк\w*|для\s+ног", lowered):
        notes.append("ноги/ножки/лапки/для ног -> НП")
    if re.search(r"б\s*\.?\s*пол|больш\w*\s+полотенц|полотенц\w*\s+больш", lowered):
        notes.append("большое полотенце -> БП")
    if re.search(r"средн\w*\s+полотенц", lowered):
        notes.append("среднее полотенце -> СП")
    if re.search(r"полотенц\w*\s+для\s+лица|п\s*\.?\s*мал", lowered):
        notes.append("малое/для лица -> МП")
    if "итого" in lowered:
        notes.append("итого принято как сводная запись")
    if "кузнецова" in lowered:
        notes.append("Кузнецова 21 может быть отдельным объектом")
    if "простынь простынь" in lowered:
        notes.append("повтор слова простынь посчитан один раз")
    if re.search(r"\bпол\s+под", lowered):
        notes.append("пол пододеяльника принято как 1 пододеяльник")
    return "; ".join(notes)


def build_report(messages: list[Message], start: date, end: date) -> tuple[str, list[Evidence]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {category: 0 for category in CATEGORIES})
    evidence: list[Evidence] = []
    last_object_by_author: dict[str, tuple[str, datetime]] = {}
    pending_weak: list[Evidence] = []

    for index, message in enumerate(messages):
        dt = datetime.fromisoformat(message.dt)
        if is_rejected(message.text):
            continue

        explicit_object = find_object(message.text)
        object_name = explicit_object
        used_context = False
        if not object_name:
            previous = last_object_by_author.get(message.author)
            if previous and dt - previous[1] <= CONTEXT_WINDOW:
                object_name = previous[0]
                used_context = True
        if not object_name:
            object_name = "Без объекта"

        category_counts, numbered = parse_category_counts(message.text, object_explicit=explicit_object is not None)
        if not category_counts:
            if explicit_object:
                last_object_by_author[message.author] = (explicit_object, dt)
            continue

        if explicit_object is None and object_name == "Без объекта" and is_caption_duplicate(messages, index, category_counts):
            for category, quantity in category_counts.items():
                evidence.append(
                    Evidence(
                        message.id,
                        message.dt,
                        object_name,
                        category,
                        quantity,
                        message.text,
                        "не учтено: короткая подпись к фото продублирована следующим сообщением с объектом",
                        weak=True,
                        applied=False,
                    )
                )
            continue

        if explicit_object:
            last_object_by_author[message.author] = (explicit_object, dt)

        is_summary = "итого" in norm(message.text)
        if is_summary:
            for pending in pending_weak:
                pending_dt = datetime.fromisoformat(pending.dt)
                if (
                    pending.applied
                    and pending.object == object_name
                    and pending.category in category_counts
                    and dt - pending_dt <= SUMMARY_WINDOW
                ):
                    counts[pending.object][pending.category] -= pending.quantity
                    pending.applied = False
                    pending.note = (pending.note + "; снято из-за последующей строки итого").strip("; ")

        for category, quantity in category_counts.items():
            weak = category not in numbered
            note = report_note(message.text, explicit_object is not None, object_name, used_context)
            if weak:
                note = (note + "; количество не указано, принято 1").strip("; ")
            item = Evidence(message.id, message.dt, object_name, category, quantity, message.text, note, weak=weak)
            evidence.append(item)
            if weak:
                pending_weak.append(item)
            counts[object_name][category] += quantity

    objects = sorted(counts, key=lambda value: value.lower())
    lines = [
        "Отчет по выводу белья",
        f"Период: {start.strftime('%d.%m.%Y')}-{end.strftime('%d.%m.%Y')}",
        "Источник: messages.html",
        "",
    ]

    for object_name in objects:
        lines.append(f"{object_name}:")
        for category in CATEGORIES:
            lines.append(f"{category}-{counts[object_name][category]}")
        lines.append("")

    totals = {category: 0 for category in CATEGORIES}
    for object_counts in counts.values():
        for category in CATEGORIES:
            totals[category] += object_counts[category]

    lines.append("Итого по всем объектам:")
    for category in CATEGORIES:
        lines.append(f"{category}-{totals[category]}")
    lines.append("")

    notes = []
    for item in evidence:
        if item.note and item.applied:
            notes.append(f"- {item.dt[:16]} {item.message_id}: {item.note}; «{item.text.replace(chr(10), ' / ')}»")
        elif item.note and not item.applied:
            notes.append(f"- {item.dt[:16]} {item.message_id}: {item.note}; «{item.text.replace(chr(10), ' / ')}»")
    if notes:
        lines.append("Спорные или непонятные места:")
        lines.extend(dict.fromkeys(notes))

    return "\n".join(lines).rstrip() + "\n", evidence


def write_evidence(path: str | Path, evidence: list[Evidence]) -> None:
    with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["applied", "message_id", "dt", "object", "category", "quantity", "note", "text"],
        )
        writer.writeheader()
        for item in evidence:
            writer.writerow(
                {
                    "applied": "yes" if item.applied else "no",
                    "message_id": item.message_id,
                    "dt": item.dt,
                    "object": item.object,
                    "category": item.category,
                    "quantity": item.quantity,
                    "note": item.note,
                    "text": item.text.replace("\n", " / "),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a linen writeoff report from Telegram messages.html.")
    parser.add_argument("messages_html", help="Path to Telegram messages.html")
    parser.add_argument("--start", required=True, help="Inclusive start date, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="Inclusive end date, YYYY-MM-DD")
    parser.add_argument("--output", help="Output Markdown path. Prints to stdout when omitted.")
    parser.add_argument("--evidence", help="Optional CSV with each counted message.")
    args = parser.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    messages = filter_messages(parse_messages(args.messages_html), start, end)
    report, evidence = build_report(messages, start, end)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    if args.evidence:
        write_evidence(args.evidence, evidence)


if __name__ == "__main__":
    main()
