# 1C Report Routes For Expense Exports

Use this reference when the user asks which 1С:Бухгалтерия 3.0 report to open and which settings to apply.

## Choose The Report

| Goal | 1C report | Use when |
|---|---|---|
| Expenses by account | Оборотно-сальдовая ведомость по счету | The expense account is known: 20, 26, 44, 91.02 or another cost account. |
| Rent accruals or settlements with owners | ОСВ by account 60 or 76, or the cost account side | The user needs owner rent and settlements. |
| Row-level operations | Карточка счета | The user needs dates, postings, documents, counterparties, and contracts. |
| Expenses by analytic | Анализ субконто | Apartments are tracked through object, department, nomenclature group, contract, or another subkonto. |
| Complex search | Журнал проводок or Универсальный отчет | Standard reports do not expose the needed fields. |

## Basic Route

1. Open `Отчеты`.
2. Select `Оборотно-сальдовая ведомость по счету`, `Карточка счета`, or `Анализ субконто`.
3. Set the period equal to the revenue period.
4. Select the relevant account or analytic.
5. Open report settings.
6. Add available groupings: expense item, department, nomenclature group, object, counterparty, contract, and document registrar.
7. Add filters if the report is too broad.
8. Generate the report, expand groups to the level where apartment and amount are visible.
9. Export to Excel.

## Owner Rent

For margin reporting, prefer accrued rent expense for the period. Cash payments to owners may include advances, debt repayment, or settlement movements that do not equal the period expense.

Useful groupings:

- counterparty;
- contract;
- expense item;
- apartment/object analytic;
- document registrar.

## Apartment Analytics

First identify where the apartment lives in 1C:

- object;
- department;
- nomenclature group;
- contract;
- counterparty;
- document comment or purpose text.

If no apartment key exists, do not claim exact apartment costs. Mark direct expenses only where the address is visible and allocate shared expenses by a declared method.

## Common Errors

- Taking owner cash payment instead of accrued rent expense.
- Mixing revenue and expenses from different periods.
- Counting `Итого` rows as operations.
- Counting deposits, refunds, internal transfers, or pure settlements as expenses.
- Duplicating the same expense from both ОСВ and account card.
- Splitting one apartment into several rows because of inconsistent address spelling.
