---
name: telegram-linen-writeoff-report
description: Build Russian linen writeoff reports from Telegram Desktop chat exports and present the final report directly in the Codex chat window by default. Use when Codex needs to read Telegram `messages.html`, filter a date range, count linen categories by object, normalize free-form Russian inventory messages, map legs/feet wording to НП, keep МП separate, create a "Без объекта" bucket, and list ambiguous or disputed message interpretations.
---

# Telegram Linen Writeoff Report

## Overview

Create linen writeoff reports from Telegram Desktop export files. The expected source is `messages.html`; the expected report groups counts by object with these rows: `БП`, `СП`, `НП`, `МП`, `Пододеяльник`, `Простынь`, `Наволочка`.

## Workflow

1. Locate the Telegram export folder and confirm `messages.html` exists.
2. Parse messages with `scripts/parse_telegram_export.py` if you need a readable intermediate message list.
3. Build the report with `scripts/build_linen_report.py`, passing the inclusive start and end dates.
4. Return the final report directly in the Codex chat window unless the user explicitly asks for a file.
5. Read `references/linen_rules.md` before changing counting behavior.
6. Read `references/object_aliases.md` before adding or changing object normalization.
7. Include a final "Спорные или непонятные места" section. Do not hide assumptions.

## Quick Start

Use the bundled report builder:

```bash
python scripts/build_linen_report.py "C:\path\to\ChatExport\messages.html" --start 2025-10-29 --end 2026-05-14
```

Omit `--output` for the normal workflow so the report prints to stdout and can be pasted directly into the Codex response. Use `--output report.md` only when the user asks for a file. Use `--evidence evidence.csv` only when you need an audit trail for checking counts.

If Python is not on PATH, use the Python executable available in the current environment.

To inspect extracted messages first:

```bash
python scripts/parse_telegram_export.py "C:\path\to\ChatExport\messages.html" --start 2025-10-29 --end 2026-05-14 --output messages.json
```

## Counting Rules

- Count only the requested period, inclusive of start and end dates.
- Count only the report categories: `БП`, `СП`, `НП`, `МП`, `Пододеяльник`, `Простынь`, `Наволочка`.
- Map `ноги`, `ножки`, `лапки`, and `для ног` to `НП`.
- Keep `МП` as its own row.
- Put item counts without a recoverable object into `Без объекта`.
- Treat short joined messages as a continuation only when they are close in time to a previous object from the same sender.
- Do not count discussion messages unless they introduce a new quantity.
- When a later "итого" message summarizes preceding detail, count the "итого" quantity and avoid double-counting the earlier descriptive line.

See `references/linen_rules.md` for the full rule set and ambiguity policy.

## Object Normalization

Normalize common aliases before reporting. Examples:

- `Общий фонд`, `общ фонд` -> `ОФ`
- `Югозапад`, `Юго запад` -> `Юго-Запад`
- `Юмашева` -> `Юмашева 6`
- `Хохрякова 63 -46` -> `Хохрякова 63`

See `references/object_aliases.md` for current aliases.

## Resources

- `scripts/parse_telegram_export.py`: extracts message id, date, author, text, and joined status from Telegram `messages.html`.
- `scripts/build_linen_report.py`: builds the object-by-object linen writeoff report and optional evidence CSV.
- `references/linen_rules.md`: counting and ambiguity rules.
- `references/object_aliases.md`: object alias list and normalization guidance.
- `references/examples.md`: example messages and expected interpretations.
- `references/verification.md`: known verification command and expected result for the 2026-05-15 export used to create this skill.

## Output Shape

Use this shape directly in the chat answer unless the user asks for a table or file:

```text
Объект:
БП-0
СП-0
НП-0
МП-0
Пододеяльник-0
Простынь-0
Наволочка-0
```

End with totals when useful, then "Спорные или непонятные места".
