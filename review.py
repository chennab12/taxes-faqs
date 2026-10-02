"""Final filing review controls and explicitly hypothetical household scenario."""
import math
import json
import pandas as pd
import streamlit as st
from calculations import ordinary_tax
from content import SOURCES

CHECKS=[
('Scope','Confirmed 2025 tax year, filing status and federal extension/relief','All'),
('Identity','Checked names, dependents, signature authentication and IP PINs in tax software','All'),
('Documents','Compared 2024 return and 2025 account inventory; identified every expected form','All'),
('Income','Reconciled both spouses’ W-2s and all other income; no duplicate imports','All'),
('Income','Checked for corrected information forms and taxable income without forms','All'),
('Investments','Reconciled proceeds, basis, holding periods, wash sales and carryovers','Stock sales'),
('Equity','Reviewed RSU/ESPP/option compensation basis against W-2 and supplemental records','Employee equity'),
('Home','Verified deductible mortgage interest and actual personal property-tax payments','Home'),
('Deductions','Applied deduction limits and compared eligible itemized versus standard','All'),
('Credits','Verified child-credit eligibility, phaseout and any childcare/FSA coordination','Child'),
('Health','Reconciled HSA employer/payroll/direct contributions and distributions on 8889','HSA'),
('Rental','Verified rental income, repairs/improvements, depreciation and passive carryovers','Rental'),
('International','Reviewed worldwide income, foreign assets, FBAR and relevant forms','Foreign accounts'),
('State','Reviewed CA adjustments, state carryovers and state-specific credits','All'),
('Payments','Matched all withholding, estimates and extension payments to the correct year','All'),
('Diagnostics','Cleared software errors and resolved unexplained year-over-year changes','All'),
('Review','Read generated 1040/540 and every applicable schedule; checked calculations','All'),
('Open issues','Resolved all substantive missing-document, eligibility and basis questions','All'),
('Submission','Confirmed both federal and CA e-file acceptance, not just transmission','All'),
('Payment','Saved confirmations for required federal and CA payments or arrangements','All'),
('Archive','Saved return PDFs, source documents, schedules and acknowledgments securely','All')]
SCREENS=['Stock sales','Employee equity','Home','Child','HSA','Rental','Foreign accounts']

def ctc_screen(magi):
    """One otherwise eligible child; MFJ phaseout arithmetic only."""
    return max(0,2200-50*math.ceil(max(0,magi-400000)/1000))

