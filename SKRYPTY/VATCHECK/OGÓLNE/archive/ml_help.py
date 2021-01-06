import datetime as d
import re

from math import floor
from statistics import mean
from unidecode import unidecode

import pandas as pd

################################################
################ FINANCIAL DATA ################
################################################

finance_cols = [
    'NIP', 'ISIC', 'FiscalYear', 'BeginDate', 'EndDate', 'LastUpdate',
    'OriginalStandardCode', 'OutputStandardCode', 'AccountErrorFlag', 'ACCRUE',
    'ACCRUL', 'AFTERTAX', 'AFTERTAXDISC', 'ART', 'ASSETFORSALE', 'AT', 'BONDDEBT',
    'BOOKVALUE', 'BRAYA', 'BRCIR', 'BRDCT', 'BRDCTO', 'BRER', 'BRERA', 'BRLACT',
    'BRLACTO', 'BRLADR', 'BRLADRO', 'BRLAR', 'BRLARO', 'BRLDR', 'BRLDR', 'BRNFCIT',
    'BRNIIT', 'BRNIM', 'BSCA', 'BSCLTL', 'BSFATA', 'BSITA', 'BSPROFIT', 'BSRTA',
    'CA', 'CAT', 'CBIO', 'CE', 'CECASH', 'CEDEPOSIT', 'CEMPL', 'CFADJFINRESULTIN',
    'CFADJGAINPROP', 'CFADJOTHADJ', 'CFADJTANG', 'CFCAPEX', 'CFCASH', 'CFCASHBEGIN',
    'CFCASHEND', 'CFCASHFOREX', 'CFCFFTCF', 'CFCFITCF', 'CFCHNGDEFERRED', 'CFCHNGINV',
    'CFCHNGOTH', 'CFCHNGPREP', 'CFCHNGPROV', 'CFCHNGREC', 'CFCHNGTRADE', 'CFFCF',
    'CFFINBOR', 'CFFINORDINAR', 'CFFINOTHEQUITY', 'CFFINOTHFINACT', 'CFFINPAIDDIV',
    'CFFINPAIDINT', 'CFFINPAYLEASE', 'CFFINREPAYBOR', 'CFFINTREASURY', 'CFINCOMETAX',
    'CFINVESTACQUIRE', 'CFINVESTDEVEXP', 'CFINVESTDIVIDREC', 'CFINVESTFININST',
    'CFINVESTINTREC', 'CFINVESTINVPROP', 'CFINVESTNTANG', 'CFINVESTOTHINVEST',
    'CFINVESTPROP', 'CFINVESTSALEFININST', 'CFINVESTSALEPROP', 'CFNCFFINANCE',
    'CFNCFINVEST', 'CFNCFOPERATING', 'CFNETINCREASECASH', 'CFOCFTCF', 'CFOTHOPCF',
    'CFPROFITOFYEAR', 'CL', 'CLDERIVA', 'CLHELDFORSALE', 'CLOTH', 'CLTAX', 'COGS',
    'CR', 'CRDC', 'DEBT', 'DEBTEV', 'DEBTTOASSETS', 'DEBTTOEBITDA', 'DEBTTOEQUITY',
    'DEPRIC', 'DOOMSDAY', 'EBITDAGLOB', 'ERPT', 'ERWCT', 'EV', 'EVEBIT', 'EVEBITDA',
    'EVGI', 'EVIC', 'EVNS', 'EVOCF', 'EVTA', 'EXPADMIN', 'EXPCHNGINVENT', 'EXPORTR',
    'EXPOTHBYNAT', 'EXPSELLING', 'EXPTAXCONTR', 'EXPWORKCAPITALIZED', 'EXTRESULT',
    'FA', 'FAT', 'FINRESULT', 'FINRESULTCOST', 'FINRESULTCOSTINT', 'FINRESULTCOSTOTH',
    'FINRESULTIN', 'FINRESULTINDIV', 'FINRESULTININTEREST', 'FINRESULTINOTH',
    'FINRESULTSHARE', 'FINVEST', 'FINVESTASSOC', 'FINVESTDERIV', 'FINVESTFORSALE',
    'FINVESTOTH', 'FINVESTPROP', 'FINVESTSUBS', 'GPM', 'GROSSPROF', 'ICR', 'INPROGR',
    'INT', 'INTDEVCOST', 'INTGOODW', 'INTOTH', 'INV', 'INVDEV', 'INVENTORYTURN',
    'INVFINISHED', 'INVOTH', 'INVRAW', 'INVWIP', 'IRCPR', 'IRLR', 'IRNIIT', 'IRNPET',
    'IRRADIOT', 'IRUER', 'ISAENS', 'ISDANS', 'ISIPNS', 'ISITNS', 'ISSEBNS', 'ISSUED',
    'LEVERAGE', 'LRCFO', 'LRCR', 'LTDC', 'LTDCF', 'LTDEBT', 'LTL', 'LTLDEFERRED',
    'LTLDERIVA', 'LTLOTH', 'LTLPAYABLE', 'LTLPROVISION', 'MARKETCAP/EBITDA',
    'MATERIAL', 'MAX', 'MCAP/EQ', 'MIN', 'MKCP', 'MMEPS', 'MMPEBIT', 'MMPER',
    'MMPGI', 'MMPIC', 'MMPOCF', 'MMPSA', 'MMPTA', 'NBSACCRUALS', 'NBSADJ', 'NBSADJDEPR',
    'NBSADJOTHNC', 'NBSADMIN', 'NBSCFCHNG', 'NBSCFCHNGADVBANK', 'NBSCFCHNGADVCUST',
    'NBSCFCHNGDEPO', 'NBSCFCHNGDEPOBANK', 'NBSCFCHNGDEPOCUST', 'NBSCFCHNGLOAN',
    'NBSCFCHNGOTHLIAB', 'NBSCFCHNGOTHSEC', 'NBSCFNCFFINANCEDIVPAY', 'NBSCFNCFFINANCEFUNDP',
    'NBSCFNCFFINANCEFUNDS', 'NBSCFNCFFINANCEORD', 'NBSCFNCFFINANCEOTH',
    'NBSCFNCFFINANCESUBORD', 'NBSCFNCFFINANCETREAP', 'NBSCFNCFINVESTOTHINV',
    'NBSCFNCFINVESTPOFPR', 'NBSCFNCFINVESTSALPR', 'NBSCFNCFINVESTSUBAQ',
    'NBSCFNCFINVESTSUBDI', 'NBSCFNP', 'NBSCUST', 'NBSCUSTS', 'NBSDEFIT', 'NBSDEOPBANK',
    'NBSDEOPBANKS', 'NBSDEPO', 'NBSDEPOCUST', 'NBSDEPOCUSTS', 'NBSDEPRIC', 'NBSDIVINC',
    'NBSDUECB', 'NBSHELDFSDO', 'NBSINVASSOC', 'NBSINVESTSEC', 'NBSISSUEDEBT',
    'NBSLOANBANKS', 'NBSLOANS', 'NBSNETFEE', 'NBSNETFEEEXP', 'NBSNETFEEINC', 'NBSNETIMP',
    'NBSNETIMPFINASST', 'NBSNETINT', 'NBSNETINTEXP', 'NBSNETINTINC', 'NBSNGOTH',
    'NBSNGXCHGDIFF', 'NBSOTHEQ', 'NBSOTHERAST', 'NBSOTHERFASSET', 'NBSOTHERLIAB',
    'NBSOTHNONOPINC', 'NBSOTHOPEXP', 'NBSOTHOPINC', 'NBSOTHRES', 'NBSPROVISIONS',
    'NBSSUBORDIN', 'NBSTEL', 'NCDEFFERED', 'NCDEFFEREDOTHER', 'NCDEFFEREDTAX',
    'NCREC', 'NCRECOTHER', 'NCRECRELAT', 'NETCASH', 'NET_DEBT', 'NISACCRULACC',
    'NISACCRULDEFIN', 'NISACCRULOTH', 'NISADMIN', 'NISBONDDEBT', 'NISBORROW',
    'NISCLAIMS', 'NISCLAIMSBROSBEN', 'NISCLAIMSCLAIMSREINS', 'NISCLAIMSGCHCONTR',
    'NISETFEEEXP', 'NISEXPENSECONTR', 'NISEXPRENDER', 'NISEXTEXP', 'NISEXTRESULT',
    'NISFA', 'NISFAAFSD', 'NISFAOTHERFASSET', 'NISINSLIAB', 'NISINTGOODW', 'NISINTOTH',
    'NISINV', 'NISINVASSOC', 'NISINVESTINC', 'NISINVPROP', 'NISNETPREM', 'NISNGFAIRVALUE',
    'NISNGFINHELDFS', 'NISOTH', 'NISOTHCOST', 'NISOTHLIAB', 'NISOTHOPINC', 'NISOTHRES',
    'NISPENSIONOBL', 'NISPREMREINS', 'NISPREMREV', 'NISREC', 'NISRECINSUR', 'NISRECINSURDIR',
    'NISRECINSURREINS', 'NISRECOTH', 'NISREINSLIAB', 'NISSEOWNOTH', 'NISSUBORDIN',
    'NISTANGOTHER', 'NISTECHFUND', 'NISTECHFUNDINS', 'NISTECHFUNDREINS', 'NISTLE',
    'NIT', 'NP', 'NPMINT', 'NPTOOWN', 'NS', 'OEXTI', 'OIT', 'OP', 'OPM', 'OREV', 'OTHCOST',
    'OTHCOSTS', 'OTHCURR', 'OTHEOPNET', 'OTHEQ', 'OTHFIX', 'OTHLIAB', 'OTHNETRE', 'OTLONGLIA',
    'P/BR', 'PERSON', 'PERSONSOCIAL', 'PERSONWAGE', 'PRCFA', 'PRCFR', 'PRCI', 'PRCRE',
    'PREBITDA', 'PRETAX', 'PROFITRESERV', 'PROROA', 'PROVIS', 'QR', 'REC', 'RECDOUBT',
    'RECOTHER', 'RECRELATED', 'RECTAX', 'RECTRADE', 'ROA', 'ROAA', 'ROC', 'ROE', 'ROEA',
    'ROS', 'RT', 'SE', 'SEC', 'SECDERIVAT', 'SECFORSALE', 'SECHELDMAT', 'SECOTH', 'SEMIN',
    'SEOWN', 'SEOWNFOREIGNCURR', 'SEOWNOTH', 'SEOWNREVALUATION', 'SEOWNTREASURY', 'SLOAN',
    'STDEBT', 'TANG', 'TANGLAND', 'TANGOTHER', 'TANGVECH', 'TAX', 'TAXDUE', 'TL', 'TLE',
    'TR', 'TRAR', 'TRBV', 'TRCE', 'TRCFO', 'TRCREDIT', 'TRCREDITOTH', 'TRCREDITTRADE',
    'TREBITDA', 'TRGP', 'TRINV', 'TRNSR', 'TRPPE', 'TRSE', 'TRTA', 'TRWC', 'TS']

keys_drop = [
    "_type", "auditedStatus", "consolidatedStatus", "countryCode",
    "displayCurrency", "multiple", "originalCurrency", "period",
    "stmtCode", "stmtId", "source"]
	
