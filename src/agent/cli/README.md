# DeepseekTravels Packing CLI

A simple command-line tool to generate a travel packing list using deterministic rules.

## Commands

- simple: Print a concise checklist (name + qty)
- generate: Print the full structured response (categories, reasons, totals)

## Arguments

Required positional:
- destination: City or location name
- start: Trip start date (YYYY-MM-DD)
- end: Trip end date (YYYY-MM-DD)
- trip_days: Integer number of days

Optional flags:
- --activities: Zero or more activity tags (e.g., hiking beach business business_dinner)
- --tod: Time-of-day usage, any of day night (default: day)
- --weather: Iteration 2 weather hints: cold rain heat

## Examples (Windows PowerShell)

- Concise checklist for a 3-day Paris trip:

```powershell
python .\src\agent\cli\deepseek_travels_cli.py simple Paris 2025-10-01 2025-10-03 3 --activities hiking --tod day
```

- Full list with activities, day+night items, and weather hints (cold, rain, heat):

```powershell
python .\src\agent\cli\deepseek_travels_cli.py generate Paris 2025-10-01 2025-10-03 3 --activities hiking beach business_dinner --tod day night --weather cold rain heat
```

Notes:
- The CLI adds repo root to sys.path automatically when run by file path.
- All logic is offline; weather is provided via --weather hints during Phase 1.
