# Verification Case

This skill was created from a Telegram export at:

```text
C:\Users\Серж\Desktop\ChatExport_2026-05-15\messages.html
```

Verification command:

```bash
python scripts/build_linen_report.py "C:\Users\Серж\Desktop\ChatExport_2026-05-15\messages.html" --start 2025-10-29 --end 2026-05-14
```

Normal delivery expectation: paste the generated report directly into the Codex chat window. Create a report file only when the user asks for one.

Expected manual totals from the seed dialogue:

```text
БП-44
СП-28
НП-18
МП-7
Пододеяльник-25
Простынь-33
Наволочка-30
```

Known manual ambiguity decisions:

- `30.10.2025`: `Артек` in one message and `2б.пол.,2м пол.,1 лапки,пол пододеяльника` in the next message belong together.
- `24.11.2025`: `1 Простынь` is a continuation for `Юмашева 6`; separate `Бп` before `Белинского 86 / 1 бп` is a duplicated photo caption and must not be counted under `Без объекта`.
- `20.12.2025`, `26.12.2025`, `21.04.2026`: short `1 бп` or `1 сп` messages immediately after `Белинского 30` belong to `Белинского 30`.
- `22.12.2025`: `1 бп` after `Белинского 30 / 1 бп` belongs to the same `Белинского 30` address, not to `Без объекта`.
- `14.05.2026`: `БП ОФ Кузнецова 21` was counted under `ОФ`, but `Кузнецова 21` may be a separate object.