"""
cols_fin_rename = {
	'ACCRUE': 'Prepayments, accrued income and other deferred current assets',
	'ACCRUL': 'Deferred revenue, accrued expenses and other deferred current liabilities ',
	'AFTERTAX': 'Profit (Loss) from continuing operations',
	'AFTERTAXDISC': 'Profit (Loss) from discontinued operations',
	'AFTERTAXTOTAL': 'Comprehensive Income',
	'ART': 'Trade Receivable Turnover',
	'ASSETFORSALE':
	'Assets of disposal group classified as held for sale', 'AT': 'Total Asset Turnover', 'BONDDEBT': 'Debts on issue of bonds', 'BOOKVALUE': 'Bookvalue (BV)', 'BRAYA': 'Yield on Earning Assets (YEA)', 'BRCIR': 'Cost to Income Ratio', 'BRDCT': 'Deposits from Customers Trend', 'BRDCTO': 'Deposits Trend', 'BRER': 'Bank Efficiency Ratio', 'BRERA': 'Earning Assets', 'BRLACT': 'Loans and Advances to Customers Trend', 'BRLACTO': 'Loans and Advances Trend', 'BRLADR': 'Liquid Assets to Deposits Ratio', 'BRLADRO': 'Liquid Assets to Deposits From Customers Ratio', 'BRLAR': 'Loans to Asset Ratio', 'BRLARO': 'Loans to Customers to Asset Ratio', 'BRLDR': 'Loans to Deposits Ratio', 'BRLDRO': 'Loans to Customers to Deposits From Customers', 'BRNFCIT': 'Net Fee and Commission Income Trend', 'BRNIIT': 'Net Interest Income Trend', 'BRNIM': 'Net Interest Margin', 'BSCA': 'Cash / Total Assets', 'BSCLTL': 'Current Liabilities/Total Liabilities', 'BSFATA': 'Fixed assets/Total Assets', 'BSITA': 'Inventories/Total Assets', 'BSPROFIT': 'Profit or loss for the period', 'BSRTA': 'Receivables / Total Assets', 'CA': 'Current Assets', 'CAT': 'Current Asset Turnover', 'CBIO': 'Current biological assets', 'CE': 'Cash and cash equivalents', 'CECASH': 'Cash at banks and on hand', 'CEDEPOSIT': 'Short-term deposits', 'CEMPL': 'Capital Employed', 'CFADJDISCONTOP': 'Adjustments for: Gain on sale of discontinued operations', 'CFADJFINRESULTCOST': 'Adjustments for: Finance expenses', 'CFADJFINRESULTIN': 'Adjustments for: Finance income', 'CFADJGAINPROP': 'Adjustments for: Gain on sale of property, plant and equipment', 'CFADJIMPINTAN': 'Adjustments for: Impairment loss on intangible assets', 'CFADJIMPREC': 'Adjustments for: Impairment loss on trade receivables', 'CFADJIMPTANK': 'Adjustments for: Impairment losses on property, plant and equipment', 'CFADJINTAN': 'Adjustments for: Amortization of intangible assets', 'CFADJOTHADJ': 'Adjustments for: Other adjustments', 'CFADJTANG': 'Depreciation and impairment of property, plant and equipment', 'CFCAPEX': 'CAPEX', 'CFCASH': 'Cash generated from operations', 'CFCASHBEGIN': 'Cash at the beginning of the period', 'CFCASHEND': 'Cash at the end of the period', 'CFCASHFOREX': 'Exchange gains (losses) on cash and cash equivalents', 'CFCFFTCF': 'Financing Cash Flow to Total Cash Flow', 'CFCFITCF': 'Investing Cash Flow to Total Cash Flow', 'CFCHNGBIOLOG': 'Changes in: Current biological assets due to sales', 'CFCHNGDEFERRED': 'Changes in: Deferred income', 'CFCHNGINV': 'Changes in: Inventories', 'CFCHNGOTH': 'Changes in: Other changes', 'CFCHNGPREP': 'Changes in: Prepayments', 'CFCHNGPROV': 'Changes in: Provisions and employee benefits', 'CFCHNGREC': 'Changes in: Trade and other payables', 'CFCHNGTRADE': 'Changes in: Trade and other receivables', 'CFFCF': 'Free cash flow', 'CFFINBOR': 'Proceeds from borrowings', 'CFFINCOSTLOAN': 'Payments of transaction costs related to loans and borrowings', 'CFFINORDINAR': 'Proceeds from issuance of ordinary shares', 'CFFINOTHEQUITY': 'Proceeds from issuance of other equity instruments', 'CFFINOTHFINACT': 'Other financing activity cash flow', 'CFFINPAIDDIV': 'Dividends paid', 'CFFINPAIDINT': 'Interest paid', 'CFFINPAYLEASE': 'Payments of finance lease liabilities', 'CFFINREPAYBOR': 'Repayment of borrowings', 'CFFINSALEOWN': 'Proceeds from sale of own shares', 'CFFINTREASURY': 'Purchase of treasury shares', 'CFINCOMETAX': 'Income tax paid', 'CFINVESTACQUIRE': 'Acquisition of subsidiary', 'CFINVESTDEVEXP': 'Development expenditures', 'CFINVESTDIVIDREC': 'Dividends received', 'CFINVESTFININST': 'Purchase of financial instruments', 'CFINVESTINTREC': 'Interest received', 'CFINVESTINVPROP': 'Purchase of investment properties', 'CFINVESTNTANG': 'Purchase of intangible assets', 'CFINVESTOTHINVEST': 'Other investing activity cash flows', 'CFINVESTPROP': 'Purchase of property, plant and equipment', 'CFINVESTSALEFININST': 'Proceeds from sale of financial instruments', 'CFINVESTSALEPROP': 'Proceeds from sale of property, plant and equipment', 'CFNCFFINANCE': 'Net cash flow from (used in) financing activities', 'CFNCFINVEST': 'Net cash flow from (used in) investing activities', 'CFNCFOPERATING': 'Net cash flow from (used in) operating activities', 'CFNETINCREASECASH': 'Net increase (decrease) in cash and cash equivalents', 'CFOCFTCF': 'Operating Cash Flow to Total Cash Flow', 'CFOTHOPCF': 'Other operating activity cash flows', 'CFPROFITOFYEAR': 'Net Profit', 'CL': 'Current Liabilities', 'CLDEFERRTAX': 'Deferred income tax liabilities', 'CLDERIVA': 'Current derivative financial instruments', 'CLHELDFORSALE': 'Liabilities of disposal group classified as held for sale', 'CLOTH': 'Other current financial liabilities', 'CLTAX': 'Current income tax liabilities', 'COEXCDIF': 'Results from exchange differences on translation', 'COGS': 'Cost of Goods Sold', 'COINVEQ': 'Results from investments in equity', 'COMBEN': 'Remeasurements of defined benefit plans', 'COMFINA': 'Revaluation of financial instruments', 'COMHED': 'Results from cash flow hedges', 'COMINTAX': 'Income tax relating to components comprehensive results', 'COMJOIN': 'Share of other results from associates and joint ventures', 'COMOTH': 'Other comprehensive Results ', 'COMPREHENSOTH': 'Other comprehensive result for the period, net of tax', 'COMREVF': 'Results from Revaluation of fixed assets', 'COMSAFI': 'Results from available-for-sale financial assets', 'COMTOOWN': '- Comprehensive Income attributable to Owers', 'CR': 'Current Ratio', 'CRDC': 'Operating Cash Flow to Debt', 'DEBT': 'Debt', 'DEBTEV': 'Debt / Enterprise Value ', 'DEBTTOASSETS': 'Debt to total assets ratio', 'DEBTTOEBITDA': 'Debt / EBITDA', 'DEBTTOEQUITY': 'Debt to equity ratio', 'DEPRIC': 'Depreciation, amortization and impairment charges', 'DOMESTIC': 'Net Domestic Sales Revenue', 'DOOMSDAY': "Doom's day ratio", 'EBITDAGLOB': 'EBITDA', 'ERPT': 'Trade Payables Turnover', 'ERWCT': 'Working Capital Turnover', 'EV': 'Enterprise value ', 'EVEBIT': 'Enterprise value/EBIT', 'EVEBITDA': 'Enterprise Value/EBITDA', 'EVGI': 'Enterprise value/Gross Profit', 'EVIC': 'Enterprise value / Capital Employed', 'EVNS': 'Enterprise value/Net Sales', 'EVOCF': 'Enterprise value/Operating Cashflow', 'EVTA': 'Enterprise value/Total Assets', 'EXPADMIN': 'Administrative expenses', 'EXPADVERT': 'Advertising costs', 'EXPCHNGINVENT': 'Changes in inventories of finished goods and work in progress', 'EXPITEXP': 'IT expenses', 'EXPORT': 'Net Export Sales Revenue', 'EXPORTR': 'Export proportion', 'EXPOTHBYNAT': 'Other costs by nature', 'EXPRDCOST': 'R&D costs', 'EXPSELLING': 'Selling and distribution expenses', 'EXPTAXCONTR': 'Tax and contributions', 'EXPTRANSP': 'Transportation costs', 'EXPWORKCAPITALIZED': 'Work performed and capitalized', 'EXTRESULT': 'Extraordinary Non-Operating Items', 'FA': 'Non-current assets ', 'FAT': 'Non Current Assets Turnover ', 'FINRESULT': 'Financial result', 'FINRESULTCOST': 'Finance expenses', 'FINRESULTCOSTFOREX': 'Foreign exchange loss', 'FINRESULTCOSTINT': 'Interest expense', 'FINRESULTCOSTOTH': 'Other financial expenses', 'FINRESULTIN': 'Finance income', 'FINRESULTINDIV': 'Dividend income', 'FINRESULTINFOREX': 'Foreign exchange gain', 'FINRESULTININTEREST': 'Interest income', 'FINRESULTINOTH': 'Other financial income', 'FINRESULTSHARE': 'Share of profit (loss) of associates', 'FINVEST': 'Long-term financial assets', 'FINVESTASSOC': 'Investments in associates', 'FINVESTDERIV': 'Derivative financial instruments', 'FINVESTFAIRVALUE': 'Financial assets at fair value through profit or loss', 'FINVESTFORSALE': 'Available-for-sale financial assets (LT)', 'FINVESTHELDMAT': 'Financial assets held-to-maturity', 'FINVESTOTH': 'Other non-current financial assets', 'FINVESTPROP': 'Investment properties', 'FINVESTSUBS': 'Investments in subsidiaries', 'GPM': 'Gross Profit Margin', 'GROSSPROF': 'Gross profit', 'ICR': 'Interest Coverage Ratio', 'INPROGR': 'Construction in progress', 'INT': 'Intangible assets and goodwill', 'INTDEVCOST': 'Development costs', 'INTGOODW': 'Goodwill', 'INTOTH': 'Other intangible assets', 'INTOWNSOFT': 'Own developed computer software', 'INTTRADM': 'Trademarks and licenses', 'INV': 'Inventories', 'INVDEV': 'Non-current loans and borrowings', 'INVENTORYTURN': 'Inventory Turnover', 'INVFINISHED': 'Finished goods', 'INVOTH': 'Other inventories', 'INVRAW': 'Raw materials', 'INVWIP': 'Work in progress', 'IRCPR': 'Ceeded Premium Ratio', 'IRFCT': 'Fees and Commissions Trend', 'IRLR': 'Loss Ratio', 'IRNIIT': 'Net Investment Income Trend', 'IRNPET': 'Net Premiums Earned Trend', 'IRRADIOT': 'Receivables Arising Out Of Direct Insurance Operations Trend', 'IRUER': 'Underwriting Expenses Ratio', 'ISAENS': 'Administrative Expenses/Net Sales', 'ISDANS': 'Depreciation and Amortization/Net sales', 'ISIPNS': 'Interest paid/Net sales', 'ISITNS': 'Income tax/Net sales', 'ISSEBNS': 'Salaries and Employee Benefits/Net sales', 'ISSUED': 'Issued capital', 'ISSUEDORD': 'Ordinary shares', 'ISSUEDPREF': 'Preferred shares', 'LEVERAGE': 'Assets to Equity Ratio', 'LRCFO': 'Operating Cash Flow Ratio', 'LRCR': 'Cash Ratio', 'LTDC': 'Long Term Debt to Capital Employed', 'LTDCF': 'Net Cash Flow to Debt ', 'LTDEBT': 'Long term Debt', 'LTL': 'Non-current liabilities', 'LTLDEFERRED': 'Deferred revenue, accrued expenses and other deferred non-current liabilities ', 'LTLDERIVA': 'Non-current derivative financial instruments', 'LTLOTH': 'Other non-current financial liabilities', 'LTLPAYABLE': 'Other non-current payables', 'LTLPROVISION': 'Provisions for other liabilities and charges', 'LTTRADPAY': 'Non-current trade payables', 'MARKETCAP/EBITDA': 'Market Capitalization/EBITDA', 'MATERIAL': 'Raw materials and consumables used', 'MAX': 'Upper Limit of Revenue Range', 'MCAP/EQ': "Market capitalization/shareholders' equity", 'MIN': 'Lower Limit of Revenue Range', 'MKCP': 'Market Capitalization', 'MMEPS': 'EPS', 'MMPEBIT': 'Market Capitalization/EBIT', 'MMPER': 'P/E', 'MMPGI': 'Market Capitalization/Gross Profit', 'MMPIC': 'Market Capitalization / Capital Employed', 'MMPOCF': 'Market Capitalization/Operating Cashflow', 'MMPSA': 'Market Capitalization/Net Sales (Price Sales Ratio)', 'MMPTA': 'Market Capitalization/Total Assets', 'nan': 'Net current assets', 'NCBIO': 'Non-current biological assets', 'NCDEFFERED': 'Deferred assets', 'NCDEFFEREDOTHER': 'Other non-current deferred assets', 'NCDEFFEREDTAX': 'Non-current deferred tax assets', 'NCREC': 'Non-current Trade and other receivables', 'NCRECDOUBT': 'Doubtful receivables', 'NCRECOTHER': 'Other non-current receivables', 'NCRECRELAT': 'Receivables from related parties', 'NCRECTRADE': 'Non-current trade receivables', 'NET_DEBT': 'Net Debt', 'NETCASH': 'Net Cash', 'NIT': 'Net Profit Trend ', 'NP': 'NET PROFIT/LOSS FOR THE PERIOD', 'NPMINT': '   -  Profit (loss) attributable to Minority Interests', 'NPTOOWN': '-  Profit (loss) attributable to Owners ', 'NS': 'Net sales revenue', 'OEXTI': 'Other Extraordinary Items', 'OIT': 'Operating Profit Trend', 'OP': 'Operating profit/loss (EBIT)', 'OPM': 'Operating Profit Margin (ROS)', 'OREV': 'Other operating income', 'OTHCOST': 'Other operating expenses', 'OTHCOSTS': 'Other expenses', 'OTHCURR': 'Other current assets', 'OTHEOPNET': 'Net - Other operating result', 'OTHEQ': 'Other components of equity', 'OTHFIX': 'Other non-current assets', 'OTHINCOME': 'Other income', 'OTHLIAB': 'Other current liabilities', 'OTHNET': 'Other Net Operating Results', 'OTHNETRE': 'Net - other non-operating result', 'OTLONGLIA': 'Other non-current liabilities', 'OUTSIDE': '-  Comprehensive Income attributable to Minority Interests', 'P/BR': 'Market Capitalization/Book Value', 'PERSON': 'Employee benefit expense', 'PERSONOTH': 'Other employee benefit expense', 'PERSONSOCIAL': 'Social security costs', 'PERSONWAGE': 'Wages and salaries', 'PRCFA': 'Operating Cash Flow to Assets', 'PRCFR': 'Operating Cash Flow to Revenue', 'PRCI': 'Operating Cash Flow to EBIT', 'PRCRE': 'Operating Cash Flow to Equity', 'PREBITDA': 'EBITDA Margin', 'PRETAX': 'Profit before income tax', 'PROFITRESERV': 'Retained earnings', 'PROROA': 'Operating ROA', 'PROVIS': 'Provisions for other liabilities and charges', 'QR': 'Quick ratio', 'REC': 'Trade and other receivables', 'RECDOUBT': 'Doubtful receivables', 'RECOTHER': 'Other current receivables', 'RECRELATED': 'Receivables from related parties', 'RECTAX': 'Tax receivables', 'RECTRADE': 'Current trade receivables', 'ROA': 'Return on Assets (ROA)', 'ROAA': 'Annualised Return on Assets (ROA) ', 'ROC': 'Return on Capital Employed', 'ROE': 'Return on Equity (ROE)', 'ROEA': 'Annualised Return on Equity (ROE)', 'ROS': 'Net Profit Margin', 'RT': 'Net Sales Revenue Trend ', 'SE': 'Total equity', 'SEC': 'Short term Financial assets', 'SECDERIVAT': 'Derivative financial instruments', 'SECFAIRVALUE': 'Financial assets at fair value through profit or loss', 'SECFORSALE': 'Available-for-sale financial assets (ST)', 'SECHELDMAT': 'Financial assets held-to-maturity', 'SECOTH': 'Other current financial assets', 'SEMIN': 'Minority interest', 'SEOWN': 'Equity attributable to owners of the parent', 'SEOWNCFHEDGE': 'Cashflow hedge reserve', 'SEOWNDUETOCONS': 'Changes due to consolidation', 'SEOWNFOREIGNCURR': 'Foreign currency translation reserve', 'SEOWNHELDFORSALE': 'Reserves of a disposal group classified as held for sale', 'SEOWNOTH': 'Other reserves', 'SEOWNPREMIUM': 'Share premium', 'SEOWNREVALUATION': 'Revaluation reserve', 'SEOWNTREASURY': 'Treasury shares', 'SLOAN': 'Current loans and borrowings', 'STDEBT': 'Short Term Debt', 'TANG': 'Property, plant and equipment', 'TANGFIXT': 'Fixtures and fittings', 'TANGLAND': 'Land and buildings', 'TANGOTHER': 'Other property, plant and equipment', 'TANGVECH': 'Vehicles and machinery', 'TAX': 'Income tax', 'TAXDUE': 'Tax difference due to consolidation', 'TL': 'Total Liabilities', 'TLE': 'Total Equity and liabilities', 'TR': 'Total operating revenue', 'TRAR': 'Accounts Receivables Trend', 'TRBV': 'Bookvalue Trend', 'TRCE': 'Capital Expenditures Trend', 'TRCFO': 'Operating Cash Flow Trend', 'TRCREDIT': 'Trade and other payables', 'TRCREDITOTH': 'Other current payables', 'TRCREDITRELATED': 'Payables due to related parties', 'TRCREDITTRADE': 'Current trade payables', 'TREBITDA': 'EBITDA Trend', 'TRGP': 'Gross Profit Trend', 'TRINV': 'Inventory Trend', 'TRNSR': 'Total Operating Revenue Trend', 'TRPPE': 'Net Property, Plant and Equipment (PP&E) Trend', 'TRSE': "Shareholders' Equity Trend", 'TRTA': 'Total Assets Trend', 'TRWC': 'Working Capital', 'TS': 'Assets'}
"""