def render(primary):
    st.divider();st.header('✅ Final completeness & accuracy cross-check')
    st.caption('Task coverage and arithmetic checks help identify gaps; they do not establish tax eligibility, detect every omitted source, or guarantee a correct return. No tax IDs, account numbers or documents should be entered here.')
    upload=st.file_uploader('Restore final-review progress',type=['json'],key='review_restore')
    if upload:
        import hashlib
        raw=upload.getvalue();digest=hashlib.sha256(raw).hexdigest()
        if st.session_state.get('review_import_digest')!=digest:
            try:
                data=json.loads(raw)
                if not isinstance(data,dict):raise ValueError()
                for i in range(len(CHECKS)):
                    key='final_tick_'+str(i)
                    if isinstance(data.get(key),bool):st.session_state[key]=data[key]
                for name in SCREENS:
                    value=data.get('screen_'+name)
                    if value in ['Unknown','Applies','Does not apply']:st.session_state['screen_'+name]=value
                st.session_state['review_import_digest']=digest
            except (ValueError,TypeError):st.error('Invalid review backup; expected checklist/status JSON.')
    st.subheader('1. Scope coverage: do these situations apply?')
    screens={}
    for name in SCREENS:
        screens[name]=st.selectbox(name,['Unknown','Applies','Does not apply'],key='screen_'+name)
    unknown=sum(v=='Unknown' for v in screens.values())
    st.subheader('2. Tick each verified final check')
    ticks=[];export={}
    for i,(group,text,condition) in enumerate(CHECKS):
        if condition!='All' and screens[condition]=='Does not apply':continue
        tick=st.checkbox(f'{group}: {text}',key='final_tick_'+str(i))
        ticks.append((text,tick));export['final_tick_'+str(i)]=tick
    done=sum(v for _,v in ticks);total=len(ticks)
    st.progress(done/total if total else 0)
    a,b,c=st.columns(3);a.metric('Final checks verified',f'{done}/{total}');b.metric('Final-review completion',f'{done/total:.0%}' if total else 'Not assessed');c.metric('Scope questions unresolved',unknown)
    primary_applicable=primary[primary['Status']!='Not applicable']
    primary_open=int((primary_applicable['Status']!='Ready').sum())
    issues=st.number_input('Unresolved substantive questions / missing records',min_value=0,value=0,key='review_issues')
    st.metric('Primary checklist items needing attention',primary_open)
    if unknown or issues or primary_open or done<total:
        st.warning('Review remains open: resolve scope questions, checklist gaps and substantive issues. Post-filing acceptance checks naturally remain unticked before submission.')
    else:st.success('All tracked controls are marked complete. Independently verify applicable forms, tax treatment and source records; this is a task-completion result, not certification.')
    export.update({'screen_'+k:v for k,v in screens.items()})
    st.download_button('Save final-review tick progress',json.dumps(export,indent=2),file_name='2025_final_review_progress.json')
    st.subheader('Document coverage calculator')
    expected=st.number_input('Expected source documents from an independent payer/account inventory',min_value=0,value=0,key='docs_expected')
    received=st.number_input('Expected documents received',min_value=0,value=0,key='docs_received')
    reconciled=st.number_input('Received documents entered and reconciled',min_value=0,value=0,key='docs_reconciled')
    if received>expected or reconciled>received:
        st.error('Counts must satisfy reconciled ≤ received ≤ expected. Revise the source inventory if additional forms were discovered.')
    elif not expected:
        st.info('Document coverage is not assessed until you inventory expected documents. Include spouse accounts and corrected forms.')
    else:
        st.metric('Document reconciliation coverage',f'{reconciled/expected:.0%}')
        st.metric('Missing documents',expected-received)
        st.metric('Received but not reconciled',received-reconciled)
        st.progress(reconciled/expected)
    st.caption('Do not count superseded/corrected copies as separate income. Coverage only measures the inventory you supplied; it cannot discover an omitted payer.')
    st.subheader('3. Source-to-return reconciliation calculator')
    st.write('Create a row for each payer/account/category from your independent inventory. Enter the amount supported by records and the corresponding return/interview total. Matching amounts cannot identify an account you never listed.')
    defaults=pd.DataFrame({'Category':['W-2 box 1 — spouse A','W-2 box 1 — spouse B','Taxable interest total','Federal withholding total','CA withholding total','Federal estimated/extension payments','CA estimated/extension payments'],'Source records total':[0.]*7,'Entered total':[0.]*7,'Evidence reviewed':[False]*7})
    ledger=st.data_editor(defaults,num_rows='dynamic',hide_index=True,width='stretch',key='reconcile_ledger')
    valid=ledger[['Source records total','Entered total']].apply(pd.to_numeric,errors='coerce')
    if ledger.empty or valid.isna().any().any() or ledger['Category'].isna().any() or ledger['Category'].astype(str).str.strip().eq('').any():
        st.warning('Complete category labels and both numeric totals for each row.')
    else:
        result=ledger.copy();result['Difference']=valid['Entered total']-valid['Source records total']
        result['Status']=['Unverified' if v is not True and v!=True else ('Mismatch' if abs(d)>0.50 else 'Matched') for v,d in zip(result['Evidence reviewed'],result['Difference'])]
        st.dataframe(result,hide_index=True,width='stretch')
        matched=int((result['Status']=='Matched').sum())
        st.metric('Evidence-reviewed rows matched',f'{matched}/{len(result)}')
        st.caption('$0.50 tolerance permits illustrative dollar rounding. Zero/zero rows require evidence review and do not prove completeness. Do not sum wages, deductions and payments into one tax amount.')
        st.download_button('Download reconciliation CSV',result.to_csv(index=False).encode(),file_name='2025_reconciliation.csv')
    st.subheader('4. Forms coverage checklist')
    st.dataframe(pd.DataFrame([
        ['Both working spouses','Each W-2; corrected forms','Form 1040 and CA 540 wages/withholding'],
        ['Shares sold','1099-B plus verified basis','8949 / Schedule D; W-2 compensation as applicable'],
        ['Home itemization','1098; actual tax payments','Schedule A; CA deduction adjustments'],
        ['Eligible child','Dependency, age, residency, SSN facts','Schedule 8812; 2441 if qualifying care'],
        ['HSA','W-2 code W; 1099-SA; contribution and receipt records','8889; CA HSA adjustments'],
        ['IRA basis or conversions','1099-R; 5498; prior basis','8606 if required; appropriate 1040 lines'],
        ['Rental','Rent ledger; depreciation and carryovers','Schedule E; 4562 / 8582 when applicable'],
        ['Marketplace coverage','1095-A','8962 if required'],
        ['Foreign accounts','Balances, ownership, income and assets','Schedule B; FBAR separately; 8938/other forms if required'],
        ['Other 2025 deductions','Eligibility and substantiation','Schedule 1-A if qualified']
    ],columns=['Situation','Records','Forms / review area']),hide_index=True,width='stretch')
    st.markdown('[IRS common-error checklist](https://www.irs.gov/taxtopics/tc303) · [2025 Form 1040 instructions](https://www.irs.gov/instructions/i1040gi)')
    family_example()

