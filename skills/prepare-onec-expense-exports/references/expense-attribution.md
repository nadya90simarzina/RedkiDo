# Expense Attribution For Apartment Margin Reports

Use this reference when deciding whether a 1C expense should be assigned directly to an apartment or allocated by formula.

## Principle

Assign an expense directly only when a reliable apartment key is present: address, object, contract, department, nomenclature group, owner counterparty, or a clear document note.

If the key is missing, treat the expense as calculation-based. In the margin report, show it separately from factual direct expenses.

## Classification

| Expense | Type | Allocation base if no apartment key |
|---|---|---|
| Owner rent | Direct | Do not allocate without contract/address. |
| Utilities | Direct | Address, area, or apartment-months. |
| Internet, TV, intercom | Direct | Address or apartment-months. |
| Repairs, furniture, appliances, locks | Direct | Do not allocate without evidence. |
| Cleaning | Direct or allocated | Cleanings or bookings. |
| Laundry | Allocated | Bookings, cleanings, or nights. |
| Consumables: paper, tea, sugar, coffee, soap, chemicals | Allocated | Bookings or nights. |
| Linen and towels | Direct or allocated | Cleanings, nights, or sleeping places. |
| Administrator payroll | Allocated | Revenue or bookings. |
| Service staff payroll | Allocated | Cleanings, bookings, or apartment-months. |
| Platform commissions and acquiring | Direct or allocated | Revenue, if not visible by booking. |
| Office overhead | Allocated | Revenue. |

## Formula

```text
Apartment cost = total shared cost * apartment base / total base across all apartments
```

Examples:

- by bookings: apartment bookings / total bookings;
- by nights: apartment nights / total nights;
- by revenue: apartment revenue / total revenue;
- by apartment-months: apartment active months / total active apartment-months;
- by area: apartment area / total area.

## Recommended Bases For Daily Rentals

- Laundry: bookings or cleanings.
- Consumables: bookings or nights.
- Linen: cleanings, nights, or sleeping places.
- Administrator payroll: revenue or bookings.
- Service staff payroll: cleanings or bookings.
- Office overhead: revenue.

Bookings are often better than revenue for laundry and consumables, because an expensive apartment does not necessarily use more paper, soap, or laundry per check-in.

## Margin Status Hints

Use only as management hints, not accounting norms:

- good: margin above 35%;
- medium: 20-35%;
- low: 0-20%;
- loss-making: profit below 0.

## Exclude Without Review

- guest deposits;
- guest refunds;
- internal bank transfers;
- advances to owners;
- debt repayment without expense accrual;
- settlement-only rows;
- taxes if the report is meant to show operating margin before taxes.