cols_fin_rename = {
'ACCRUE': 'Prepayments, accrued income and other deferred current assets',
'ACCRUL': 'Deferred revenue, accrued expenses and other deferred current liabilities',
'AFTERTAX': 'Profit (Loss) from continuing operations',
'AFTERTAXDISC': 'Profit (Loss) from discontinued operations',
'AFTERTAXTOTAL': 'Comprehensive Income',
'ART': 'Trade Receivable Turnover',
'ASSETFORSALE': 'Assets of disposal group classified as held for sale',
 'AT': 'Total Asset Turnover',
 'BONDDEBT': 'Debts on issue of bonds',
 'BOOKVALUE': 'Bookvalue (BV)',
 'BRAYA': 'Yield on Earning Assets (YEA)',
 'BRCIR': 'Cost to Income Ratio',
 'BRDCT': 'Deposits from Customers Trend',
 'BRDCTO': 'Deposits Trend',
 'BRER': 'Bank Efficiency Ratio',
 'BRERA': 'Earning Assets',
 'BRLACT': 'Loans and Advances to Customers Trend',
 'BRLACTO': 'Loans and Advances Trend',
 'BRLADR': 'Liquid Assets to Deposits Ratio',
 'BRLADRO': 'Liquid Assets to Deposits From Customers Ratio',
 'BRLAR': 'Loans to Asset Ratio',
 'BRLARO': 'Loans to Customers to Asset Ratio',
 'BRLDR': 'Loans to Deposits Ratio',
 'BRLDRO': 'Loans to Customers to Deposits From Customers',
 'BRNFCIT': 'Net Fee and Commission Income Trend',
 'BRNIIT': 'Net Interest Income Trend',
 'BRNIM': 'Net Interest Margin',
 'BSCA': 'Cash / Total Assets',
 'BSCLTL': 'Current Liabilities/Total Liabilities',
 'BSFATA': 'Fixed assets/Total Assets',
 'BSITA': 'Inventories/Total Assets',
 'BSPROFIT': 'Profit or loss for the period',
 'BSRTA': 'Receivables / Total Assets',
 'CA': 'Current Assets',
 'CAT': 'Current Asset Turnover',
 'CBIO': 'Current biological assets',
 'CE': 'Cash and cash equivalents',
 'CECASH': 'Cash at banks and on hand',
 'CEDEPOSIT': 'Short-term deposits',
 'CEMPL': 'Capital Employed',
 'CFADJDISCONTOP': 'Adjustments for: Gain on sale of discontinued operations',
 'CFADJFINRESULTCOST': 'Adjustments for: Finance expenses',
 'CFADJFINRESULTIN': 'Adjustments for: Finance income',
 'CFADJGAINPROP': 'Adjustments for: Gain on sale of property, plant and equipment',
 'CFADJIMPINTAN': 'Adjustments for: Impairment loss on intangible assets',
 'CFADJIMPREC': 'Adjustments for: Impairment loss on trade receivables',
 'CFADJIMPTANK': 'Adjustments for: Impairment losses on property, plant and equipment',
 'CFADJINTAN': 'Adjustments for: Amortization of intangible assets',
 'CFADJOTHADJ': 'Adjustments for: Other adjustments',
 'CFADJTANG': 'Depreciation and impairment of property, plant and equipment',
 'CFCAPEX': 'CAPEX',
 'CFCASH': 'Cash generated from operations',
 'CFCASHBEGIN': 'Cash at the beginning of the period',
 'CFCASHEND': 'Cash at the end of the period',
 'CFCASHFOREX': 'Exchange gains (losses) on cash and cash equivalents',
 'CFCFFTCF': 'Financing Cash Flow to Total Cash Flow',
 'CFCFITCF': 'Investing Cash Flow to Total Cash Flow',
 'CFCHNGBIOLOG': 'Changes in: Current biological assets due to sales',
 'CFCHNGDEFERRED': 'Changes in: Deferred income',
 'CFCHNGINV': 'Changes in: Inventories',
 'CFCHNGOTH': 'Changes in: Other changes',
 'CFCHNGPREP': 'Changes in: Prepayments',
 'CFCHNGPROV': 'Changes in: Provisions and employee benefits',
 'CFCHNGREC': 'Changes in: Trade and other payables',
 'CFCHNGTRADE': 'Changes in: Trade and other receivables',
 'CFFCF': 'Free cash flow',
 'CFFINBOR': 'Proceeds from borrowings',
 'CFFINCOSTLOAN': 'Payments of transaction costs related to loans and borrowings',
 'CFFINORDINAR': 'Proceeds from issuance of ordinary shares',
 'CFFINOTHEQUITY': 'Proceeds from issuance of other equity instruments',
 'CFFINOTHFINACT': 'Other financing activity cash flow',
 'CFFINPAIDDIV': 'Dividends paid',
 'CFFINPAIDINT': 'Interest paid',
 'CFFINPAYLEASE': 'Payments of finance lease liabilities',
 'CFFINREPAYBOR': 'Repayment of borrowings',
 'CFFINSALEOWN': 'Proceeds from sale of own shares',
 'CFFINTREASURY': 'Purchase of treasury shares',
 'CFINCOMETAX': 'Income tax paid',
 'CFINVESTACQUIRE': 'Acquisition of subsidiary',
 'CFINVESTDEVEXP': 'Development expenditures',
 'CFINVESTDIVIDREC': 'Dividends received',
 'CFINVESTFININST': 'Purchase of financial instruments',
 'CFINVESTINTREC': 'Interest received',
 'CFINVESTINVPROP': 'Purchase of investment properties',
 'CFINVESTNTANG': 'Purchase of intangible assets',
 'CFINVESTOTHINVEST': 'Other investing activity cash flows',
 'CFINVESTPROP': 'Purchase of property, plant and equipment',
 'CFINVESTSALEFININST': 'Proceeds from sale of financial instruments',
 'CFINVESTSALEPROP': 'Proceeds from sale of property, plant and equipment',
 'CFNCFFINANCE': 'Net cash flow from (used in) financing activities',
 'CFNCFINVEST': 'Net cash flow from (used in) investing activities',
 'CFNCFOPERATING': 'Net cash flow from (used in) operating activities',
 'CFNETINCREASECASH': 'Net increase (decrease) in cash and cash equivalents',
 'CFOCFTCF': 'Operating Cash Flow to Total Cash Flow',
 'CFOTHOPCF': 'Other operating activity cash flows',
 'CFPROFITOFYEAR': 'Net Profit',
 'CL': 'Current Liabilities',
 'CLDEFERRTAX': 'Deferred income tax liabilities',
 'CLDERIVA': 'Current derivative financial instruments',
 'CLHELDFORSALE': 'Liabilities of disposal group classified as held for sale',
 'CLOTH': 'Other current financial liabilities',
 'CLTAX': 'Current income tax liabilities',
 'COEXCDIF': 'Results from exchange differences on translation',
 'COGS': 'Cost of Goods Sold',
 'COINVEQ': 'Results from investments in equity',
 'COMBEN': 'Remeasurements of defined benefit plans',
 'COMFINA': 'Revaluation of financial instruments',
 'COMHED': 'Results from cash flow hedges',
 'COMINTAX': 'Income tax relating to components comprehensive results',
 'COMJOIN': 'Share of other results from associates and joint ventures',
 'COMOTH': 'Other comprehensive Results ',
 'COMPREHENSOTH': 'Other comprehensive result for the period, net of tax',
 'COMREVF': 'Results from Revaluation of fixed assets',
 'COMSAFI': 'Results from available-for-sale financial assets',
 'COMTOOWN': '- Comprehensive Income attributable to Owers',
 'CR': 'Current Ratio',
 'CRDC': 'Operating Cash Flow to Debt',
 'DEBT': 'Debt',
 'DEBTEV': 'Debt / Enterprise Value ',
 'DEBTTOASSETS': 'Debt to total assets ratio',
 'DEBTTOEBITDA': 'Debt / EBITDA',
 'DEBTTOEQUITY': 'Debt to equity ratio',
 'DEPRIC': 'Depreciation, amortization and impairment charges',
 'DOMESTIC': 'Net Domestic Sales Revenue',
 'DOOMSDAY': "Doom's day ratio",
 'EBITDAGLOB': 'EBITDA',
 'ERPT': 'Trade Payables Turnover',
 'ERWCT': 'Working Capital Turnover',
 'EV': 'Enterprise value ',
 'EVEBIT': 'Enterprise value/EBIT',
 'EVEBITDA': 'Enterprise Value/EBITDA',
 'EVGI': 'Enterprise value/Gross Profit',
 'EVIC': 'Enterprise value / Capital Employed',
 'EVNS': 'Enterprise value/Net Sales',
 'EVOCF': 'Enterprise value/Operating Cashflow',
 'EVTA': 'Enterprise value/Total Assets',
 'EXPADMIN': 'Administrative expenses',
 'EXPADVERT': 'Advertising costs',
 'EXPCHNGINVENT': 'Changes in inventories of finished goods and work in progress',
 'EXPITEXP': 'IT expenses',
 'EXPORT': 'Net Export Sales Revenue',
 'EXPORTR': 'Export proportion',
 'EXPOTHBYNAT': 'Other costs by nature',
 'EXPRDCOST': 'R&D costs',
 'EXPSELLING': 'Selling and distribution expenses',
 'EXPTAXCONTR': 'Tax and contributions',
 'EXPTRANSP': 'Transportation costs',
 'EXPWORKCAPITALIZED': 'Work performed and capitalized',
 'EXTRESULT': 'Extraordinary Non-Operating Items',
 'FA': 'Non-current assets ',
 'FAT': 'Non Current Assets Turnover ',
 'FINRESULT': 'Financial result',
 'FINRESULTCOST': 'Finance expenses',
 'FINRESULTCOSTFOREX': 'Foreign exchange loss',
 'FINRESULTCOSTINT': 'Interest expense',
 'FINRESULTCOSTOTH': 'Other financial expenses',
 'FINRESULTIN': 'Finance income',
 'FINRESULTINDIV': 'Dividend income',
 'FINRESULTINFOREX': 'Foreign exchange gain',
 'FINRESULTININTEREST': 'Interest income',
 'FINRESULTINOTH': 'Other financial income',
 'FINRESULTSHARE': 'Share of profit (loss) of associates',
 'FINVEST': 'Long-term financial assets',
 'FINVESTASSOC': 'Investments in associates',
 'FINVESTDERIV': 'Derivative financial instruments',
 'FINVESTFAIRVALUE': 'Financial assets at fair value through profit or loss',
 'FINVESTFORSALE': 'Available-for-sale financial assets (LT)',
 'FINVESTHELDMAT': 'Financial assets held-to-maturity',
 'FINVESTOTH': 'Other non-current financial assets',
 'FINVESTPROP': 'Investment properties',
 'FINVESTSUBS': 'Investments in subsidiaries',
 'GPM': 'Gross Profit Margin',
 'GROSSPROF': 'Gross profit',
 'ICR': 'Interest Coverage Ratio',
 'INPROGR': 'Construction in progress',
 'INT': 'Intangible assets and goodwill',
 'INTDEVCOST': 'Development costs',
 'INTGOODW': 'Goodwill',
 'INTOTH': 'Other intangible assets',
 'INTOWNSOFT': 'Own developed computer software',
 'INTTRADM': 'Trademarks and licenses',
 'INV': 'Inventories',
 'INVDEV': 'Non-current loans and borrowings',
 'INVENTORYTURN': 'Inventory Turnover',
 'INVFINISHED': 'Finished goods',
 'INVOTH': 'Other inventories',
 'INVRAW': 'Raw materials',
 'INVWIP': 'Work in progress',
 'IRCPR': 'Ceeded Premium Ratio',
 'IRFCT': 'Fees and Commissions Trend',
 'IRLR': 'Loss Ratio',
 'IRNIIT': 'Net Investment Income Trend',
 'IRNPET': 'Net Premiums Earned Trend',
 'IRRADIOT': 'Receivables Arising Out Of Direct Insurance Operations Trend',
 'IRUER': 'Underwriting Expenses Ratio',
 'ISAENS': 'Administrative Expenses/Net Sales',
 'ISDANS': 'Depreciation and Amortization/Net sales',
 'ISIPNS': 'Interest paid/Net sales',
 'ISITNS': 'Income tax/Net sales',
 'ISSEBNS': 'Salaries and Employee Benefits/Net sales',
 'ISSUED': 'Issued capital',
 'ISSUEDORD': 'Ordinary shares',
 'ISSUEDPREF': 'Preferred shares',
 'LEVERAGE': 'Assets to Equity Ratio',
 'LRCFO': 'Operating Cash Flow Ratio',
 'LRCR': 'Cash Ratio',
 'LTDC': 'Long Term Debt to Capital Employed',
 'LTDCF': 'Net Cash Flow to Debt ',
 'LTDEBT': 'Long term Debt',
 'LTL': 'Non-current liabilities',
 'LTLDEFERRED': 'Deferred revenue, accrued expenses and other deferred non-current liabilities ',
 'LTLDERIVA': 'Non-current derivative financial instruments',
 'LTLOTH': 'Other non-current financial liabilities',
 'LTLPAYABLE': 'Other non-current payables',
 'LTLPROVISION': 'Provisions for other liabilities and charges',
 'LTTRADPAY': 'Non-current trade payables',
 'MARKETCAP/EBITDA': 'Market Capitalization/EBITDA',
 'MATERIAL': 'Raw materials and consumables used',
 'MAX': 'Upper Limit of Revenue Range',
 'MCAP/EQ': "Market capitalization/shareholders' equity",
 'MIN': 'Lower Limit of Revenue Range',
 'MKCP': 'Market Capitalization',
 'MMEPS': 'EPS',
 'MMPEBIT': 'Market Capitalization/EBIT',
 'MMPER': 'P/E',
 'MMPGI': 'Market Capitalization/Gross Profit',
 'MMPIC': 'Market Capitalization / Capital Employed',
 'MMPOCF': 'Market Capitalization/Operating Cashflow',
 'MMPSA': 'Market Capitalization/Net Sales (Price Sales Ratio)',
 'MMPTA': 'Market Capitalization/Total Assets',
 'nan': 'Net current assets',
 'NCBIO': 'Non-current biological assets',
 'NCDEFFERED': 'Deferred assets',
 'NCDEFFEREDOTHER': 'Other non-current deferred assets',
 'NCDEFFEREDTAX': 'Non-current deferred tax assets',
 'NCREC': 'Non-current Trade and other receivables',
 'NCRECDOUBT': 'Doubtful receivables',
 'NCRECOTHER': 'Other non-current receivables',
 'NCRECRELAT': 'Receivables from related parties',
 'NCRECTRADE': 'Non-current trade receivables',
 'NET_DEBT': 'Net Debt',
 'NETCASH': 'Net Cash',
 'NIT': 'Net Profit Trend ',
 'NP': 'NET PROFIT/LOSS FOR THE PERIOD',
 'NPMINT': '   -  Profit (loss) attributable to Minority Interests',
 'NPTOOWN': '-  Profit (loss) attributable to Owners ',
 'NS': 'Net sales revenue',
 'OEXTI': 'Other Extraordinary Items',
 'OIT': 'Operating Profit Trend',
 'OP': 'Operating profit/loss (EBIT)',
 'OPM': 'Operating Profit Margin (ROS)',
 'OREV': 'Other operating income',
 'OTHCOST': 'Other operating expenses',
 'OTHCOSTS': 'Other expenses',
 'OTHCURR': 'Other current assets',
 'OTHEOPNET': 'Net - Other operating result',
 'OTHEQ': 'Other components of equity',
 'OTHFIX': 'Other non-current assets',
 'OTHINCOME': 'Other income',
 'OTHLIAB': 'Other current liabilities',
 'OTHNET': 'Other Net Operating Results',
 'OTHNETRE': 'Net - other non-operating result',
 'OTLONGLIA': 'Other non-current liabilities',
 'OUTSIDE': '-  Comprehensive Income attributable to Minority Interests',
 'P/BR': 'Market Capitalization/Book Value',
 'PERSON': 'Employee benefit expense',
 'PERSONOTH': 'Other employee benefit expense',
 'PERSONSOCIAL': 'Social security costs',
 'PERSONWAGE': 'Wages and salaries',
 'PRCFA': 'Operating Cash Flow to Assets',
 'PRCFR': 'Operating Cash Flow to Revenue',
 'PRCI': 'Operating Cash Flow to EBIT',
 'PRCRE': 'Operating Cash Flow to Equity',
 'PREBITDA': 'EBITDA Margin',
 'PRETAX': 'Profit before income tax',
 'PROFITRESERV': 'Retained earnings',
 'PROROA': 'Operating ROA',
 'PROVIS': 'Provisions for other liabilities and charges',
 'QR': 'Quick ratio',
 'REC': 'Trade and other receivables',
 'RECDOUBT': 'Doubtful receivables',
 'RECOTHER': 'Other current receivables',
 'RECRELATED': 'Receivables from related parties',
 'RECTAX': 'Tax receivables',
 'RECTRADE': 'Current trade receivables',
 'ROA': 'Return on Assets (ROA)',
 'ROAA': 'Annualised Return on Assets (ROA) ',
 'ROC': 'Return on Capital Employed',
 'ROE': 'Return on Equity (ROE)',
 'ROEA': 'Annualised Return on Equity (ROE)',
 'ROS': 'Net Profit Margin',
 'RT': 'Net Sales Revenue Trend ',
 'SE': 'Total equity',
 'SEC': 'Short term Financial assets',
 'SECDERIVAT': 'Derivative financial instruments',
 'SECFAIRVALUE': 'Financial assets at fair value through profit or loss',
 'SECFORSALE': 'Available-for-sale financial assets (ST)',
 'SECHELDMAT': 'Financial assets held-to-maturity',
 'SECOTH': 'Other current financial assets',
 'SEMIN': 'Minority interest',
 'SEOWN': 'Equity attributable to owners of the parent',
 'SEOWNCFHEDGE': 'Cashflow hedge reserve',
 'SEOWNDUETOCONS': 'Changes due to consolidation',
 'SEOWNFOREIGNCURR': 'Foreign currency translation reserve',
 'SEOWNHELDFORSALE': 'Reserves of a disposal group classified as held for sale',
 'SEOWNOTH': 'Other reserves',
 'SEOWNPREMIUM': 'Share premium',
 'SEOWNREVALUATION': 'Revaluation reserve',
 'SEOWNTREASURY': 'Treasury shares',
 'SLOAN': 'Current loans and borrowings',
 'STDEBT': 'Short Term Debt',
 'TANG': 'Property, plant and equipment',
 'TANGFIXT': 'Fixtures and fittings',
 'TANGLAND': 'Land and buildings',
 'TANGOTHER': 'Other property, plant and equipment',
 'TANGVECH': 'Vehicles and machinery',
 'TAX': 'Income tax',
 'TAXDUE': 'Tax difference due to consolidation',
 'TL': 'Total Liabilities',
 'TLE': 'Total Equity and liabilities',
 'TR': 'Total operating revenue',
 'TRAR': 'Accounts Receivables Trend',
 'TRBV': 'Bookvalue Trend',
 'TRCE': 'Capital Expenditures Trend',
 'TRCFO': 'Operating Cash Flow Trend',
 'TRCREDIT': 'Trade and other payables',
 'TRCREDITOTH': 'Other current payables',
 'TRCREDITRELATED': 'Payables due to related parties',
 'TRCREDITTRADE': 'Current trade payables',
 'TREBITDA': 'EBITDA Trend',
 'TRGP': 'Gross Profit Trend',
 'TRINV': 'Inventory Trend',
 'TRNSR': 'Total Operating Revenue Trend',
 'TRPPE': 'Net Property, Plant and Equipment (PP&E) Trend',
 'TRSE': "Shareholders' Equity Trend",
 'TRTA': 'Total Assets Trend',
 'TRWC': 'Working Capital',
 'TS': 'Assets'}



