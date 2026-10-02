# Tax Filing Compass — 2025 Federal and California

Replacement content for a tabbed Streamlit reference app. Includes master cheatsheet, a dedicated **File 2025 by Oct 15** command center, 12 tax-topic tabs, calculators and official links. All content concerns taxes. The filing center includes a 24-item editable checklist, 11-step self-filing sequence, common mistakes, commonly missed items, myths/facts, escalation criteria, acceptance controls, flow diagram, charts and six calculator modes.

## Run or deploy

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Keep `app.py`, `content.py`, `calculations.py`, `tools.py`, `review.py` and `requirements.txt` in the same repository folder. For Streamlit Cloud set the main file path to `app.py` or its repository-relative path. This deliverable does not change the live website.

## Important scope

For 2025 income, the usual extended federal filing deadline is October 15, **2026**, contingent on a timely extension or applicable exception. California generally grants an automatic filing extension. An extension to file generally does not extend the April 15, 2026 payment date. Check taxpayer-specific disaster relief, international and military exceptions.

Sources checked October 1, 2026. Revised 2025 standard deductions and SALT rules are used; California differences are flagged. The app does not promise an error-free filing or substitute for Form 1040/540 software. Its ordinary-income calculator excludes preferential capital gains/dividends, IRS Tax Table rounding, AMT, NIIT, self-employment tax, credits and state taxes. Other tools are explicitly arithmetic organizers, not full tax liability calculators. Deduction comparison requires already-allowed mortgage/SALT/charity amounts and excludes additional standard-deduction adjustments. No automated SALT phaseout or credit eligibility is calculated.

Do not enter SSNs, bank numbers or full tax documents in this dashboard. Only checklist item/status pairs are backed up in JSON. No external API, telemetry, brokerage or IRS connection is included. Session progress requires a download to persist. A checklist readiness percentage measures task completion only.

Relevant household topics include rental property, employee equity and HSA/CA adjustments; no personal financial amounts are embedded. Unsupported situations, such as PFICs or omitted prior depreciation, receive clear prompts for specialist review.

## Validation

Python compilation, tax bracket boundaries, payment reconciliation and medical-threshold arithmetic passed. Streamlit AppTest rendered the app and exercised all six filing-calculator modes without exceptions.

## Final-review additions

The filing tab ends with applicability screens, 21 tickable final controls, completion metrics linked to the primary checklist, JSON progress backup/restore, an evidence-based source/entry reconciliation ledger with $0.50 rounding tolerance, forms-coverage reference and an editable hypothetical two-engineer California household example. Sample wages are invented, not market salary estimates. The example computes regular federal tax only and explicitly flags AMT/NIIT/Additional Medicare/California omissions. CTC calculation is only a phaseout screen for one otherwise eligible child and sufficient regular tax; no general credit eligibility is certified. High-MAGI SALT requires the official worksheet. All fields are session-local unless downloaded; restrict downloads to secure personal storage.

Final-review validation: Streamlit AppTest passed tick updates, conditional applicability, document-coverage counts, dynamic salary/MAGI changes and the high-MAGI SALT branch. Child-credit phaseout boundary arithmetic passed.
