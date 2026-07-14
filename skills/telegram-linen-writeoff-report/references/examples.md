# Examples

## Basic Object Lines

Input:

```text
Радиус
5сп
1нп
Износ
```

Expected:

```text
Радиус:
СП-5
НП-1
```

## Synonyms For НП

Input:

```text
Бажовский- ножки
Азина 1 для ног
Артек 1 лапки
```

Expected:

```text
Бажовский НП-1
Азина НП-1
Артек НП-1
```

## Context Continuation

Input:

```text
Белинского 30 1 ноги
1 сп
```

When the second message is close in time and from the same sender, expected:

```text
Белинского 30:
НП-1
СП-1
```

## No Object

Input:

```text
Бп
```

Expected:

```text
Без объекта:
БП-1
```

## Caption Followed By Object

Input:

```text
Бп
Белинского 86
1 бп
```

When both messages are from the same sender and close in time, expected:

```text
Белинского 86:
БП-1
```

Do not also count the first `Бп` under `Без объекта`; it is a short caption duplicated by the object-specific message.

## Summary Avoiding Double Count

Input:

```text
Хохрякова 63 простынь.
Дыра.
Ещё одна. тоже дыра.
Итого две простыни с дырками.
```

Expected:

```text
Хохрякова 63:
Простынь-2
```

The first descriptive `простынь` line is not added on top of the later `итого`.