cols_tech_rename = {
    'acctErrFlag' : 'AccountErrorFlag',
    'beginDate' : 'BeginDate',
    'endDate' : 'EndDate',
    'fsYear' : 'FiscalYear',
    'isic' : 'ISIC',
    'lastUpdate' : 'LastUpdate',
    'originalStandardCode' : 'OriginalStandardCode',
    'outputStandardCode' : 'OutputStandardCode'}
cols_rename = {**cols_fin_rename, **cols_tech_rename}
known_cols = [
    'NIP', 'ISIC', 'FiscalYear', 'BeginDate', 'EndDate', 'LastUpdate',
    'OriginalStandardCode', 'OutputStandardCode', 'AccountErrorFlag']

################################################
################ REGISTER DATA #################
################################################

############ FLATTEN NESTED JSONS ##############
def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

################# PARSE AFFILIATES ################
def parse_affiliates(result: dict) -> dict:
    # PARSE AFFILIATES
    affiliates = []
    affiliates_percentage = []
    affiliates_count = 0
    affiliates_foreign = 0
    affiliates_emis = 0
    affiliateship_total = 0
    affiliateship_type = 0
    for key, value in result.items():
        if key.startswith('affiliateList_') and key.endswith('_affiliateNameLocal'):
            affiliates_count += 1
            for i, j in {
                    ', ExternalID: ' : '_affiliateExternalId',
                    ', ISIC: ' : '_affiliateIsic',
                    ', Percentage: ' : '_affiliateshipPercentage',
                    ', Type: ' : '_affiliateshipType'}.items():
                key_processed = key[:15] + j if len(key) == 34 else key[:16] + j
                affiliate = 'Name: ' + value
                info = i + str(result[key_processed])
                affiliate += info
            affiliates.append(affiliate)
        if key.startswith('affiliateList_') and key.endswith('_affiliateCountry'):
            if value is not None and value != 'PL':
                affiliates_foreign = 1
        if key.startswith('affiliateList_') and key.endswith('_affiliateshipPercentage'):
            if value is not None:
                affiliates_percentage.append(float(value))
            if value == '100':
                affiliateship_total = 1
        if key.startswith('affiliateList_') and key.endswith('_affiliateIsic'):
            if value is not None:
                affiliates_emis += 1
        if key.startswith('affiliateList_') and key.endswith('_affiliateshipType'):
            if value != 'Total':
                affiliateship_type = 1

    affiliates_dedup = list(set(affiliates))
    affiliates_merged = ', '.join(affiliates_dedup)

    # Add new variables to output
    result['AffiliatesMerged'] = affiliates_merged if affiliates_merged.split() else 'n/a'
    result['AffiliatesCount'] = affiliates_count
    result['AffiliatesForeign'] = affiliates_foreign
    result['AffiliatesEMIS'] = affiliates_emis
    result['AffilatteshipMin'] = min(affiliates_percentage, default='n/a')
    result['AffilatteshipMax'] = max(affiliates_percentage, default='n/a')
    if affiliates_percentage:
        result['AffilatteshipAvg'] = mean(affiliates_percentage)
    else:
        result['AffilatteshipAvg'] = 'n/a'
    result['AffilatteshipsTotal'] = affiliateship_total
    #result['AffilatteshipsType'] = affiliateship_type

    # Drop unnecessary keys
    affiliates_keys_drop = []
    for col in AFFILIATE_COLS_DROP:
        for key in result.keys():
            if key.endswith(col) or key.startswith(col):
                affiliates_keys_drop.append(key)
    for key in affiliates_keys_drop:
        result.pop(key, None)
    return result

############### PARSE EMPLOYEES ##############
def parse_employees(result: dict) -> dict:
    # Parse employees number
    if result['EmployeeNumberType'] == 'real_fixed':
        result['EmployeesNumber'] = result['EmployeeNumber']

    elif result['EmployeeNumberType'] == 'real_range': # and 'employeeNumberRange_min' in result and 'employeeNumberRange_max' in result:
        if result['employeeNumberRange_min'] is not None and result['employeeNumberRange_max'] is not None:
            result['EmployeesNumber'] = str(floor(mean([int(result['employeeNumberRange_min']), int(result['employeeNumberRange_max'])])))
        elif result['employeeNumberRange_min'] is not None and result['employeeNumberRange_max'] is None:
            result['EmployeesNumber'] = result['employeeNumberRange_min']
        elif result['employeeNumberRange_min'] is None and result['employeeNumberRange_max'] is not None:
            result['EmployeesNumber'] = result['employeeNumberRange_max']

    elif result['EmployeeNumberType'] is None:
        result['EmployeesNumber'] = 'n/a'
    else:
        result['EmployeesNumber'] = 'n/a'

    # Parse employees number date
    if result['EmployeesNumberDate'] is not None:
        result['EmployeesNumberDate3YearsAgo'] = 0 if d.datetime.strptime(result['EmployeesNumberDate'], '%Y-%m-%d') > d.datetime.now() - d.timedelta(days=3*365) else 1
    else:
        result['EmployeesNumberDate3YearsAgo'] = 'n/a'

    # Drop unnecessary keys
    for key in EMPLOYEES_COLS_DROP:
        result.pop(key, None)
    return result

############### PARSE DIVIDENDS ##############
def parse_dividends(result: dict) -> dict:
    # Parse dividend
    dividends_types = []
    dividends_currencies = []
    dividends_presence = 1
    dividends_count = 0
    dividends_sum = 0
    dividends_time_horizon = 0

    for key, value in result.items():
        if key.endswith('dividendList'):
            dividends_presence = 0
        elif key.endswith('dividendType'):
            dividends_types.append(value)
            dividends_count += 1
        elif key.endswith('dividendCurrency'):
            dividends_currencies.append(value)
        elif key.endswith('dividendValue'):
            dividends_sum += float(value)
        elif key.endswith('dividendPayDate') and d.datetime.strptime(value, '%Y-%m-%d') > d.datetime.now() - d.timedelta(days=2*365):
            dividends_time_horizon = 1

    dividends_types_dedup = list(set(dividends_types))
    dividends_types_merged = ', '.join(dividends_types_dedup)

    dividend_ccy_dedup = list(set(dividends_currencies))
    dividend_ccy_merged = ', '.join(dividend_ccy_dedup)

    result['DividendPresent'] = dividends_presence
    #result['DividendTypes'] = dividends_types_merged
    #result['DividendCurrencies'] = dividend_ccy_merged
    result['DividendCount'] = dividends_count
    result['DividendSum'] = dividends_sum
    result['DividendDate2YearsAgo'] = dividends_time_horizon

    # Drop unnecessary keys
    dividends_keys_drop = []
    for col in DIVIDENDS_COLS_DROP:
        for key in result.keys():
            if key.endswith(col):
                dividends_keys_drop.append(key)
    for key in dividends_keys_drop:
        result.pop(key, None)
    return result

################# PARSE EXECUTIVES ################
def parse_executives(result: dict) -> dict:
    # PARSE AFFILIATES
    executives_count = 0
    #executives = []
    for key, value in result.items():
        if key.endswith('_executiveNameLocal'):
            executives_count += 1
            """executive = 'Name: ' + value
            for i, j in {
                    ', Position: ' : '_executiveUserDefinedPosition',
                    ', Code: ' : '_executiveCode',
                    ', GlobalCode: ' : '_globalExecutiveCode'}.items():
                key_processed = key[:15] + j if len(key) == 34 else key[:16] + j
                info = i + result[key_processed]
                executive += info
            executives.append(executive)

    executives_dedup = list(set(executives))
    executives_merged = ', '.join(executives_dedup)"""

    result['ExecutivesCount'] = executives_count
    #result['ExecutivesMerged'] = executives_merged if executives_merged.split() else 'n/a'

    # Drop unnecessary keys
    executives_keys_drop = []
    for col in EXECUTIVES_COLS_DROP:
        for key in result.keys():
            if key.endswith(col):
                executives_keys_drop.append(key)
    for key in executives_keys_drop:
        result.pop(key, None)
    return result

################# PARSE EXTERNAL IDS ################
def parse_external_ids(result: dict) -> dict:
    external_ids = {}
    other_ids = 0
    for key in result.keys():
        if key.startswith('externalIdList_') and key.endswith('_classCode'):
            key_processed = key[:17] + 'externalId'
            if result[key] in ['PL-KRS', 'PL-REGON']:
                external_ids[result[key][3:]] = result[key_processed]
            elif result[key] == 'PL-FISCAL':
                external_ids['NIP'] = result[key_processed]
            else:
                other_ids += 1

    external_ids['ExternalIdsOthers'] = other_ids
    for key, value in external_ids.items():
        result[key] = value

    # Drop unnecessary keys
    external_ids_keys_drop = []
    for col in EXTERNAL_IDS_COLS_DROP:
        for key in result.keys():
            if key.endswith(col):
                external_ids_keys_drop.append(key)
    for key in external_ids_keys_drop:
        result.pop(key, None)
    return result

############### PARSE NAICS ##############
def parse_naics(result: dict) -> dict:
    main_naics_list = []
    main_pkd = 'n/a'
    secondary_pkd_list = []
    secondary_naics_list = []
    for key in result.keys():
        # Main activity
        if key.startswith('mainActivityList_') and key.endswith('_naics'):
            main_naics_list.append(result[key][:3])
        if key.startswith('mainActivityList_') and key.endswith('_induClass'):
            key_processed = key[:18] + '_induCode' if len(key) == 28 else key[:19] + '_induCode'
            if result[key] == 'pkd_2007':
                main_pkd = result[key_processed]
        # Secondary activity
        if key.startswith('secondaryActivityList_') and key.endswith('_naics'):
            secondary_naics_list.append(result[key][:3])
        if key.startswith('secondaryActivityList_') and key.endswith('_induClass'):
            key_processed = key[:24] + 'induCode'
            if result[key] == 'pkd_2007':
                secondary_pkd_list.append(result[key_processed])

    main_naics_list_dedup = list(set(main_naics_list))
    main_naics_merged = ', '.join(main_naics_list_dedup)
    sec_naics_list_dedup = list(set(secondary_naics_list))
    sec_naics_merged = ', '.join(sec_naics_list_dedup)
    secondary_pkd_list_dedup = list(set(secondary_pkd_list))
    sec_pkd_merged = ', '.join(secondary_pkd_list_dedup)


    result['MainPKD'] = main_pkd
    result['MainNAICSCount'] = str(len(main_naics_list_dedup))
    result['MainNAICSCodes'] = main_naics_merged if main_naics_merged.strip() else 'n/a'
    result['SecondaryPKD'] = sec_pkd_merged
    result['SecondaryPKDCount'] = str(len(secondary_pkd_list_dedup))
    result['SecondaryNAICSCodes'] = sec_naics_merged if sec_naics_merged.strip() else 'n/a'

    # Drop unnecessary keys
    naics_ids_keys_drop = []
    for col in NAICS_COLS_DROP:
        for key in result.keys():
            if key.startswith('mainActivityList_') or key.startswith('secondaryActivityList_') and key.endswith(col):
                naics_ids_keys_drop.append(key)
    for key in naics_ids_keys_drop:
        result.pop(key, None)
    return result

