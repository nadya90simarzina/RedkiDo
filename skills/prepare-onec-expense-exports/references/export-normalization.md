# 1C Export Normalization

Use this reference when the user attaches an Excel or CSV export from 1С:Бухгалтерия 3.0.

## Target Table

Normalize exports into a long table where one row equals one expense operation or one expense amount by apartment.

Recommended columns:

| Field | Meaning |
|---|---|
| `date` | operation date or period |
| `apartment` | address or apartment key |
| `expense_category` | management expense category |
| `amount` | expense amount |
| `attribution_type` | `direct`, `allocated`, or `needs_review` |
| `allocation_base` | allocation base for shared costs |
| `account_debit` | debit account |
| `account_credit` | credit account |
| `counterparty` | counterparty |
| `contract` | contract |
| `expense_item` | 1C expense item |
| `document` | source document |
| `description` | source description or comment |

## Cleanup Rules

1. Find the header row by words such as date, account, debit, credit, amount, counterparty, contract, expense item, department, object.
2. Remove blank rows, report headers, and settings rows.
3. Remove total rows: `Итого`, `Общий итог`, opening balance, closing balance, turnover summary.
4. Convert amounts to numbers: remove spaces, non-breaking spaces, currency symbols, and convert comma decimals.
5. Normalize apartment names and address spelling.
6. If apartments are columns, unpivot the report into long format.
7. Keep a source sheet and source row reference for auditability.

## Apartment Detection Priority

1. Explicit `Адрес`, `Квартира`, or `Объект` column.
2. Department or nomenclature group if they represent apartments.
3. Contract, if each contract maps to one apartment.
4. Counterparty, if each owner maps to one apartment.
5. Document text, comment, or payment purpose.
6. Known address list supplied by the user.

If apartment cannot be found, do not silently assign the row. Mark it as `needs_review` or `allocated`.

## Checks

- Normalized amount should explainably match the source total after excluding totals and service rows.
- Rows without apartment must be visible.
- Negative amounts require review: refund, reversal, correction, or discount.
- Do not duplicate the same operation from multiple 1C reports.
- Map 1C expense items to stable management categories.

## Output For Margin

Prepare a summary by apartment:

| Apartment | Direct expenses | Allocated expenses | Total expenses | Needs review |
|---|---:|---:|---:|---|

Then join it with revenue for the same apartment and period.