def family_example():
    st.subheader('5. Hypothetical Bay Area tech-family example — editable')
    st.info('Example only: married filing jointly; both spouses are software engineers with 10 years’ experience; one eligible 10-year-old child; one personal single-family home. Experience and location do not establish salary or deductions. Inputs below are invented for learning, not salary benchmarks or your family’s data.')
    a,b=st.columns(2)
    wage_a=a.number_input('Spouse A — W-2 box 1 wages ($)',min_value=0.,value=220000.,key='family_a')
    wage_b=b.number_input('Spouse B — W-2 box 1 wages ($)',min_value=0.,value=200000.,key='family_b')
    interest=a.number_input('Taxable bank interest ($)',min_value=0.,value=2000.,key='family_interest')
    adjustments=b.number_input('Verified adjustments to income ($)',min_value=0.,value=0.,key='family_adj')
    mortgage=a.number_input('Mortgage interest already verified deductible ($)',min_value=0.,value=28000.,key='family_mortgage')
    state_tax=b.number_input('Personal state income taxes paid in 2025 ($)',min_value=0.,value=30000.,key='family_state')
    property_tax=a.number_input('Personal property taxes actually paid in 2025 ($)',min_value=0.,value=15000.,key='family_property')
    charity=b.number_input('Charitable gifts already verified deductible ($)',min_value=0.,value=2000.,key='family_charity')
    withholding=a.number_input('Combined federal withholding ($)',min_value=0.,value=65000.,key='family_withheld')
    payments=b.number_input('Verified federal estimated + extension payments ($)',min_value=0.,value=0.,key='family_paid')
    agi=wage_a+wage_b+interest-adjustments
    if agi<0:st.error('Adjustments exceed this simplified scenario’s income. Review inputs.');return
    custom_magi=st.checkbox('Use a custom MAGI after reviewing official definitions',key='family_custom_magi')
    magi=st.number_input('MAGI for this example’s SALT/CTC screen ($)',min_value=0.,value=float(agi),key='family_magi') if custom_magi else agi
    st.caption('MAGI is assumed equal for the two screens in this example; actual definitions can differ and require add-backs. By default MAGI follows the recalculated AGI; enable the custom override only after reviewing definitions. Do not include RSU compensation a second time when already included in W-2 box 1. Pretax payroll 401(k) is generally already reflected in box 1.')
    if magi>500000:
        st.warning('SALT MAGI phase-down applies above $500,000. Use the official Schedule A worksheet; this simplified example does not compute that phase-down.')
        allowed_salt=st.number_input('Allowed SALT from official worksheet ($)',min_value=0.,max_value=40000.,value=10000.,key='family_salt_override')
        allowed_salt=min(allowed_salt,state_tax+property_tax)
    else:allowed_salt=min(state_tax+property_tax,40000.)
    itemized=mortgage+allowed_salt+charity;deduction=max(31500.,itemized)
    taxable=max(0,agi-deduction);regular,layers=ordinary_tax(taxable,'Married filing jointly')
    child_credit=ctc_screen(magi);after=max(0,regular-child_credit);balance=after-withholding-payments
    metrics=[['Combined box 1 wages',wage_a+wage_b,'Two W-2s, not gross compensation doubled with RSUs'],['Illustrative AGI',agi,'Wages + interest − verified adjustments'],['Allowed SALT used',allowed_salt,'Personal income tax + property tax, subject to official limit'],['Illustrative itemized deductions',itemized,'Verified interest + allowed SALT + charity'],['Deduction used in example',deduction,'Larger of itemized vs $31,500 base standard'],['Taxable ordinary income',taxable,'AGI less deduction'],['Regular federal tax before credits',regular,'Continuous rate-schedule illustration'],['CTC phaseout screen',child_credit,'One otherwise eligible child; $50 reduction per started $1,000 above $400,000 MFJ'],['Illustrative regular tax after CTC',after,'Excludes other taxes and credits'],['Illustrative balance (+ due / − refund)',balance,'Illustrative tax − withholding − payments']]
    st.dataframe(pd.DataFrame(metrics,columns=['Metric','Example amount ($)','Meaning / cross-check']),hide_index=True,width='stretch')
    st.bar_chart(pd.DataFrame({'Amount':[31500.,itemized]},index=['Base standard deduction','Illustrative itemized']))
    st.bar_chart(pd.DataFrame(layers).set_index('Rate')['Tax'])
    st.warning('This is not a complete return or a payment recommendation. Excludes IRS Tax Table rounding, preferential gains/dividends, AMT, NIIT, Additional Medicare Tax, self-employment tax, additional deductions, other credits, penalties and California tax. Two high W-2 incomes can require additional tax reviews even when regular-income arithmetic looks reconciled.')
    st.dataframe(pd.DataFrame([
        ['RSU/ESPP','W-2 compensation and stock-sale basis','Do not add compensation twice; reconcile each sale'],
        ['10-year-old child','Dependency and CTC tests; work-related care if applicable','Private-school tuition is not automatically deductible childcare'],
        ['Two W-2 earners','Additional Medicare Tax and withholding','Review Form 8959; separate-employer withholding can differ from joint liability'],
        ['Investment income','NIIT and capital-gains worksheets','Review Form 8960 when applicable'],
        ['Single-family home','Qualified mortgage debt and actual tax payments','Escrow deposits and mortgage principal are not deductions'],
        ['California','Federal/state differences','Use Schedule CA; federal SALT/CTC outcome is not CA tax'],
        ['HSA/retirement if applicable','Eligibility, payroll exclusion and records','Avoid duplicate deductions; account for CA HSA treatment']
    ],columns=['Example-family issue','Verify','Practical check']),hide_index=True,width='stretch')
    st.markdown(f"[Schedule A]({SOURCES['Itemized deductions']}) · [Child credit]({SOURCES['Child Tax Credit']}) · [CA adjustments]({SOURCES['CA adjustments']}) · [Additional Medicare Tax](https://www.irs.gov/taxtopics/tc560) · [NIIT](https://www.irs.gov/newsroom/net-investment-income-tax)")