############### PARSE OUTSTANDING SHARELIST ##############
def parse_outstanting_shares(result: dict) -> dict:
    shares_value = 0
    shares_dates = []
    for key in result.keys():
        if key.startswith('outstandingSharesList_') and key.endswith('_outstandingShareValue'):
            shares_value += float(result[key])
        if key.startswith('outstandingSharesList_') and key.endswith('_outstandingShareDate'):
            shares_dates.append(d.datetime.strptime(result[key], '%Y-%m-%d'))

    result['OutstandingSharesSum'] = shares_value
    if shares_dates:
        latest_date = max(shares_dates)
        result['OutstandingSharesDate'] = latest_date
        result['OutstandingSharesDateLessThan2YearsAgo'] = 1 if latest_date > d.datetime.now() - d.timedelta(days=2*365) else 0
    else:
        result['OutstandingSharesDate'] = 'n/a'
        result['OutstandingSharesDateLessThan2YearsAgo'] = 0

    # Drop unnecessary keys
    shares_keys_drop = []
    for col in OUTSTANDING_SHARES_COLS_DROP:
        for key in result.keys():
            if key.startswith('outstandingSharesList') and key.endswith(col):
                shares_keys_drop.append(key)
    for key in shares_keys_drop:
        result.pop(key, None)
    return result

############### PARSE OWNERS ##############
def parse_owners(result: dict) -> dict:
    owners_count = 0
    owners_isics = 0
    owners_foreign = 0

    for key, value in result.items():
        if key.startswith('ownerList_') and key.endswith('_ownerIsic'):
            owners_count += 1
            if value is not None:
                owners_isics += 1
        elif key.startswith('ownerList_') and key.endswith('_ownerCountry') and value is not None:
            if value is not None and value != 'PL':
                owners_foreign = 1

    result['OwnersCount'] = owners_count
    result['OwnersInEMIS'] = owners_isics
    #result['OwnersIfForeign'] = owners_foreign

    # Drop unnecessary keys
    owners_keys_drop = []
    for col in OWNERS_COLS_DROP:
        for key in result.keys():
            if key.startswith('ownerList_') and key.endswith(col):
                owners_keys_drop.append(key)
    for key in owners_keys_drop:
        result.pop(key, None)
    return result

############### PARSE PREVIOUS NAMES ##############
def parse_previous_names(result: dict) -> dict:
    prev_names_count = 0
    prev_names_changes_dates = []
    for key, value in result.items():
        if key.startswith('previousNameList_') and key.endswith('_previousNameChangeYear'):
            prev_names_count += 1
            if value is not None:
                prev_names_changes_dates.append(d.datetime.now().year - int(value))

    result['PreviousNamesCount'] = prev_names_count
    result['PreviousNameChangeYearsAgo'] = min(prev_names_changes_dates) if prev_names_changes_dates else 'n/a'

    # Drop unnecessary keys
    previous_names_keys_drop = []
    for col in PREVIOUS_NAMES_COLS_DROP:
        for key in result.keys():
            if key.startswith('previousNameList') and key.endswith(col):
                previous_names_keys_drop.append(key)
    for key in previous_names_keys_drop:
        result.pop(key, None)
    return result

############### PARSE SEGMENT ##############
def parse_segment(result: dict) -> dict:
    segment_presence = 0
    segment_names = []
    segment_stock_exchange_ids = []
    segment_stock_names = []
    for key, value in result.items():
        if key.startswith('segmentList_') and key.endswith('_segmentName'):
            segment_presence = 1
            segment_names.append(value)
        elif key.startswith('segmentList_') and key.endswith('_segmentStockExchangeId'):
            segment_stock_exchange_ids.append(value)
        elif key.startswith('segmentList_') and key.endswith('_segmentStockName'):
            segment_stock_names.append(value)

    segment_names_dedup = list(set(segment_names))
    segment_names_merged = ', '.join(segment_names_dedup)

    segment_stock_exchange_ids_dedup = list(set(segment_stock_exchange_ids))
    segment_stock_exchange_ids_merged = ', '.join(segment_stock_exchange_ids_dedup)

    segment_stock_names_dedup = list(set(segment_stock_names))
    segment_stock_names_merged = ', '.join(segment_stock_names_dedup)

    result['SegmentPresence'] = segment_presence
    result['SegmentName'] = segment_names_merged if segment_names_merged.strip() else 'n/a'
    result['SegmentStockExchangeId'] = segment_stock_exchange_ids_merged if segment_stock_exchange_ids_merged.strip() else 'n/a'
    result['SegmentStockName'] = segment_stock_names_merged if segment_stock_names_merged.strip() else 'n/a'

    # Drop unnecessary keys
    segment_keys_drop = []
    for col in SEGMENT_COLS_DROP:
        for key in result.keys():
            if key.startswith('segmentList') and key.endswith(col):
                segment_keys_drop.append(key)
    for key in segment_keys_drop:
        result.pop(key, None)
    return result

################ INITIAL KEYS TO DROP ################
COLS_DROP = [
    '_type', 'companyName', 'companySizeType',
    'displayName', 'displayNameLocal', 'latestMarketCapitalizationCurrency',
    'registeredCapitalCurrency', 'ratingList']

FLATTEN_COLS_DROP = [
    '__type', 'address_address', 'address_city', 'address_region',
    'affiliateName', 'descriptionLocal', 'executiveName',
    'executiveUserDefinedPositionLocal', 'mainProductsLocal',
    'ownerName', 'previousNameName']

################ PARSED NESTED KEYS TO DROP ################
AFFILIATE_COLS_DROP = [
    'affiliateCountry', 'AffiliateCountry', 'affiliateExternalId', 'AffiliateExternalId',
    'affiliateExternalIdClass', 'AffiliateExternalIdClass',
    'affiliateIsic', 'AffiliateIsic', 'affiliateNameLocal', 'AffiliateNameLocal',
    'affiliateshipPercentage', 'AffiliateshipPercentage',
    'affiliateshipType', 'AffiliateshipType']

EMPLOYEES_COLS_DROP = [
    'EmployeeNumber', 'employeeNumberRange',
    'employeeNumberRange_min', 'employeeNumberRange_max', ]

DIVIDENDS_COLS_DROP = [
    '_dividendCurrency', '_dividendPayDate',
    '_dividendType', '_dividendValue', 'dividendList']

EXECUTIVES_COLS_DROP = [
    '_executiveCode', '_executiveNameLocal',
    '_executiveUserDefinedPosition', '_globalExecutiveCode']

EXTERNAL_IDS_COLS_DROP = ['_classCode', '_externalId']

NAICS_COLS_DROP = ['_naics', '_induClass', '_induCode']

OUTSTANDING_SHARES_COLS_DROP = [
    '_outstandingShareDate', '_outstandingShareSeriesName',
    '_outstandingShareValue', 'outstandingSharesList']

OWNERS_COLS_DROP = [
    '_ownerCountry', '_ownerExternalId', '_ownerExternalIdClass', '_ownerIsic',
    '_ownerNameLocal', '_ownerType', '_ownershipPercentage', '_ownershipType']

PREVIOUS_NAMES_COLS_DROP = [
    '_previousNameChangeYear', '_previousNameLocalName', 'previousNameList']

SEGMENT_COLS_DROP = [
    '_segmentName', '_segmentStockExchangeId', '_segmentStockName', 'segmentList']

OUTPUT_RENAME = {
    'address_addressLocal' : 'Address',
    'address_cityLocal' : 'City',
    'address_email' : 'EmailAddress',
    'address_fax' : 'Fax',
    'address_phone' : 'Phone',
    'address_postalCode' : 'PostalCode',
    'address_regionLocal' : 'Region',
    'address_url' : 'Website',
    'auditorDate' : 'AuditDate',
    'auditorName' : 'AuditorName',
    'companyLocalName' : 'CompanyName',
    'companySizeRevenue' : 'CompanyRevenue',
    'companySizeYear' : 'CompanyRevenueYear',
    'companyType' : 'CompanyType',
    'countryCode' : 'Country',
    'description' : 'Description',
    'employeeNumber' : 'EmployeeNumber',
    'employeeNumberDate' : 'EmployeesNumberDate',
    'employeeNumberType' : 'EmployeeNumberType',
    'globalLegalForm' : 'GlobalLegalForm',
    'incorporationYear' : 'IncorporationYear',
    'isic' : 'EMISID',
    'latestMarketCapitalization' : 'LatestMarketCapitalization',
    'legalForm' : 'LegalForm',
    'mainProducts' : 'MainProducts',
    'profileUpdateDate' : 'ProfileUpdateDate',
    'registeredCapitalDate' : 'RegisteredCapitalDate',
    'registeredCapitalValue' : 'RegisteredCapitalValue',
    'status' : 'Status'}

AFFILIATE_COLS = [
    '._affiliateCountry', '._affiliateExternalId', '._affiliateExternalIdClass',
    '._affiliateIsic', '._affiliateNameLocal', '._affiliateshipPercentage',
    '._affiliateshipType']

PUBLIC_DOMAINS = [
    '@gmail', '@wp', '@poczta.onet', '@onet.', '@op.pl', '@gazeta.pl', '@go2',
    '@yahoo', '@o2', '@autograf.pl', '@buziaczek.pl', '@tlen.', '@hotmail',
    '@interia.', '@vp', '@gery.pl', '@akcja.pl', '@czateria.pl', '@1gb.pl', '@2gb.pl',
    '@os.pl', '@skejt.pl', '@fuks.pl', '@ziomek.pl', '@oferujemy.info', '@twoj.info',
    '@twoja.info', '@boy.pl', '@najx.com', '@adresik.com', '@e-mail.net.pl', '@iv.pl',
    '@bajery.pl', '@gog.pl', '@os.pl', '@serwus.pl', '@aol.pl', '@poczta.fm',
    '@lycos.co%', '@windowslive.com']

######### OUTPUT COLUMNS ###########
OUTPUT_REGISTER_COLS = [
    'NIP', 'CompanyName', 'Status', 'KRS', 'REGON', 'EMISID', 'ExternalIdsOthers',
    'Country', 'Region', 'City', 'Address', 'PostalCode', 'AddresFlat',
    'EmailAddress', 'EmailAdressNotPresent', 'EmailAdressPublic',
    'Website', 'WebsiteNotPresent',
    'Phone','PhoneNotPresent', 'Fax', 'FaxNotPresent',
    'IncorporationYear', 'IncYearsAgo', 'IncLessThan1YearsAgo', 'IncLessThan3YearsAgo',
    'IncLessThan5YearsAgo', 'IncLessThan10YearsAgo',
    'PreviousNameChangeYearsAgo', 'PreviousNamesCount',
    'CompanyType', 'GlobalLegalForm', 'LegalForm',
    'RegisteredCapitalDate', 'RegisteredCapitalValue',
    'CompanyRevenue', 'CompanyRevenueYear', 'CompanyRevenue2YearsAgo',
    'AffiliatesCount', 'AffiliatesEMIS', 'AffiliatesForeign',
    'AffilatteshipAvg', 'AffilatteshipMax', 'AffilatteshipMin',	'AffilatteshipsTotal',
    'AuditDate', 'AuditDateNull', 'AuditDateYearsAgo', 'AuditorName',
    'EmployeeNumberType', 'EmployeesNumber', 'EmployeesNumberDate', 'EmployeesNumberDate3YearsAgo',
    'Description', 'DescriptionNull', 'MainProducts', 'MainProductsNull',
    'DividendPresent', 'DividendCount', 'DividendDate2YearsAgo', 'DividendSum',
    'ExecutivesCount', 'OwnersCount',	'OwnersInEMIS',
    'MainPKD', 'SecondaryPKD',
    'MainNAICSCodes', 'MainNAICSCount', 'SecondaryNAICSCodes',  'SecondaryPKDCount',
    'LatestMarketCapitalization', 'MarketCapNull',
    'OutstandingSharesSum', 'OutstandingSharesDate', 'OutstandingSharesDateLessThan2YearsAgo', 
    'SegmentName', 'SegmentPresence', 'SegmentStockName']

######### GET NIP NAME LIST  ###########
def get_nip_name(input_file):
    valid_nips_list = []
    invalid_nips_list = []
    nip_name_valid = []
    nip_name_invalid = []
    try:
        data = pd.read_excel(input_file, dtype=str, header=None, names=['NIP', 'NazwaPodmiotu'])
        data_dedup = data.drop_duplicates(subset='NIP')
        duplicates = list(set([i for i in data['NIP'].tolist() if
                               data['NIP'].tolist().count(i) > 1]))
        nip_list = data_dedup['NIP'].tolist()
        name_list = data_dedup['NazwaPodmiotu'].tolist()
        for nip, company_name in zip(nip_list, name_list):
            nip_valid_dic, nip_invalid_dic = clean_nip_name(nip, company_name)
            if nip_valid_dic:
                nip_name_valid.append(nip_valid_dic)
                valid_nips_list.append(nip)
            else:
                nip_name_invalid.append(nip_invalid_dic)
                invalid_nips_list.append(nip)
    except ValueError:
        print("Names not found")
        name_list = []
        data = pd.read_excel(input_file, dtype=str, header=None, names=['NIP'])
        data_dedup = data.drop_duplicates(subset='NIP')
        duplicates = list(set([i for i in data['NIP'].tolist() if
                               data['NIP'].tolist().count(i) > 1]))
        nip_list = data_dedup['NIP'].tolist()
        for i in nip_list:
            name_list.append(None)

        for nip, company_name in zip(nip_list, name_list):
            nip_valid_dic, nip_invalid_dic = clean_nip_name(nip, company_name)
            if nip_valid_dic:
                nip_name_valid.append(nip_valid_dic)
                valid_nips_list.append(nip)
            else:
                nip_name_invalid.append(nip_invalid_dic)
                invalid_nips_list.append(nip)

    log_df = pd.DataFrame({"ValidNIP" : pd.Series(valid_nips_list),
                           "InvalidNIP" : pd.Series(invalid_nips_list),
                           "DuplicatedNIP" : pd.Series(duplicates)})
    return nip_name_valid, nip_name_invalid, log_df

############ CLEAN_NAME_NIP ###################
def clean_nip_name(nip, name):
    nip_invalid_dic = {}
    nip_valid_dic = {}
    total = 0
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]

    clean_nip = re.sub(r'[A-Z]', "", nip)
    nip_factorized = list(clean_nip)
    for i, j in zip(nip_factorized, weights):
        total += int(i)*j
    if re.search(r"[A-Z]", nip, re.IGNORECASE) is not None and re.search("PL", nip, re.IGNORECASE) is None:
        nip_invalid_dic[nip] = name
    elif int(nip_factorized[-1]) == total % 11 and len(clean_nip) == 10:
        if name is not None:
            trans = name.maketrans("-;", "  ", "'\"")
            name = name.translate(trans).strip()
            name = re.sub(r' +', " ", name)
            for form in legal_forms:
                m = re.search(unidecode(form), unidecode(name), re.IGNORECASE)
                if m:
                    name = name[:m.start()] + name[m.end():]
            name = re.sub(r' +', " ", name).strip()
        nip_valid_dic[clean_nip] = '"' + name.upper() + '"' if name is not None else None
    else:
        nip_invalid_dic[nip] = 'n/a' if name == 'nan' else name
    return nip_valid_dic, nip_invalid_dic

