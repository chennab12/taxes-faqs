import pandas as pd
import streamlit as st
from calculations import BRACKETS,STANDARD,ordinary_tax,payment_balance,eligible_medical
from content import SOURCES

def render(prefix):
    tool=st.selectbox('Choose a tax tool',['2025 ordinary-income brackets','Deduction comparison','Payment reconciliation','Capital gain arithmetic','Rental worksheet','Filing readiness'],key=prefix+'tool')
    if tool=='2025 ordinary-income brackets':
        status=st.selectbox('Filing status',list(BRACKETS),index=1,key=prefix+'status')
        taxable=st.number_input('2025 taxable ordinary income ($), after deductions',min_value=0.,value=100000.,key=prefix+'income')
        tax,rows=ordinary_tax(taxable,status)
        st.metric('Illustrative regular federal tax before credits',f'${tax:,.2f}')
        st.metric('Average rate on this taxable income',f'{tax/taxable:.2%}' if taxable else '0%')
        df=pd.DataFrame(rows);st.bar_chart(df.set_index('Rate')['Tax']);st.dataframe(df,hide_index=True)
        st.caption('Each bar is tax on one income layer. Educational continuous rate schedule only: excludes IRS Tax Table rounding, preferential gains/dividends, credits, AMT, NIIT, self-employment tax and all state tax. Do not copy this estimate into a return. Qualifying surviving spouses use MFJ rates; special status rules still apply.')
        st.markdown(f"[IRS brackets]({SOURCES['Brackets']}) · [2025 tax tables and worksheets]({SOURCES['1040 instructions']})")
    elif tool=='Deduction comparison':
        status=st.selectbox('Status for base standard deduction',list(STANDARD),index=1,key=prefix+'ds')
        agi=st.number_input('AGI ($)',min_value=0.,value=120000.,key=prefix+'agi')
        medical=st.number_input('Eligible unreimbursed medical expenses ($)',min_value=0.,value=0.,key=prefix+'med')
        interest=st.number_input('Mortgage interest already determined deductible ($)',min_value=0.,value=10000.,key=prefix+'interest')
        salt=st.number_input('SALT already limited under Schedule A worksheet ($)',min_value=0.,value=10000.,key=prefix+'salt')
        charity=st.number_input('Charitable gifts already determined deductible ($)',min_value=0.,value=0.,key=prefix+'charity')
        others=st.number_input('Other allowed itemized deductions ($)',min_value=0.,value=0.,key=prefix+'other')
        eligible=eligible_medical(agi,medical);total=eligible+interest+salt+charity+others
        st.bar_chart(pd.DataFrame({'Deduction':[STANDARD[status],total]},index=['Base standard','Illustrative itemized']))
        st.metric('Medical amount above 7.5% AGI floor',f'${eligible:,.2f}');st.metric('Itemized minus base standard',f'${total-STANDARD[status]:,.2f}')
        st.caption('Comparison aid only. Enter allowed amounts after applicable limits. Standard deduction may differ for age/blindness, dependents, spouse itemizing or other restrictions. Schedule 1-A/QBI deductions are separate. CA is separate. The 2025 federal SALT cap is generally $40,000 ($20,000 MFS), reduced above MAGI $500,000 ($250,000 MFS), with a floor of $10,000 ($5,000 MFS); use the official worksheet.')
        st.markdown(f"[Schedule A rules]({SOURCES['Itemized deductions']}) · [Standard deduction eligibility]({SOURCES['Standard deduction']})")
    elif tool=='Payment reconciliation':
        st.caption('Use final return totals, not the ordinary-income estimate. Run separately for federal and CA. Avoid counting refundable credits twice if already included in the entered payment total.')
        values=[st.number_input(label,min_value=0.,value=0.,key=prefix+str(i)) for i,label in enumerate(['Total tax after nonrefundable credits ($)','Withholding ($)','Estimated payments / prior refund applied ($)','Extension payments ($)','Refundable credits ($)'])]
        balance=payment_balance(*values)
        st.metric('Balance due' if balance>=0 else 'Refund before offsets',f'${abs(balance):,.2f}')
        st.caption('Excludes penalties, interest and refund offsets. Confirm jurisdiction, tax year and payment category.')
    elif tool=='Capital gain arithmetic':
        proceeds=st.number_input('Net sale proceeds ($)',min_value=0.,value=1200.,key=prefix+'proceeds')
        basis=st.number_input('Adjusted cost basis ($)',min_value=0.,value=1000.,key=prefix+'basis')
        st.metric('Gain / loss before other adjustments',f'${proceeds-basis:,.2f}')
        st.caption('Does not compute capital-gains tax or wash sales. Holding period, compensation basis, netting, collectibles, recapture and foreign-currency issues may change treatment.')
    elif tool=='Rental worksheet':
        income=st.number_input('Gross rental income ($)',min_value=0.,value=30000.,key=prefix+'rent')
        expense=st.number_input('Eligible operating expenses ($), excluding depreciation',min_value=0.,value=12000.,key=prefix+'ex')
        depreciation=st.number_input('Depreciation from verified schedule ($)',min_value=0.,value=5000.,key=prefix+'dep')
        st.metric('Illustrative rental result before limitations',f'${income-expense-depreciation:,.2f}')
        st.caption('Not a determination of deductible loss. Personal-use allocation, basis, passive/at-risk limits and depreciation conventions matter. Do not divide full purchase price by 27.5: land is not depreciable and first/last-year conventions apply.')
    else:
        st.write('A completed checklist is an organizational aid. Resolve substantive questions before transmitting the return.')
        total=st.number_input('Applicable checklist items',min_value=1,value=24,key=prefix+'tot')
        completed=st.number_input('Completed applicable items',min_value=0,max_value=int(total),value=0,key=prefix+'done')
        st.progress(completed/total);st.metric('Completion',f'{completed/total:.0%}')
