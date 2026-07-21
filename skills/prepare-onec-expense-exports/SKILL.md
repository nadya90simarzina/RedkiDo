---
name: prepare-onec-expense-exports
description: Use this skill when the user needs to выгрузить расходы из 1С:Бухгалтерия 3.0, сформировать ОСВ, карточку счета or Анализ субконто, check screenshots from 1C, normalize Excel/CSV exports, classify apartment expenses, allocate shared costs, or prepare expense data for apartment margin reports. Trigger on phrases like "как выгрузить расходы из 1С", "сформировать оборотку по аренде", "проверь выгрузку 1С", "подготовь расходы для маржи квартир", or "какие расходы отнести на квартиры".
metadata:
  author: "Codex"
  status: "team-ready"
---

# Prepare 1C Expense Exports

## Authorship

Author: Codex.

This skill was created as a Codex-authored contribution for review through a Pull Request. It is based on a sanitized workflow for preparing 1C expense exports for apartment margin reporting; it must not contain raw client screenshots, private file paths, real owner names, phone numbers, or unredacted exports.

## Overview

Help turn data from 1С:Бухгалтерия 3.0 into usable management-reporting expense data for apartments. The skill supports three inputs: a text question, a screenshot from 1C, or an Excel/CSV export.

The goal is not statutory accounting or tax advice. The goal is to prepare a clear expense table for a margin report: which costs are direct by apartment, which costs are calculation-based allocations, which rows need review, and which 1C report settings should be used next time.

## Request Router

- Text question about 1C: give a step-by-step route in 1C and the minimal report settings.
- Screenshot from 1C: read the visible report type, account, period, groupings, filters, and missing pieces; ask for Excel/CSV if totals cannot be trusted from the screenshot.
- Excel/CSV export: normalize rows, remove totals, classify expenses, and prepare data that can be joined with apartment revenue.
- Shared expenses question: separate direct costs from allocated costs and suggest an allocation base.
- Director-facing report question: prepare management P&L logic by apartment, not a raw accounting turnover table.

## Workflow

1. Define the report goal: owner rent, all apartment expenses, export quality check, or margin-report input.
2. Identify the apartment key in 1C: address, object, department, nomenclature group, contract, counterparty, document comment, or another analytic.
3. For 1C report setup, read `references/1c-report-routes.md`.
4. For attached Excel/CSV exports, use `scripts/normalize_1c_expenses.py` or manually follow `references/export-normalization.md`.
5. For direct versus allocated expenses, read `references/expense-attribution.md`.
6. Reconcile control totals: the normalized total should explainably match the 1C export after excluding report headers, service rows, and totals.
7. Return a table that can be joined with apartment revenue for the same period.

## 1C Report Routes

For 1С:Бухгалтерия 3.0, usually choose:

- `Оборотно-сальдовая ведомость по счету` when the account is known.
- `Карточка счета` when the user needs row-level postings and source documents.
- `Анализ субконто` when apartment information exists as analytics.
- `Журнал проводок` or `Универсальный отчет` when standard reports do not expose the needed fields.

For apartment margin, accrued rent expense is usually more useful than cash payment to the owner, because margin needs costs of the same period as revenue.

## Expense Attribution

Treat expenses as direct only when there is a reliable apartment key. Typical direct costs: rent, utilities, internet, repairs, furniture, equipment, locks, address-specific cleaning, and address-specific platform commissions.

Treat shared costs as calculation-based allocations when no apartment-level accounting was maintained. Typical allocated costs: laundry, consumables, linen, administrator payroll, service staff payroll, and office overhead.

Use this formula:

```text
Apartment cost = total shared cost * apartment base / total base across all apartments
```

Recommended bases:

- laundry: bookings or cleanings;
- consumables: bookings or nights;
- linen: cleanings, nights, or sleeping places;
- administrator payroll: revenue or bookings;
- service staff payroll: cleanings, bookings, or apartment-months;
- office overhead: revenue.

Always state when costs are allocated, not factual apartment-level expenses.

## Output Shape

For an export, prepare these blocks or sheets:

- `operations_normalized`: date, apartment, category, amount, debit account, credit account, counterparty, contract, document, attribution type, allocation base, comment.
- `expenses_by_apartment`: apartment, direct expenses, allocated expenses, total expenses, needs review.
- `allocation_rules`: expense type, total amount, allocation base, reason, factual or calculated status.
- `data_quality_notes`: rows without apartment, suspicious amounts, excluded totals, method limitations.

For a director report, include revenue, direct expenses, allocated expenses, total expenses, profit, margin %, and apartment status.

## Safety And Boundaries

Do not use this skill for tax advice, audit conclusions, legal accounting decisions, or correction of statutory accounting without an accountant.

Do not include guest deposits, refunds, internal transfers, advances to owners, debt repayments without expense accrual, or settlement-only rows as expenses without checking their accounting meaning.

Do not invent exact apartment-level facts from shared costs. If laundry, consumables, linen, or payroll were not tracked by apartment, show the allocation method openly.

## Definition Of Done

The work is complete when the user has:

- a clear 1C route or normalized export;
- direct and allocated expenses separated;
- allocation methodology for shared costs;
- data-quality notes;
- a table ready to connect with revenue for apartment margin reporting.