legal_forms = [
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ", "SPÓŁKA KOMANDYTOWA", "Sp\.z o\.o\.",
    "P\.P\.U\.H.", "PPUH", "PRZEDSIĘBIORSTWO HANDLOWO PRODUKCYJNE", "PHU", "P\.H\.U.",
    "SPÓŁKA CYWILNA", "SPÓŁKA JAWNA", "SPÓŁKA KOMANDYTOWA", "SPÓŁKA AKCYJNA",
    "PRZEDSIĘBIORSTWO HANDLOWO USŁUGOWE", "SPÓŁKA KOMANDYTOWO AKCYJNA",
    "Przedsiębiorstwo wielobranżowe", "SPÓŁKA KOMANDYTOWO AKCYJNA",
    "SPÓŁKA PARTNERSKA", "FIRMA TRANSPORTOWO HANDLOWA", "SPÓŁKA KOMANDYTOWO   AKCYJNA",
    "ZAKŁAD PRODUKCYJNO USŁUGOWY", "PRZEDSIĘBIORSTWO WIELOBRANŻOWE", "Sp\. z o\.o\.",
    "FIRMA HANDLOWO USŁUGOWA", "PRZEDSIEBIORSTWO PRODUKCYJNO USLUGOWO HANDLOWE",
    "PRZEDSIEBIORSTWO WIELOBRANZOWE", "SPOLKA KOMANDYTOWO AKCYJNA", " S\.C\.",
    "SP\. Z O\.O\.", "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZILNOŚCIĄ", " S\.A\.",
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOIŚCIĄ", "PPHU", "P\.P\.P\.U\.",
    "PRZEDSIĘBIORSTWO PRODUKCYJNO HANDLOWO USŁUGOWE", " S\.K\.",
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNO0ŚCIĄ", "SPOLKA Z O\.O\.", " SP\.J\.",
    "SPÓŁKA Z OGRANICZONĄ OSPOWIEDZIALNOŚCIĄ", "FIRMA HANDLOWO USŁUGOWA",
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIELNOŚCIĄ", "SPÓŁKI JAWNEJ", "SPÓŁKA Z O.O.",
    "SPÓŁKA KOMANDYTWO AKCYJNA", "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALANOŚCIĄ",
    "SPÓŁKA OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ", "SPÓŁKA ZOGRANICZONĄ ODPOWIEDZIALNOŚCIĄ",
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZILANOŚCIĄ", "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNŚCIĄ",
    "SPÓŁKA Z OGRANICZONĄ ODOWIEDZIALNOŚCIĄ", "SPÓŁKA Z OGRANICZONĄ 0ODPOWIEDZIALNOŚCIĄ",
    "SPÓŁKA HANDLOWO USŁUGOWA", "SPÓŁKA Z ODPOWEDZIALNOŚCIĄ", "W LIKWIDACJI",
    "SPÓŁKA Z OGRANICZONĄ OODPOWIEDZIALNOŚCIĄ", "W UPADŁOŚCI LIKWIDACYJNEJ",
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZALNOŚCIĄ", "Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ"]

"""
fin_cols_rename = {'TS': 'Assets', 'FA': 'Non-current assets ', 'TANG': 'Property, plant and equipment', 'TANGLAND': 'Land and buildings', 'TANGVECH': 'Vehicles and machinery', 'TANGFIXT': 'Fixtures and fittings', 'TANGOTHER': 'Other property, plant and equipment', 'INPROGR': 'Construction in progress', 'INT': 'Intangible assets anCOINVEQd goodwill', 'INTGOODW': 'Goodwill', 'INTTRADM': 'Trademarks and licenses', 'INTDEVCOST': 'Development costs', 'INTOWNSOFT': 'Own developed computer software', 'INTOTH': 'Other intangible assets', 'NCBIO': 'Non-current biological assets', 'NCREC': 'Non-current Trade and other receivables', 'NCRECTRADE': 'Non-current trade receivables', 'NCRECRELAT': 'Receivables from related parties', 'NCRECOTHER': 'Other non-current receivables', 'NCRECDOUBT': 'Doubtful receivables', 'FINVEST': 'Long-term financial assets', 'FINVESTPROP': 'Investment properties', 'FINVESTSUBS': 'Investments in subsidiaries', 'FINVESTASSOC': 'Investments in associates', 'FINVESTFORSALE': 'Available-for-sale financial assets (LT)', 'FINVESTDERIV': 'Derivative financial instruments', 'FINVESTFAIRVALUE': 'Financial assets at fair value through profit or loss', 'FINVESTHELDMAT': 'Financial assets held-to-maturity', 'FINVESTOTH': 'Other non-current financial assets', 'NCDEFFERED': 'Deferred assets', 'NCDEFFEREDTAX': 'Non-current deferred tax assets', 'NCDEFFEREDOTHER': 'Other non-current deferred assets', 'OTHFIX': 'Other non-current assets', 'CA': 'Current Assets', 'INV': 'Inventories', 'INVRAW': 'Raw materials', 'INVWIP': 'Work in progress', 'INVFINISHED': 'Finished goods', 'INVOTH': 'Other inventories', 'CBIO': 'Current biological assets', 'REC': 'Trade and other receivables', 'RECTRADE': 'Current trade receivables', 'RECRELATED': 'Receivables from related parties', 'RECOTHER': 'Other current receivables', 'RECDOUBT': 'Doubtful receivables', 'RECTAX': 'Tax receivables', 'ACCRUE': 'Prepayments, accrued income and other deferred current assets', 'SEC': 'Short term Financial assets', 'SECFORSALE': 'Available-for-sale financial assets (ST)', 'SECDERIVAT': 'Derivative financial instruments', 'SECFAIRVALUE': 'Financial assets at fair value through profit or loss', 'SECHELDMAT': 'Financial assets held-to-maturity', 'SECOTH': 'Other current financial assets', 'CE': 'Cash and cash equivalents', 'CECASH': 'Cash at banks and on hand', 'CEDEPOSIT': 'Short-term deposits', 'OTHCURR': 'Other current assets', 'ASSETFORSALE': 'Assets of disposal group classified as held for sale', 'NA': 'Net current assets', 'TLE': 'Total Equity and liabilities', 'SE': 'Total equity', 'SEOWN': 'Equity attributable to owners of the parent', 'ISSUED': 'Issued capital', 'ISSUEDORD': 'Ordinary shares', 'ISSUEDPREF': 'Preferred shares', 'SEOWNPREMIUM': 'Share premium', 'SEOWNTREASURY': 'Treasury shares', 'SEOWNREVALUATION': 'Revaluation reserve', 'SEOWNFOREIGNCURR': 'Foreign currency translation reserve', 'SEOWNCFHEDGE': 'Cashflow hedge reserve', 'SEOWNHELDFORSALE': 'Reserves of a disposal group classified as held for sale', 'SEOWNOTH': 'Other reserves', 'PROFITRESERV': 'Retained earnings', 'BSPROFIT': 'Profit or loss for the period', 'SEOWNDUETOCONS': 'Changes due to consolidation', 'OTHEQ': 'Other components of equity', 'SEMIN': 'Minority interest', 'TL': 'Total Liabilities', 'LTL': 'Non-current liabilities', 'INVDEV': 'Non-current loans and borrowings', 'LTLDERIVA': 'Non-current derivative financial instruments', 'LTLOTH': 'Other non-current financial liabilities', 'BONDDEBT': 'Debts on issue of bonds', 'LTTRADPAY': 'Non-current trade payables', 'LTLPAYABLE': 'Other non-current payables', 'LTLDEFERRED': 'Deferred revenue, accrued expenses and other deferred non-current liabilities ', 'LTLPROVISION': 'Provisions for other liabilities and charges', 'OTLONGLIA': 'Other non-current liabilities', 'CL': 'Current Liabilities', 'CLDEFERRTAX': 'Deferred income tax liabilities', 'SLOAN': 'Current loans and borrowings', 'CLDERIVA': 'Current derivative financial instruments', 'CLOTH': 'Other current financial liabilities', 'TRCREDIT': 'Trade and other payables', 'TRCREDITTRADE': 'Current trade payables', 'TRCREDITRELATED': 'Payables due to related parties', 'TRCREDITOTH': 'Other current payables', 'ACCRUL': 'Deferred revenue, accrued expenses and other deferred current liabilities ', 'PROVIS': 'Provisions for other liabilities and charges', 'OTHLIAB': 'Other current liabilities', 'CLTAX': 'Current income tax liabilities', 'CLHELDFORSALE': 'Liabilities of disposal group classified as held for sale', 'TR': 'Total operating revenue', 'NS': 'Net sales revenue', 'EXPORT': 'Net Export Sales Revenue', 'DOMESTIC': 'Net Domestic Sales Revenue', 'COGS': 'Cost of Goods Sold', 'GROSSPROF': 'Gross profit', 'EXPSELLING': 'Selling and distribution expenses', 'EXPADMIN': 'Administrative expenses', 'EXPCHNGINVENT': 'Changes in inventories of finished goods and work in progress', 'EXPWORKCAPITALIZED': 'Work performed and capitalized', 'MATERIAL': 'Raw materials and consumables used', 'PERSON': 'Employee benefit expense', 'PERSONWAGE': 'Wages and salaries', 'PERSONSOCIAL': 'Social security costs', 'PERSONOTH': 'Other employee benefit expense', 'EXPTRANSP': 'Transportation costs', 'EXPITEXP': 'IT expenses', 'EXPADVERT': 'Advertising costs', 'EXPTAXCONTR': 'Tax and contributions', 'EXPRDCOST': 'R&D costs', 'EXPOTHBYNAT': 'Other costs by nature', 'DEPRIC': 'Depreciation, amortization and impairment charges', 'OTHEOPNET': 'Net - Other operating result', 'OREV': 'Other operating income', 'OTHCOST': 'Other operating expenses', 'OTHNET': 'Other Net Operating Results', 'OP': 'Operating profit/loss (EBIT)', 'EBITDAGLOB': 'EBITDA', 'FINRESULT': 'Financial result', 'FINRESULTIN': 'Finance income', 'FINRESULTININTEREST': 'Interest income', 'FINRESULTINDIV': 'Dividend income', 'FINRESULTINFOREX': 'Foreign exchange gain', 'FINRESULTINOTH': 'Other financial income', 'FINRESULTCOST': 'Finance expenses', 'FINRESULTCOSTINT': 'Interest expense', 'FINRESULTCOSTFOREX': 'Foreign exchange loss', 'FINRESULTCOSTOTH': 'Other financial expenses', 'FINRESULTSHARE': 'Share of profit (loss) of associates', 'OTHNETRE': 'Net - other non-operating result', 'OTHINCOME': 'Other income', 'OTHCOSTS': 'Other expenses', 'EXTRESULT': 'Extraordinary Non-Operating Items', 'PRETAX': 'Profit before income tax', 'TAX': 'Income tax', 'TAXDUE': 'Tax difference due to consolidation', 'AFTERTAX': 'Profit (Loss) from continuing operations', 'AFTERTAXDISC': 'Profit (Loss) from discontinued operations', 'OEXTI': 'Other Extraordinary Items', 'NP': 'NET PROFIT/LOSS FOR THE PERIOD', 'NPTOOWN': '-  Profit (loss) attributable to Owners ', 'NPMINT': '   -  Profit (loss) attributable to Minority Interests', 'COMPREHENSOTH': 'Other comprehensive result for the period, net of tax', 'COEXCDIF': 'Results from exchange differences on translation', 'COINVEQ': 'Results from investments in equity', 'COMSAFI': 'Results from available-for-sale financial assets', 'COMHED': 'Results from cash flow hedges', 'COMBEN': 'Remeasurements of defined benefit plans', 'COMREVF': 'Results from Revaluation of fixed assets', 'COMFINA': 'Revaluation of financial instruments', 'COMJOIN': 'Share of other results from associates and joint ventures', 'COMOTH': 'Other comprehensive Results ', 'COMINTAX': 'Income tax relating to components comprehensive results', 'AFTERTAXTOTAL': 'Comprehensive Income', 'COMTOOWN': '- Comprehensive Income attributable to Owers', 'OUTSIDE': '-  Comprehensive Income attributable to Minority Interests', 'CFNCFOPERATING': 'Net cash flow from (used in) operating activities', 'CFPROFITOFYEAR': 'Net Profit', 'CFCASH': 'Cash generated from operations', 'CFADJTANG': 'Depreciation and impairment of property, plant and equipment', 'CFADJINTAN': 'Adjustments for: Amortization of intangible assets', 'CFADJIMPTANK': 'Adjustments for: Impairment losses on property, plant and equipment', 'CFADJIMPINTAN': 'Adjustments for: Impairment loss on intangible assets', 'CFADJIMPREC': 'Adjustments for: Impairment loss on trade receivables', 'CFADJFINRESULTIN': 'Adjustments for: Finance income', 'CFADJFINRESULTCOST': 'Adjustments for: Finance expenses', 'CFADJGAINPROP': 'Adjustments for: Gain on sale of property, plant and equipment', 'CFADJDISCONTOP': 'Adjustments for: Gain on sale of discontinued operations', 'CFADJOTHADJ': 'Adjustments for: Other adjustments', 'CFCHNGINV': 'Changes in: Inventories', 'CFCHNGBIOLOG': 'Changes in: Current biological assets due to sales', 'CFCHNGTRADE': 'Changes in: Trade and other receivables', 'CFCHNGPREP': 'Changes in: Prepayments', 'CFCHNGREC': 'Changes in: Trade and other payables', 'CFCHNGPROV': 'Changes in: Provisions and employee benefits', 'CFCHNGDEFERRED': 'Changes in: Deferred income', 'CFCHNGOTH': 'Changes in: Other changes', 'CFINCOMETAX': 'Income tax paid', 'CFOTHOPCF': 'Other operating activity cash flows', 'CFNCFINVEST': 'Net cash flow from (used in) investing activities', 'CFINVESTSALEPROP': 'Proceeds from sale of property, plant and equipment', 'CFINVESTPROP': 'Purchase of property, plant and equipment', 'CFINVESTNTANG': 'Purchase of intangible assets', 'CFINVESTINVPROP': 'Purchase of investment properties', 'CFINVESTFININST': 'Purchase of financial instruments', 'CFINVESTSALEFININST': 'Proceeds from sale of financial instruments', 'CFINVESTDEVEXP': 'Development expenditures', 'CFINVESTACQUIRE': 'Acquisition of subsidiary', 'CFINVESTINTREC': 'Interest received', 'CFINVESTDIVIDREC': 'Dividends received', 'CFINVESTOTHINVEST': 'Other investing activity cash flows', 'CFNCFFINANCE': 'Net cash flow from (used in) financing activities', 'CFFINORDINAR': 'Proceeds from issuance of ordinary shares', 'CFFINOTHEQUITY': 'Proceeds from issuance of other equity instruments', 'CFFINTREASURY': 'Purchase of treasury shares', 'CFFINSALEOWN': 'Proceeds from sale of own shares', 'CFFINBOR': 'Proceeds from borrowings', 'CFFINREPAYBOR': 'Repayment of borrowings', 'CFFINCOSTLOAN': 'Payments of transaction costs related to loans and borrowings', 'CFFINPAYLEASE': 'Payments of finance lease liabilities', 'CFFINPAIDINT': 'Interest paid', 'CFFINPAIDDIV': 'Dividends paid', 'CFFINOTHFINACT': 'Other financing activity cash flow', 'CFNETINCREASECASH': 'Net increase (decrease) in cash and cash equivalents', 'CFCASHBEGIN': 'Cash at the beginning of the period', 'CFCASHFOREX': 'Exchange gains (losses) on cash and cash equivalents', 'CFCASHEND': 'Cash at the end of the period', 'CFFCF': 'Free cash flow', 'CFCAPEX': 'CAPEX', 'MIN': 'Lower Limit of Revenue Range', 'MAX': 'Upper Limit of Revenue Range'}
fin_cols_rename1 = {'A, Fixed Assets': 'A, Aktywa trwałe', 'I, Intangible assets': 'I, Wartości niematerialne i prawne', '1, R&D expenses': '1, Koszty zakończonych prac rozwojowych ', '2, Goodwill': '2, Wartość firmy ', '3, Other intangible assets': '3, Inne wartości niematerialne i prawne ', '4, Advances for intangible assets': '4, Zaliczki na wartości niematerialne i prawne ', 'II, Goodwill of associated entities': 'II, Wartość firmy jednostek podporządkowanych', '1, Subsidiaries': '1, Zależnych', '2, Associated entities': '2, Współzależnych', '3, Affiliates': '3, Stowarzyszonych', 'III, Tangible fixed assets': 'III, Rzeczowe aktywa trwałe ', '1, Tangible fixed assets in use': '1, Środki trwałe ', 'a, land (including right to perpetual usufruct)': 'a, grunty (w tym prawo użytkowania wieczystego gruntu) ', 'b, buildings, premises, civil and water engineering structures': 'b, budynki, lokale i obiekty inżynierii lądowej i wodnej', 'c, technical equipment and machines': 'c, urządzenia techniczne i maszyny', 'd, vehicles': 'd, środki transportu ', 'e, other tangible fixed assets': 'e, inne środki trwałe ', '2, Tangible fixed assets under construction': '2, Środki trwałe w budowie ', '3, Advances for tangible fixed assets under construction': '3, Zaliczki na środki trwałe w budowie ', 'IV, Long-term receivables': 'IV, Należności długoterminowe ', '1, From related parties': '1, Od jednostek powiązanych ', '2, From other entities': '2, Od jednostek pozostałych ', 'V, Long-term investments': 'V, Inwestycje długoterminowe ', '1, Real property': '1, Nieruchomości ', '2, Intangible assets': '2, Wartości niematerialne i prawne ', '3, Long-term financial assets': '3, Długoterminowe aktywa finansowe', 'a, in related parties': 'a, w jednostkach powiązanych ', '- shares': '- udziały lub akcje', '- other securities': '- inne papiery wartościowe', '- loans granted': '- udzielone pożyczki', '- other long-term financial assets': '- inne długoterminowe aktywa finansowe', 'b, In subsidiaries, associated entities and affiliates valuated by means of equity method': 'b, W jednostkach zależnych, współzależnych i stowarzyszonych wycenionych metodą praw własności', '- Shares': '- udziały lub akcje', '- Other securities': '- inne papiery wartościowe', '- Loans granted': '- udzielone pożyczki', '- Other long-term financial assets': '- inne długoterminowe aktywa finansowe', 'c, in other entities': 'c, w pozostałych jednostkach ', '4, Other long-term investments': '4, Inne inwestycje długoterminowe ', 'VI, Long-term prepayments': 'VI, Długoterminowe rozliczenia międzyokresowe ', '1, Deferred tax assets': '1, Aktywa z tytułu odroczonego podatku dochodowego ', '2, Other prepayments': '2, Inne rozliczenia międzyokresowe ', 'B, Current Assets': 'B, Aktywa obrotowe', 'I, Inventory': 'I, Zapasy ', '1, Materials': '1, Materiały ', '2, Semi-finished products and work in progress': '2, Półprodukty i produkty w toku ', '3, Finished products': '3, Produkty gotowe ', '4, Goods': '4, Towary ', '5, Advances for deliveries': '5, Zaliczki na dostawy ', 'II, Short-term receivables': 'II, Należności krótkoterminowe ', '1, Receivables from related parties': '1, Należności od jednostek powiązanych ', 'a, trade receivables, maturing:': 'a, z tytułu dostaw i usług, o okresie spłaty: ', '- up to 12 months': '- do 12 miesięcy ', '- above 12 months': '- powyżej 12 miesięcy ', 'b, other': 'b, inne ', '2, Receivables from other entities': '2, Należności od pozostałych jednostek ', 'b, receivables from tax, subsidy, customs, social security and other benefits': 'b, z tytułu podatków, dotacji, ceł, ubezpieczeń społecznych i zdrowotnych oraz innych świadczeń ', 'c, other': 'c, inne ', 'd, claimed at court': 'd, dochodzone na drodze sądowej ', 'III, Short-term investments': 'III, Inwestycje krótkoterminowe ', '1, Short-term financial assets': '1, Krótkoterminowe aktywa finansowe ', '- other short-term financial assets': '- inne krótkoterminowe aktywa finansowe', '- Other short-term financial assets': '- inne krótkoterminowe aktywa finansowe', 'd, cash and other pecuniary assets': 'd, środki pieniężne i inne aktywa pieniężne ', '- cash in hand and at bank': '- środki pieniężne W kasie i na rachunkach', '- other cash': '- inne środki pieniężne', '- other pecuniary assets': '- inne aktywa pieniężne', '2, Other short-term investments': '2, Inne inwestycje krótkoterminowe ', 'IV, Short-term prepayments': 'IV, Krótkoterminowe rozliczenia międzyokresowe ', 'Total Assets': 'Aktywa Razem', 'A, Equity': 'A, Kapitał (fundusz) własny', 'I, Share capital': 'I, Kapitał (fundusz) podstawowy ', 'II, Called up share capital (negative value)': 'II, Należne wpłaty na kapitał podstawowy (wielkość ujemna) ', 'III, Own shares (negative value)': 'III, Udziały (akcje) własne (wielkość ujemna) ', 'IV, Supplementary capital': 'IV, Kapitał (fundusz) zapasowy ', 'V, Revaluation reserve': 'V, Kapitał (fundusz) z aktualizacji wyceny ', 'VI, Other reserve capitals': 'VI, Pozostałe kapitały (fundusze) rezerwowe ', 'VII, Currency conversion differences': 'VII, Różnice kursowe z przeliczenia', 'VIII, Previous years profit (loss)': 'VIII, Zysk (strata) z lat ubiegłych ', 'IX, Net profit (loss)': 'IX, Zysk (strata) netto ', 'X, Write-off on net profit during the financial year (negative value)': 'X, Odpisy z zysku netto w ciągu roku obrotowego (wielkość ujemna) ', 'B, Minority capital': 'B, Kapitał mniejszościowy', 'C, Unified goodwill of subsidiaries': 'C, Ujednolicona wartość firmy jednostek podporządkowanych', 'I, Unified goodwill - subsidiaries': 'I, Ujednolicona wartość firmy - jednostki zależne', 'II, Unified goodwill - partner entities': 'II, Ujednolicona wartość firmy - jednostki współzależne', 'III, Unified goodwill - affiliates': 'III, Ujednolicona wartość firmy - jednostki stowarzyszone', 'D, Liabilities and Provisions Liabilities': 'D, Zobowiązania i rezerwy na zobowiązania', 'I, Provisions for liabilities': 'I, Rezerwy na zobowiązania ', '1, Provision for deferred income tax': '1, Rezerwa z tytułu odroczonego podatku dochodowego ', '2, Provision for retirement and similar benefits': '2, Rezerwa na świadczenia emerytalne i podobne ', '-long-term': '-długoterminowe', '-short-term': '-krótkoterminowe', '3, Other provisions': '3, Pozostałe rezerwy ', 'II, Long-term liabilities': 'II, Zobowiązania długoterminowe ', '1, To related parties': '1, Wobec jednostek powiązanych ', '2, To other entities': '2, Wobec pozostałych jednostek ', 'a, credits and loans': 'a, kredyty i pożyczki ', 'b, arising from issuance of debt securities': 'b, z tytułu emisji dłużnych papierów wartościowych', 'c, other financial liabilities': 'c, inne zobowiązania finansowe ', 'd, other': 'd, inne ', 'III, Short-term liabilities': 'III, Zobowiązania krótkoterminowe ', 'a, trade liabilities, maturing:': 'a, z tytułu dostaw i usług, o okresie wymagalności: ', 'd, trade liabilities, maturing:': 'd, z tytułu dostaw i usług, o okresie wymagalności: ', 'e, received advances for deliveries': 'e, zaliczki otrzymane na dostawy ', 'f, bill-of-exchange liabilities': 'f, zobowiązania wekslowe ', 'g, tax, customs, insurance and other liabilities': 'g, z tytułu podatków, ceł, ubezpieczeń i innych świadczeń ', 'h, payroll liabilities': 'h, z tytułu wynagrodzeń ', 'i, other': 'i, inne ', '3, Special funds': '3, Fundusze specjalne ', 'IV, Accruals': 'IV, Rozliczenia międzyokresowe ', '1, Negative goodwill': '1, Ujemna wartość firmy ', '2, Other accruals': '2, Inne rozliczenia międzyokresowe ', 'a, long-term': 'a, długoterminowe ', 'b, short-term': 'b, krótkoterminowe ', 'Total Liabilities': 'Pasywa Razem', 'A, Net revenues from sales and equivalent, including revenues:': 'A, Przychody netto ze sprzedaży i zrównane z nimi, w tym: ', '- from related parties': '- od jednostek powiązanych ', 'I, Net revenues from sales of products': 'I, Przychody netto ze sprzedaży produktów ', 'II, Change in the balance of products (increase - positive value, decrease - negative value)': 'II, Zmiana stanu produktów (zwiększenie - wartość dodatnia, zmniejszenie - wartość ujemna) ', 'III, Manufacturing cost of products for internal purposes': 'III, Koszt wytworzenia produktów na własne potrzeby jednostki ', 'IV, Net revenues from sales of goods and materials': 'IV, Przychody netto ze sprzedaży towarów i materiałów ', 'B, Operating expenses': 'B, Koszty działalności operacyjnej ', 'I, Amortisation and depreciation': 'I, Amortyzacja ', 'II, Consumption of materials and energy': 'II, Zużycie materiałów i energii ', 'III, External services': 'III, Usługi obce ', 'IV, Taxes and charges, including:': 'IV, Podatki i opłaty, w tym: ', '- excise duty': '- podatek akcyzowy', 'V, Payroll': 'V, Wynagrodzenia ', 'VI, Social security and other benefits': 'VI, Ubezpieczenia społeczne i inne świadczenia ', 'VII, Other costs by type': 'VII, Pozostałe koszty rodzajowe ', 'VIII, Value of goods and materials sold': 'VIII, Wartość sprzedanych towarów i materiałów ', 'C, Profit (loss) on sales': 'C, Zysk (strata) ze sprzedaży ', 'D, Other operating revenues': 'D, Pozostałe przychody operacyjne ', 'I, Gain on disposal of non-financial fixed assets': 'I, Zysk ze zbycia niefinansowych aktywów trwałych ', 'II, Subsidies': 'II, Dotacje ', 'III, Revaluation of non-financial fixed assets': 'III, Aktualizacja wartości aktywów niefinansowych', 'IV, Other operating revenues': 'IV, Inne przychody operacyjne ', 'E, Other operating expenses': 'E, Pozostałe koszty operacyjne', 'I, Loss on disposal of non-financial fixed assets': 'I, Strata ze zbycia niefinansowych aktywów trwałych ', 'II, Revaluation of non-financial assets': 'II, Aktualizacja wartości aktywów niefinansowych ', 'III, Other operating expenses': 'III, Inne koszty operacyjne ', 'F, Profit (loss) on operating activities': 'F, Zysk (strata) z działalności operacyjnej', 'G, Financial revenues': 'G, Przychody finansowe ', 'I, Dividend and profit sharing, including:': 'I, Dywidendy i udziały w zyskach, w tym: ', 'II, Interest, including:': 'II, Odsetki, w tym: ', 'III, Gain on disposal of investments': 'III, Zysk ze zbycia inwestycji ', 'IV, Revaluation of investments': 'IV, Aktualizacja wartości inwestycji ', 'V, Other': 'V, Inne ', 'H, Financial expenses': 'H, Koszty finansowe ', 'I, Interest, including:': 'I, Odsetki, w tym: ', '- for related parties': '- dla jednostek powiązanych ', 'II, Loss on disposal of investments': 'II, Strata ze zbycia inwestycji ', 'III, Revaluation of investments': 'III, Aktualizacja wartości inwestycji ', 'IV, Other': 'IV, Inne', "I, Profit (loss) on sale of the total or part of subsidiaries' shares": 'I, Zysk (strata) na sprzedaży całości lub części udziałów jednostek podporządkowanych', 'J, Profit (loss) on business activities': 'J, Zysk (strata) z działalności gospodarczej', 'K, Result on extraordinary events': 'K, Wynik zdarzeń nadzwyczajnych', 'I, Extraordinary gains': 'I, Zyski nadzwyczajne ', 'II, Extraordinary losses': 'II, Straty nadzwyczajne ', "L, Write-offs of company's goodwill": 'L, Odpis wartości firmy', "I, Write-offs of subsidiaries' goodwill": 'I, Odpis wartości firmy - jednostki zależne', "II, Write-offs of associated entities' goodwill": 'II, Odpis wartości firmy - jednostki współzależne', "III, Write-offs of affiliates' goodwill": 'III, Odpis wartości firmy - jednostki stowarzyszone', 'M, Write-off of negative goodwill': 'M, Odpis ujemnej wartości firmy', 'I, Write-off of negative goodwill - subsidiaries': 'I, Odpis ujemnej wartości firmy - jednostki zależne', 'II, Write-off of negative goodwill - associated entities': 'II, Odpis ujemnej wartości firmy - jednostki współzależne', 'III, Write-off of negative goodwill - affiliates': 'III, Odpis ujemnej wartości firmy - jednostki stowarzyszone', 'N, Proft before tax': 'N, Zysk (strata) brutto', 'O, Income tax': 'O, Podatek dochodowy ', 'a, current ': 'a, część bieżąca', 'b, deferred': 'b, część odroczona', 'P, Other statutory reductions in profit (increases in loss)': 'P, Pozostałe obowiązkowe zmniejszenie zysku (zwiększenia straty) ', 'Q, Profit (loss) on shares in subsidiaries valuated by means of equity method': 'Q, Zysk (strata) z udziałów w jednostkach podporządkowanych wycenianych metodą praw własności', 'R, Minorities profit (loss)': 'R, Zyski (straty) mniejszości', 'S, Net profit (loss)': 'S, Zysk (strata) netto', 'A, Cash flow on operating activities': 'A, Przepływy środków pieniężnych z działalności operacyjnej', 'I, Net profit (loss)': 'I, Zysk (strata) netto', 'II, Total adjustments': 'II, Korekty razem', '1, Profit (loss) of minority shareholders': '1, Zysk (strata) udziałowców mniejszościowych', '2, Profit (loss) from shares in associated entities': '2, Zysk (strata) z udziałów w jednostkach stowarzyszonych', '3. Depreciation': '3, Amortyzacja', '4, Profit (loss) on exchange rates differences': '4, Zyski (straty) z tytułu różnic kursowych', '5, Interest earned and share in profits (dividends)': '5, Odsetki i udziały w zyskach (dywidendy)', '6, Profit (loss) on investment activity': '6, Zysk (strata) z działalności inwestycyjnej', '7, Change in reserves': '7, Zmiana stanu rezerw', '8, Change in stock position': '8, Zmiana stanu zapasów', '9, Change in receivables': '9, Zmiana stanu należności', '10, Change of position of short-term liabilities, except for loans and borrowings': '10, Zmiana stanu zobowiązań krótkoterminowych, z wyjątkiem pożyczek i kredytów', '11, Change in prepayments and accruals': '11, Zmiana stanu rozliczeń międzyokresowych', '12, Other adjustments': '12, Inne korekty', 'III, Net cash flow on operating activities (I + II)': 'III, Przepływy pieniężne netto z działalności operacyjnej (I + II)', 'B, Cash flow on investment activities': 'B, Przepływy środków pieniężnych z działalności inwestycyjnych', 'I, Inflows': 'I, Wpływy', '1, Sale of intangible assets and tangible fixed assets': '1, Zbycie wartości niematerialnych i prawnych oraz rzeczowych aktywów trwałych', '2, Sale of real estate investments and intangible assets': '2, Zbycie inwestycji w nieruchomości oraz wartości niematerialne i prawne', '3, From financial assets, including:': '3, Z aktywów finansowych, w tym:', 'a), In affiliated units': 'a), w jednostkach powiązanych', '- sale of financial assets': '- zbycie aktywów finansowych', '- dividends and shares in profits': '- dywidendy i udziały w zyskach', '- repayment of granted long-term loans': '- spłata udzielonych pożyczek długoterminowych', '- interest': '- odsetki', 'b), In other entities': 'b), w pozostałych jednostkach', '- other finanzial inflows': '- inne wpływy z aktywów finansowych', '4, Other investment inflows': '4, Inne wpływy inwestycyjne', 'II, Outflows': 'II, Wydatki', '1, Purchase of intangible assets and tangible fixed assets': '1, Nabycie wartości niematerialnych i prawnych oraz rzeczowych aktywów trwałych', '2, Investment in real estate investments and intangible assets': '2, Inwestycje w nieruchomości oraz wartości niematerialne i prawne', '3, For financial assets, including:': '3, Na aktywa finansowe, w tym:', '- purchase of financial assets': '- nabycie aktywów finansowych', '- granted long-term loans': '- udzielone pożyczki długoterminowe', '4, Dividends and shares in profits paid to minority shareholders': '4, Dywidendy i inne udziały w zyskach wypłacone udziałowcom mniejszościowym', '5, Other investment expenses': '5, Inne wydatki inwestycyjne', 'III, Net cash flow on investment activities  (I-II)': 'III, Przepływy pieniężne netto z działalności inwestycyjnej (I-II)', 'C, Cash flow on financial activities': 'C, Przepływy środków pieniężnych z działalności finansowej', '1, Net inflows from issuance of shares and other capital instruments and additional payments to share capital': '1, Wpływy netto z wydania udziałów (emisji akcji) i innych instrumentów kapitałowych oraz dopłat do kapitału', '2, Loans and borrowings': '2, Kredyty i pożyczki', '3, Issuance of debt securities': '3, Emisja dłużnych papierów wartościowych', '4, Other financial inflows': '4, Inne wpływy finansowe', '1, Purchase of own shares': '1, Nabycie udziałów (akcji) własnych', '2, Dividends and other payments in favour of owners': '2, Dywidendy i inne wypłaty na rzecz właścicieli', '3, Outflows on division of earnings other than payments in favour of owners': '3, Inne, niż wypłaty na rzecz właścicieli, wydatki z tytułu podziału zysku', '4, Repayments of loans and borrowings': '4, Spłaty kredytów i pożyczek', '5, Redemption of debt securities': '5, Wykup dłużnych papierów wartościowych', '6, On other financial liabilities': '6, Z tytułu innych zobowiązań finansowych', '7, Payments of liabilities on financial leasing agreements': '7, Płatności zobowiązań z tytułu umów leasingu finansowego', '8, Interest': '8, Odsetki', '9, Other financial outflows': '9, Inne wydatki finansowe', 'III, Net cash flow from financial activity (I-II)': 'III, Przepływy pieniężne netto z działalności finansowej (I-II)', 'D, Total net cash flow (AIII + BIII + CIII)': 'D, Przepływy pieniężne netto razem (AIII + BIII + CIII)', 'E, Change in cash in balance sheet, including: Change in cash on exchange rate differences': 'E, Bilansowa zmiana stanu środków pieniężnych, w tym: zmiana stanu środków pieniężnych z tytułu różnic kursowych', '- Change in cash on exchange rate differences': '- zmiana stanu środków pieniężnych z tytułu różnic kursowych', 'F, Cash at the beginning of the period': 'F, Środki pieniężne na początek okresu', 'G, Cash at the end of the period (F + D):': 'G, Środki pieniężne na koniec okresu (F + D), w tym:', '- of limited capacity of disposing of': '- o ograniczonej możliwości dysponowania', 'A, Cash Flow From Operating Activity': 'A, Przepływy środków pieniężnych z działalności operacyjnej', '1, Sales Incomes': '1, Sprzedaż', '2, Other Incomes from Operating Activity': '2, Inne wpływy z działalności operacyjnej', '1, Deliveries and Services': '1, Dostawy i usługi', '2, Net Salaries': '2, Wynagrodzenia netto', '3, Social Security': '3, Ubezpieczenia społeczne i zdrowotne oraz inne świadczenia', '4, Taxes': '4, Podatki i opłaty o charakterze publicznoprawnym', '5, Other Operating Expenses': '5, Inne wydatki operacyjne', 'III, Net cash flow on operating activities': 'III, Przepływy pieniężne netto z działalności operacyjnej (I-II)', '- other financial inflows': '- inne wpływy z aktywów finansowych', '4, Other investment expenses': '4, Inne wydatki inwestycyjne'}
fin_cols_rename2 = {'ROA': 'Return on Assets (ROA)', 'ROAA': 'Annualised Return on Assets (ROA) ', 'ROE': 'Return on Equity (ROE)', 'ROEA': 'Annualised Return on Equity (ROE)', 'ROC': 'Return on Capital Employed', 'ROS': 'Net Profit Margin', 'GPM': 'Gross Profit Margin', 'OPM': 'Operating Profit Margin (ROS)', 'PREBITDA': 'EBITDA Margin', 'PROROA': 'Operating ROA', 'INVENTORYTURN': 'Inventory Turnover', 'ART': 'Trade Receivable Turnover', 'CAT': 'Current Asset Turnover', 'FAT': 'Non Current Assets Turnover ', 'AT': 'Total Asset Turnover', 'ERPT': 'Trade Payables Turnover', 'ERWCT': 'Working Capital Turnover', 'BOOKVALUE': 'Bookvalue (BV)', 'EV': 'Enterprise value ', 'NETCASH': 'Net Cash', 'DEBT': 'Debt', 'LTDEBT': 'Long term Debt', 'STDEBT': 'Short Term Debt', 'NET_DEBT': 'Net Debt', 'MKCP': 'Market Capitalization', 'TRWC': 'Working Capital', 'CEMPL': 'Capital Employed', 'CR': 'Current Ratio', 'QR': 'Quick ratio', 'DOOMSDAY': "Doom's day ratio", 'LRCR': 'Cash Ratio', 'LRCFO': 'Operating Cash Flow Ratio', 'DEBTTOASSETS': 'Debt to total assets ratio', 'DEBTTOEQUITY': 'Debt to equity ratio', 'LTDC': 'Long Term Debt to Capital Employed', 'DEBTTOEBITDA': 'Debt / EBITDA', 'DEBTEV': 'Debt / Enterprise Value ', 'LTDCF': 'Net Cash Flow to Debt ', 'LEVERAGE': 'Assets to Equity Ratio', 'RT': 'Net Sales Revenue Trend ', 'TRNSR': 'Total Operating Revenue Trend', 'TRGP': 'Gross Profit Trend', 'TREBITDA': 'EBITDA Trend', 'OIT': 'Operating Profit Trend', 'NIT': 'Net Profit Trend ', 'TRAR': 'Accounts Receivables Trend', 'TRINV': 'Inventory Trend', 'TRPPE': 'Net Property, Plant and Equipment (PP&E) Trend', 'TRTA': 'Total Assets Trend', 'TRBV': 'Bookvalue Trend', 'TRSE': "Shareholders' Equity Trend", 'TRCFO': 'Operating Cash Flow Trend', 'TRCE': 'Capital Expenditures Trend', 'ICR': 'Interest Coverage Ratio', 'CRDC': 'Operating Cash Flow to Debt', 'PRCFR': 'Operating Cash Flow to Revenue', 'PRCFA': 'Operating Cash Flow to Assets', 'PRCRE': 'Operating Cash Flow to Equity', 'PRCI': 'Operating Cash Flow to EBIT', 'BSCA': 'Cash / Total Assets', 'BSRTA': 'Receivables / Total Assets', 'BSITA': 'Inventories/Total Assets', 'BSFATA': 'Fixed assets/Total Assets', 'BSCLTL': 'Current Liabilities/Total Liabilities', 'EXPORTR': 'Export proportion', 'ISSEBNS': 'Salaries and Employee Benefits/Net sales', 'ISAENS': 'Administrative Expenses/Net Sales', 'ISDANS': 'Depreciation and Amortization/Net sales', 'ISIPNS': 'Interest paid/Net sales', 'ISITNS': 'Income tax/Net sales', 'CFOCFTCF': 'Operating Cash Flow to Total Cash Flow', 'CFCFITCF': 'Investing Cash Flow to Total Cash Flow', 'CFCFFTCF': 'Financing Cash Flow to Total Cash Flow', 'BRCIR': 'Cost to Income Ratio', 'BRER': 'Bank Efficiency Ratio', 'BRLDR': 'Loans to Deposits Ratio', 'BRLDRO': 'Loans to Customers to Deposits From Customers', 'BRLADR': 'Liquid Assets to Deposits Ratio', 'BRLADRO': 'Liquid Assets to Deposits From Customers Ratio', 'BRLAR': 'Loans to Asset Ratio', 'BRLARO': 'Loans to Customers to Asset Ratio', 'BRNIIT': 'Net Interest Income Trend', 'BRNFCIT': 'Net Fee and Commission Income Trend', 'BRLACT': 'Loans and Advances to Customers Trend', 'BRLACTO': 'Loans and Advances Trend', 'BRDCT': 'Deposits from Customers Trend', 'BRDCTO': 'Deposits Trend', 'BRERA': 'Earning Assets', 'BRAYA': 'Yield on Earning Assets (YEA)', 'BRNIM': 'Net Interest Margin', 'IRLR': 'Loss Ratio', 'IRUER': 'Underwriting Expenses Ratio', 'IRCPR': 'Ceeded Premium Ratio', 'IRNPET': 'Net Premiums Earned Trend', 'IRFCT': 'Fees and Commissions Trend', 'IRNIIT': 'Net Investment Income Trend', 'IRRADIOT': 'Receivables Arising Out Of Direct Insurance Operations Trend', 'MMEPS': 'EPS', 'MMPER': 'P/E', 'MMPSA': 'Market Capitalization/Net Sales (Price Sales Ratio)', 'MMPGI': 'Market Capitalization/Gross Profit', 'MARKETCAP/EBITDA': 'Market Capitalization/EBITDA', 'MMPEBIT': 'Market Capitalization/EBIT', 'MMPTA': 'Market Capitalization/Total Assets', 'MCAP/EQ': "Market capitalization/shareholders' equity", 'P/BR': 'Market Capitalization/Book Value', 'MMPIC': 'Market Capitalization / Capital Employed', 'MMPOCF': 'Market Capitalization/Operating Cashflow', 'EVNS': 'Enterprise value/Net Sales', 'EVGI': 'Enterprise value/Gross Profit', 'EVEBITDA': 'Enterprise Value/EBITDA', 'EVEBIT': 'Enterprise value/EBIT', 'EVTA': 'Enterprise value/Total Assets', 'EVIC': 'Enterprise value / Capital Employed', 'EVOCF': 'Enterprise value/Operating Cashflow', 'TS': 'Assets', 'TANG': 'Property, plant and equipment', 'INT': 'Intangible assets and goodwill', 'CE': 'Cash and cash equivalents', 'SE': 'Total equity', 'SEOWN': 'Equity attributable to owners of the parent', 'ISSUED': 'Issued capital', 'ISSUEDORD': 'Ordinary shares', 'ISSUEDPREF': 'Preferred shares', 'SEOWNPREMIUM': 'Share premium', 'SEOWNTREASURY': 'Treasury shares', 'SEOWNREVALUATION': 'Revaluation reserve', 'SEOWNFOREIGNCURR': 'Foreign currency translation reserve', 'PROFITRESERV': 'Retained earnings', 'BSPROFIT': 'Balance-sheet profit or loss figure', 'SEMIN': 'Minority interest', 'TL': 'Total Liabilities', 'TR': 'Total operating revenue', 'OP': 'Operating profit (EBIT)', 'PRETAX': 'Profit before income tax', 'TAX': 'Income tax', 'TAXDUE': 'Tax difference due to consolidation', 'AFTERTAX': 'Profit after income tax', 'AFTERTAXDISC': 'Profit from discontinued operations', 'NP': 'Net Profit', 'COMPREHENSOTH': 'Other comprehensive result for the period, net of tax', 'AFTERTAXTOTAL': 'Profit for the period', 'OUTSIDE': 'From this minority interest', 'CFNCFOPERATING': 'Net cash flow from (used in) operating activities', 'CFNCFINVEST': 'Net cash flow from (used in) investing activities', 'CFNCFFINANCE': 'Net cash flow from (used in) financing activities', 'CFNETINCREASECASH': 'Net increase (decrease) in cash and cash equivalents', 'CFCASHBEGIN': 'Cash at the beginning of the period', 'CFCASHFOREX': 'Exchange gains (losses) on cash and cash equivalents', 'CFCASHEND': 'Cash at the end of the period', 'CFFCF': 'Free cash flow', 'CFCAPEX': 'CAPEX', 'MIN': 'Lower Limit of Revenue Range', 'MAX': 'Upper Limit of Revenue Range'}
fin_cols_rename_full = {**fin_cols_rename, **fin_cols_rename2}
"""
