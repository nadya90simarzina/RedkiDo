# Linen Writeoff Counting Rules

Use these rules when interpreting Russian free-form linen writeoff messages from Telegram.

## Categories

Report exactly these categories, in this order:

```text
БП
СП
НП
МП
Пододеяльник
Простынь
Наволочка
```

## Synonyms

- `ноги`, `ножки`, `лапки`, `для ног` -> `НП`.
- `б.пол.`, `б пол`, `большое полотенце`, `полотенце большое` -> `БП`.
- `среднее полотенце` -> `СП`.
- `м пол`, `м.пол.`, `малое полотенце`, `полотенце для лица`, `П.мал.` -> `МП`.
- `подод`, `под одеяльник` -> `Пододеяльник`.

## Quantities

- `1БП`, `1 бп`, `БП 1`, `Пододеяльник 2`, `2простыни` are valid quantity forms.
- If an object and category are present but no number is written, count 1 and mark it as an assumption.
- If a message is only `БП`, `СП`, `НП`, or `МП` with no object, count 1 under `Без объекта`.
- If a short no-object item-only photo caption such as `Бп` is immediately followed by the same sender's message with an object and the same item, treat the caption as a duplicate and count only the object-specific message.
- Empty old-summary forms like `НП-` or `Простынь-` mean 0.

## Object Context

- If a short joined or follow-up message has no object, inherit the previous object only when it is close in time and from the same sender.
- For photo-caption follow-ups, "close in time" can include a same-sender sequence within about 45 minutes when no other object interrupts the block.
- If no object can be recovered, use `Без объекта`.
- Record context inheritance in the ambiguous notes.

## Discussion And Duplicates

- Do not count general discussion, questions, or explanations without a new quantity.
- If a later message says `итого` and summarizes preceding detail, count the `итого` number and avoid double-counting earlier descriptive lines.
- If a category word is repeated accidentally, such as `1 простынь простынь`, count it once and note the repeat.

## Ambiguity Notes

Always list:

- object inherited from context;
- messages counted under `Без объекта`;
- synonym mappings that are not obvious;
- rows counted as 1 because no quantity was written;
- possible object ambiguity, such as `БП ОФ Кузнецова 21`;
- ignored non-report items if they could look countable, such as `наматрасник`, `халат`, and discussion-only messages.
