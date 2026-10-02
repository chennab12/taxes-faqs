from datetime import date
from zoneinfo import ZoneInfo
from datetime import datetime
import json
import pandas as pd
import streamlit as st
from content import SOURCES,TOPICS,CHECKLIST,STEPS,MISTAKES,MISSED,MYTHS,ESCALATE
from calculations import STANDARD,BRACKETS,RATES
from tools import render
from review import render as final_review
st.set_page_config(page_title='Tax Filing Compass',page_icon='🧾',layout='wide')
st.title('🧾 Tax Filing Compass')
st.caption('2025 tax year · Federal + California · Sources checked October 1, 2026')
st.info('Use this as a filing organizer and explanation guide alongside updated 2025 tax software and official instructions. A checklist cannot guarantee an error-free return; resolve items that depend on your facts before filing.')

def frame(data,columns=None):
    df=pd.DataFrame(data,columns=columns)
    config={c:st.column_config.LinkColumn(c) for c in df.columns if c=='Official link'}
    st.dataframe(df,hide_index=True,width='stretch',column_config=config)
    return df

def source(name):st.markdown(f'[Official guidance: {name} ↗]({SOURCES[name]})')

names=['📌 Master cheatsheet','🚨 File 2025 by Oct 15']+[t[0] for t in TOPICS]+['🧮 Calculators','📚 Official links']
tabs=st.tabs(names)
with tabs[0]:
    st.header('Tax concepts at a glance')
    search=st.text_input('Search master table')
    master=[dict(zip(['Focus','Core concept','Example','Do / next step','Key metric / formula','Reference'],r)) for r in TOPICS]
    df=pd.DataFrame(master);df['Official link']=df['Reference'].map(SOURCES)
    if search:df=df[df.astype(str).apply(lambda s:s.str.contains(search,case=False,regex=False)).any(axis=1)]
    frame(df);st.download_button('Download cheatsheet CSV',df.to_csv(index=False).encode(),file_name='tax_cheatsheet.csv')
    st.subheader('2025 numbers to verify against your eligibility')
    frame([['Federal base standard deduction', '$31,500 MFJ; $15,750 single/MFS; $23,625 HOH','Age/blindness, dependent and other rules can change amount'],['Federal SALT cap','$40,000; $20,000 MFS','MAGI reduction above $500,000/$250,000; floor $10,000/$5,000'],['Child Tax Credit','Up to $2,200 per qualifying child','Eligibility, SSN rules, income phaseout and refundability matter'],['Medical deduction threshold','Eligible expenses above 7.5% AGI','Itemized only; unreimbursed qualifying costs'],['2025 HSA base limits','$4,300 self-only; $8,550 family','Eligibility, employer amounts, monthly coverage and catch-up rules'],['California base standard deduction','$5,706 single/MFS; $11,412 MFJ/HOH','State rules differ; review official instructions']],['Metric','2025 figure','Important condition'])
    source('1040 instructions');source('CA deductions')
    st.subheader('2025 federal ordinary-income rate thresholds')
    bracket_rows=[]
    for i,rate in enumerate(RATES):
        row={'Rate':f'{rate:.0%}'}
        for status,thresholds in BRACKETS.items():
            lower=0 if i==0 else thresholds[i-1]
            upper=thresholds[i] if i<len(thresholds) else None
            row[status]=f'Above ${lower:,.0f} through ${upper:,.0f}' if upper else f'Above ${lower:,.0f}'
        bracket_rows.append(row)
    frame(bracket_rows)
    st.caption('Thresholds apply to taxable ordinary income, not gross salary. Rate schedules are explanatory; actual return preparation may require the IRS Tax Table or special worksheets.')
    source('Brackets')
