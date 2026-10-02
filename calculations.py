RATES=(.10,.12,.22,.24,.32,.35,.37)
BRACKETS={
'Single':(11925,48475,103350,197300,250525,626350),
'Married filing jointly':(23850,96950,206700,394600,501050,751600),
'Married filing separately':(11925,48475,103350,197300,250525,375800),
'Head of household':(17000,64850,103350,197300,250500,626350)}
STANDARD={'Single':15750,'Married filing jointly':31500,'Married filing separately':15750,'Head of household':23625}
def ordinary_tax(taxable,status):
    """Continuous rate-schedule illustration, not IRS Tax Table or full Form 1040."""
    if taxable<0:raise ValueError('Taxable income must be nonnegative')
    result=[];lower=0
    for upper,rate in zip((*BRACKETS[status],float('inf')),RATES):
        amount=max(0,min(taxable,upper)-lower)
        result.append({'Rate':f'{rate:.0%}','Taxed dollars':amount,'Tax':amount*rate})
        lower=upper
    return sum(r['Tax'] for r in result),result

def payment_balance(total_tax,withholding,estimates,extension,refundable):
    return total_tax-withholding-estimates-extension-refundable

def eligible_medical(agi,expenses):return max(0,expenses-.075*agi)
