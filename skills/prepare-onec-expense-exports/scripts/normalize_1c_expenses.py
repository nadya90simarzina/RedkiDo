#!/usr/bin/env python3
"""Normalize CSV exports from 1C for apartment margin reports.

Input: CSV exported from 1C, preferably with columns such as date, account,
counterparty, contract, expense item, apartment/object/department, amount, and
comment. Output: normalized rows, summary by apartment, and a data-quality report.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

FIELDS = [
    "source_row",
    "date",
    "apartment",
    "expense_category",
    "amount",
    "attribution_type",
    "allocation_base",
    "account_debit",
    "account_credit",
    "counterparty",
    "contract",
    "expense_item",
    "document",
    "description",
    "needs_review",
    "notes",
]

ALIASES = {
    "date": ["дата", "период"],
    "account_debit": ["счет дт", "дебет", "дт"],
    "account_credit": ["счет кт", "кредит", "кт"],
    "counterparty": ["контрагент", "поставщик", "арендодатель"],
    "contract": ["договор"],
    "expense_item": ["статья затрат", "статья расходов", "вид расхода"],
    "apartment": ["адрес", "квартира", "объект", "помещение"],
    "division": ["подразделение"],
    "document": ["документ", "регистратор", "документ-регистратор"],
    "description": ["содержание", "операция", "назначение", "комментарий"],
    "amount": ["сумма", "оборот", "расход", "затраты", "стоимость"],
}

CLASSIFIERS = [
    ("Аренда", ["аренд", "собственник"], "direct", ""),
    ("Коммунальные услуги", ["коммун", "жкх", "электро", "водоснаб", "отоплен"], "direct", "apartment_months"),
    ("Интернет и связь", ["интернет", "домофон", "связь", "тв"], "direct", "apartment_months"),
    ("Ремонт и улучшения", ["ремонт", "мебел", "техник", "замок", "мастер", "матрас"], "direct", ""),
    ("Уборка", ["уборк", "клининг", "горнич"], "direct", "cleanings"),
    ("Стирка и прачечная", ["стирк", "прач", "химчист"], "allocated", "bookings_or_cleanings"),
    ("Расходники", ["бумаг", "сахар", "чай", "кофе", "мыло", "химия", "расходник"], "allocated", "bookings_or_nights"),
    ("Белье и текстиль", ["бель", "полотен", "простын", "наволоч", "текстил"], "allocated", "cleanings_or_beds"),
    ("Зарплата персонала", ["зарплат", "зп", "оклад", "сотрудник", "персонал", "администратор"], "allocated", "revenue_or_bookings"),
    ("Комиссии", ["комисс", "эквайр", "банк", "авито", "суточно", "островок"], "direct", "revenue"),
]

ADDRESS_RE = re.compile(r"((?:ул\.?|улица|проспект|пр-кт|пер\.?|шоссе|наб\.?)\s+[^,;|]{2,80}\d[^,;|]*)", re.I)


def norm(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("ё", "е").replace("Ё", "Е").replace("\u00a0", " ").lower()
    return re.sub(r"\s+", " ", text).strip()


def parse_amount(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    text = str(value).strip().replace("\u00a0", " ")
    if not text:
        return None
    negative = text.startswith("(") and text.endswith(")") or text.endswith("-")
    text = text.strip("()").rstrip("-")
    text = re.sub(r"(руб\.?|₽)", "", text, flags=re.I).replace(" ", "")
    text = re.sub(r"[^0-9,.-]", "", text).replace(",", ".")
    try:
        amount = Decimal(text)
    except InvalidOperation:
        return None
    return -amount if negative else amount


def read_csv(path: Path) -> list[list[str]]:
    for encoding in ("utf-8-sig", "cp1251", "utf-8"):
        try:
            text = path.read_text(encoding=encoding)
            try:
                dialect = csv.Sniffer().sniff(text[:4096], delimiters=";\t,")
            except csv.Error:
                dialect = csv.excel
                dialect.delimiter = ";"
            return list(csv.reader(text.splitlines(), dialect))
        except UnicodeDecodeError:
            continue
    raise SystemExit("Cannot read CSV encoding")


def detect_header(rows: list[list[str]]) -> int:
    best_i, best_score = 0, -1
    for i, row in enumerate(rows[:30]):
        joined = " | ".join(norm(c) for c in row)
        score = sum(any(alias in joined for alias in aliases) for aliases in ALIASES.values())
        if score > best_score:
            best_i, best_score = i, score
    return best_i


def map_columns(headers: list[str]) -> dict[str, int]:
    mapping = {}
    for field, aliases in ALIASES.items():
        for i, header in enumerate(headers):
            if any(alias in norm(header) for alias in aliases):
                mapping[field] = i
                break
    return mapping


def value(row: list[str], mapping: dict[str, int], key: str) -> str:
    i = mapping.get(key)
    return "" if i is None or i >= len(row) else str(row[i]).strip()


def is_total(row: list[str]) -> bool:
    joined = " ".join(norm(c) for c in row[:4] if str(c).strip())
    return not joined or any(mark in joined for mark in ["итого", "общий итог", "сальдо", "оборот за"])


def read_addresses(path: Path | None) -> list[str]:
    if not path:
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def detect_apartment(row: list[str], mapping: dict[str, int], known: list[str]) -> tuple[str, str]:
    joined = " | ".join(row)
    normalized = norm(joined)
    for address in known:
        if norm(address) in normalized:
            return address, "known address"
    for key in ["apartment", "division"]:
        candidate = value(row, mapping, key)
        if candidate and "общ" not in norm(candidate) and "итого" not in norm(candidate):
            return candidate, f"from {key}"
    contract = value(row, mapping, "contract")
    if contract and any(ch.isdigit() for ch in contract) and "общ" not in norm(contract):
        return contract, "from contract"
    match = ADDRESS_RE.search(joined)
    if match:
        return match.group(1).strip(), "from text"
    return "", "not found"


def classify(row: list[str], mapping: dict[str, int], has_apartment: bool) -> tuple[str, str, str, str]:
    text = norm(" | ".join([value(row, mapping, k) for k in ["expense_item", "counterparty", "contract", "document", "description"]] + row))
    for category, needles, default_type, base in CLASSIFIERS:
        if any(needle in text for needle in needles):
            if default_type == "direct" and not has_apartment:
                return category, "needs_review", base, "usually direct, but apartment was not found"
            return category, default_type, base, ""
    return "Прочее / требует классификации", "direct" if has_apartment else "needs_review", "", "unknown category"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("out"))
    parser.add_argument("--addresses", type=Path)
    args = parser.parse_args()

    rows = read_csv(args.input)
    header_i = detect_header(rows)
    headers = rows[header_i]
    mapping = map_columns(headers)
    known = read_addresses(args.addresses)
    out_rows: list[dict[str, str]] = []
    skipped_totals = skipped_no_amount = 0

    for source_row, row in enumerate(rows[header_i + 1 :], start=header_i + 2):
        if is_total(row):
            skipped_totals += 1
            continue
        amount = parse_amount(value(row, mapping, "amount"))
        if amount is None:
            numbers = [parse_amount(c) for c in row]
            numbers = [n for n in numbers if n is not None]
            amount = numbers[-1] if numbers else None
        if amount is None:
            skipped_no_amount += 1
            continue
        apartment, apartment_note = detect_apartment(row, mapping, known)
        category, attribution, base, note = classify(row, mapping, bool(apartment))
        out_rows.append({
            "source_row": str(source_row),
            "date": value(row, mapping, "date"),
            "apartment": apartment,
            "expense_category": category,
            "amount": f"{amount.quantize(Decimal('0.01'))}",
            "attribution_type": attribution,
            "allocation_base": base,
            "account_debit": value(row, mapping, "account_debit"),
            "account_credit": value(row, mapping, "account_credit"),
            "counterparty": value(row, mapping, "counterparty"),
            "contract": value(row, mapping, "contract"),
            "expense_item": value(row, mapping, "expense_item"),
            "document": value(row, mapping, "document"),
            "description": value(row, mapping, "description") or " | ".join(row),
            "needs_review": "yes" if attribution == "needs_review" or not apartment else "no",
            "notes": "; ".join(x for x in [apartment_note if not apartment else "", note] if x),
        })

    summary = defaultdict(Decimal)
    for row in out_rows:
        key = (row["apartment"] or "[без квартиры]", row["expense_category"], row["attribution_type"])
        summary[key] += Decimal(row["amount"])

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "normalized_expenses.csv", out_rows, FIELDS)
    write_csv(
        args.output_dir / "expense_summary_by_apartment.csv",
        [
            {"apartment": k[0], "expense_category": k[1], "attribution_type": k[2], "amount": f"{v.quantize(Decimal('0.01'))}"}
            for k, v in sorted(summary.items())
        ],
        ["apartment", "expense_category", "attribution_type", "amount"],
    )
    report = [
        f"Rows normalized: {len(out_rows)}",
        f"Rows without apartment: {sum(1 for r in out_rows if not r['apartment'])}",
        f"Rows marked for review: {sum(1 for r in out_rows if r['needs_review'] == 'yes')}",
        f"Skipped total/service rows: {skipped_totals}",
        f"Skipped rows without amount: {skipped_no_amount}",
        "Shared costs must be shown as allocated if apartment-level accounting was not maintained.",
    ]
    (args.output_dir / "data_quality_report.txt").write_text("\n".join(report), encoding="utf-8")
    print(f"Normalized rows: {len(out_rows)}")
    print(f"Output directory: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