with tabs[1]:
    st.header('2025 filing command center • October 15, 2026')
    st.warning('Federal: October 15 is generally available after a timely extension, subject to applicable exceptions/relief. Filing extension did not extend the usual April 15, 2026 payment deadline. California generally grants an automatic filing extension to October 15, with payment due April 15. Check relief separately; do not assume an October extension exists for federal filing.')
    source('Extension');source('CA deadlines');source('Disaster relief')
    today=datetime.now(ZoneInfo('America/Los_Angeles')).date();deadline=date(2026,10,15)
    st.metric('Calendar days to October 15, 2026',(deadline-today).days)
    if today>deadline:st.error('This filing target has passed. Follow current IRS/FTB guidance and file promptly; this dashboard is still a 2025-tax-year guide.')
    st.write('High-priority review areas for a California household with employee equity, an HSA and a rented property: cost basis, Form 8889, rental depreciation/carryovers, actual property-tax payments, and California adjustments. Check these only if they apply to your 2025 facts.')
    st.subheader('Comprehensive filing checklist')
    upload=st.file_uploader('Restore checklist progress JSON (no tax IDs or account details)',type=['json'])
    if upload:
        try:
            restored=json.load(upload)
            if not isinstance(restored,list):raise ValueError('Expected a list')
            allowed={'Missing','In progress','Ready','Not applicable'}
            by_item={r.get('Item'):r.get('Status') for r in restored if isinstance(r,dict) and r.get('Status') in allowed}
        except (ValueError,TypeError):st.error('Invalid progress file.');by_item={}
    else:by_item={}
    check=pd.DataFrame([{'Category':r[0],'Item':r[1],'Evidence to gather':r[2],'Required verification':r[3],'Official link':SOURCES[r[4]],'Status':by_item.get(r[1],'Missing')} for r in CHECKLIST])
    edited=st.data_editor(check,hide_index=True,width='stretch',disabled=list(check.columns[:-1]),column_config={'Status':st.column_config.SelectboxColumn(options=['Missing','In progress','Ready','Not applicable'],required=True),'Official link':st.column_config.LinkColumn('Official link')},key='checklist')
    applicable=edited[edited['Status']!='Not applicable'];ready=(applicable['Status']=='Ready').sum()
    a,b,c=st.columns(3);a.metric('Applicable items',len(applicable));b.metric('Marked ready',int(ready));c.metric('Need attention',len(applicable)-int(ready))
    st.progress(float(ready/len(applicable)) if len(applicable) else 0)
    st.caption('Ready means you verified the item; it is not an IRS approval or correctness score. Progress is session-only unless downloaded. Do not enter personal identifiers here.')
    st.download_button('Save checklist progress JSON',edited[['Item','Status']].to_json(orient='records'),file_name='2025_tax_checklist_progress.json')
    st.download_button('Download full checklist CSV',edited.to_csv(index=False).encode(),file_name='2025_tax_checklist.csv')
    st.subheader('Sequence for filing yourself')
    frame(STEPS,['Step','Suggested timing','Action','Completion evidence'])
    st.caption('Dates are a suggested October 2026 work plan. Complete unresolved technical issues before filing; seek targeted help rather than guessing.')
    st.subheader('Common mistakes and prevention');frame(MISTAKES,['Mistake','Why it matters','How to avoid'])
    st.subheader('Important items commonly missed');frame(MISSED,['Item','Why important','Check / next step'])
    st.subheader('Myths versus facts');frame(MYTHS,['Myth','Fact'])
    st.subheader('Other important decisions / when to get help');frame(ESCALATE,['Situation','Why review is needed','Practical next step'])
    st.subheader('Final submission controls')
    frame([['Federal return','Submitted → accepted','Save IRS/provider acknowledgment'],['California return','Submitted → accepted','Save FTB/provider acknowledgment'],['Federal payment','Correct year and type','Save payment reference; return filing does not itself prove payment'],['CA payment','Correct year and type','Save separate state confirmation'],['FBAR if required','Separate FinCEN submission','Save report acknowledgment; not part of Form 1040'],['Archive','PDF return + schedules + source records','Keep basis, rental and carryover records beyond ordinary annual filing records']],['Control','Expected state','Evidence'])
    st.subheader('Visual: income-to-filing flow')
    st.graphviz_chart('digraph {rankdir=TB; node [shape=box]; income [label="Income + records"]; agi [label="Adjustments → AGI"]; taxable [label="Deductions → taxable income"]; tax [label="Tax worksheets → credits"]; balance [label="Payments → refund / balance"]; federal [label="Federal review + acceptance"]; ca [label="CA adjustments + acceptance"]; income -> agi -> taxable -> tax -> balance; balance -> federal; balance -> ca;}')
    st.subheader('Tax calculations and interactive charts');render('filing_')
    st.subheader('Official IRS and FTB links for filing')
    frame([{'Task':n,'Official link':u} for n,u in SOURCES.items()])
    st.caption('IRS Free File guided software uses a 2025 AGI threshold of $89,000, with partner-specific eligibility and possible state charges. Fillable Forms closes October 15, 2026 and requires greater tax knowledge; choose a tool that supports your forms.')
    final_review(edited)
for tab,topic in zip(tabs[2:2+len(TOPICS)],TOPICS):
    title,meaning,example,action,metric,ref=topic
    with tab:
        st.header(title);frame([['Core concept',meaning],['Intuitive example',example],['Do / next step',action],['Metric / formula',metric]],['Field','Quick reference'])
        source(ref)
        related=[r for r in CHECKLIST if r[4]==ref or r[0] in ({'Rental'} if ref=='Rental' else set())]
        if related:frame([[r[1],r[2],r[3]] for r in related],['Task','Evidence','Verification'])
        with st.expander('Knowledge check: how would you verify this area?'):
            st.text_area('Your answer first',key='quiz_'+ref)
            if st.checkbox('Show expected answer',key='show_'+ref):st.success('Identify applicable forms and source records; reconcile amounts, eligibility and carryovers; check federal and CA differences; resolve unexplained results before filing. '+action)
        st.subheader('Common error to avoid')
        st.write('Applying a general rule without checking tax year, eligibility, exceptions and state differences. Follow the linked official instructions and record your evidence.')
with tabs[-2]:render('general_')
with tabs[-1]:
    st.header('Official references and scope')
    frame([{'Topic':n,'Official link':u} for n,u in SOURCES.items()])
    st.write('This app covers common US individual-return topics with California guidance. It does not calculate a complete tax return, verify eligibility automatically, or cover every international/business situation. Use final 2025 forms and updated software. Numeric scenarios show their exclusions. Content snapshot: October 1, 2026.')
