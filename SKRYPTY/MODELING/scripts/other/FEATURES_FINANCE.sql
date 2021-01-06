USE modeling
-- CLOSED
SELECT x.* INTO modeling.finance


FROM (
SELECT [NIP], [NetSalesRevenue], [OperatingProfitEBIT], ABS([EmployeeBenefitExpense]) AS [EmployeeBenefitExpense],
	   [TotalAssets], [NetProfitLossForThePeriod], [PropertyPlantAndEquipment],
	   [CashandCashEquivalents], [TotalEquity], [IssuedCapital],
	   [WorkingCapital], [RetainedEarnings], [TotalLiabilities], [CurrentLiabilities], [NonCurrentLiabilities],
	   [ProfitBeforeIncomeTax], [IncomeTax], [DepreciationImpairment], [DepreciationAmortization], [CurrentAssets], [ROE], [ROA], [ROS], [FiscalYear],
	   CASE WHEN [WorkingCapital] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [WorkingCapital] / [TotalAssets] END AS [A1],
	   CASE WHEN [RetainedEarnings] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [RetainedEarnings] / [TotalAssets] END AS [A2],
	   CASE WHEN [OperatingProfitEBIT] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [OperatingProfitEBIT] / [TotalAssets] END AS [A3],
	   CASE WHEN [TotalEquity] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			ELSE [TotalEquity] / [TotalLiabilities] END AS [A4],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [NetSalesRevenue] / [TotalAssets] END AS [A5],
	  -- OTHERS
	   CASE WHEN [NetSalesRevenue] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			-- ALL VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NOT NULL AND
				 [DepreciationAmortization] IS NOT NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] - [DepreciationImpairment] + [DepreciationAmortization]) / [TotalLiabilities]
			-- NSR I AMORTIZATION VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NULL AND
				 [DepreciationAmortization] IS NOT NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] + [DepreciationAmortization]) / [TotalLiabilities]
			-- NSR I DEPRECIATION VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NOT NULL AND
				 [DepreciationAmortization] IS NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] - [DepreciationImpairment]) / [TotalLiabilities]
			-- ONLY NSR VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NULL AND
				 [DepreciationAmortization] IS NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN [NetSalesRevenue] / [TotalLiabilities] END AS [P3],
	   CASE WHEN [EmployeeBenefitExpense] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE ABS([EmployeeBenefitExpense]) / [CurrentLiabilities] END AS [P4],
	   
	   CASE WHEN [TotalEquity] IS NULL OR [TotalAssets] IS NULL OR ([TotalAssets] - [CurrentAssets]) = 0 THEN NULL
			WHEN [TotalAssets] IS NOT NULL AND [CurrentAssets] IS NOT NULL AND
				 ([TotalAssets] - [CurrentAssets]) = 0 AND
				 [TotalEquity] IS NOT NULL AND [TotalEquity] != 0 AND
				 [NonCurrentLiabilities] IS NULL
			THEN [TotalEquity] / ([TotalAssets] - [CurrentAssets])
			ELSE ([TotalEquity] + [NonCurrentLiabilities]) / ([TotalAssets] - [CurrentAssets])
			END AS [X6],
	   
	   CASE WHEN [CurrentAssets] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE [CurrentAssets] / [CurrentLiabilities] END AS [X8],
	   CASE WHEN [CurrentLiabilities] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [CurrentLiabilities] / [TotalAssets] END AS [X9],
	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE [ProfitBeforeIncomeTax] / [CurrentLiabilities] END AS [X10],
	   CASE WHEN [TotalAssets] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			ELSE [TotalAssets] / [TotalLiabilities] END AS [X11],
	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [NetSalesRevenue] IS NULL OR [NetSalesRevenue] = 0 THEN NULL
			ELSE [ProfitBeforeIncomeTax] / [NetSalesRevenue] END AS [X13],

	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			WHEN [ProfitBeforeIncomeTax] IS NOT NULL AND
				 [IncomeTax] IS NOT NULL AND 
				 [TotalAssets] IS NOT NULL AND [TotalAssets] != 0
			THEN ([ProfitBeforeIncomeTax] - [IncomeTax]) / [TotalAssets]
			WHEN [ProfitBeforeIncomeTax] IS NOT NULL AND
				 [IncomeTax] IS NULL AND 
				 [TotalAssets] IS NOT NULL AND [TotalAssets] != 0
			THEN [ProfitBeforeIncomeTax] / [TotalAssets] 
			ELSE [ProfitBeforeIncomeTax] / [TotalAssets] END AS [X14],
	   
	   -- FAIT
	   CASE WHEN [OperatingProfitEBIT] IS NULL OR [NetSalesRevenue] IS NULL OR [NetSalesRevenue] = 0 THEN NULL
			ELSE [OperatingProfitEBIT] / [NetSalesRevenue] END AS [BruttoMargin],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [CashandCashEquivalents] IS NULL OR [CashandCashEquivalents] = 0 THEN NULL
			ELSE [NetSalesRevenue] / [CashandCashEquivalents] END AS [RevenueToCash],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [EmployeeBenefitExpense] IS NULL OR [EmployeeBenefitExpense] = 0 THEN NULL
			ELSE [NetSalesRevenue] / ABS([EmployeeBenefitExpense]) END AS [RevenueToWages]
FROM [finance].[closed]

UNION
-- LIQUIDATED
SELECT [NIP], [NetSalesRevenue], [OperatingProfitEBIT], ABS([EmployeeBenefitExpense]) AS [EmployeeBenefitExpense],
	   [TotalAssets], [NetProfitLossForThePeriod], [PropertyPlantAndEquipment],
	   [CashandCashEquivalents], [TotalEquity], [IssuedCapital],
	   [WorkingCapital], [RetainedEarnings], [TotalLiabilities], [CurrentLiabilities], [NonCurrentLiabilities],
	   [ProfitBeforeIncomeTax], [IncomeTax], [DepreciationImpairment], [DepreciationAmortization], [CurrentAssets], [ROE], [ROA], [ROS], [FiscalYear],
	   CASE WHEN [WorkingCapital] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [WorkingCapital] / [TotalAssets] END AS [A1],
	   CASE WHEN [RetainedEarnings] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [RetainedEarnings] / [TotalAssets] END AS [A2],
	   CASE WHEN [OperatingProfitEBIT] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [OperatingProfitEBIT] / [TotalAssets] END AS [A3],
	   CASE WHEN [TotalEquity] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			ELSE [TotalEquity] / [TotalLiabilities] END AS [A4],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [NetSalesRevenue] / [TotalAssets] END AS [A5],
	  -- OTHERS
	   CASE WHEN [NetSalesRevenue] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			-- ALL VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NOT NULL AND
				 [DepreciationAmortization] IS NOT NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] - [DepreciationImpairment] + [DepreciationAmortization]) / [TotalLiabilities]
			-- NSR I AMORTIZATION VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NULL AND
				 [DepreciationAmortization] IS NOT NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] + [DepreciationAmortization]) / [TotalLiabilities]
			-- NSR I DEPRECIATION VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NOT NULL AND
				 [DepreciationAmortization] IS NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] - [DepreciationImpairment]) / [TotalLiabilities]
			-- ONLY NSR VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NULL AND
				 [DepreciationAmortization] IS NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN [NetSalesRevenue] / [TotalLiabilities] END AS [P3],
	   CASE WHEN [EmployeeBenefitExpense] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE ABS([EmployeeBenefitExpense]) / [CurrentLiabilities] END AS [P4],
	   
	   CASE WHEN [TotalEquity] IS NULL OR [TotalAssets] IS NULL OR ([TotalAssets] - [CurrentAssets]) = 0 THEN NULL
			WHEN [TotalAssets] IS NOT NULL AND [CurrentAssets] IS NOT NULL AND
				 ([TotalAssets] - [CurrentAssets]) = 0 AND
				 [TotalEquity] IS NOT NULL AND [TotalEquity] != 0 AND
				 [NonCurrentLiabilities] IS NULL
			THEN [TotalEquity] / ([TotalAssets] - [CurrentAssets])
			ELSE ([TotalEquity] + [NonCurrentLiabilities]) / ([TotalAssets] - [CurrentAssets])
			END AS [X6],
	   
	   CASE WHEN [CurrentAssets] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE [CurrentAssets] / [CurrentLiabilities] END AS [X8],
	   CASE WHEN [CurrentLiabilities] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [CurrentLiabilities] / [TotalAssets] END AS [X9],
	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE [ProfitBeforeIncomeTax] / [CurrentLiabilities] END AS [X10],
	   CASE WHEN [TotalAssets] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			ELSE [TotalAssets] / [TotalLiabilities] END AS [X11],
	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [NetSalesRevenue] IS NULL OR [NetSalesRevenue] = 0 THEN NULL
			ELSE [ProfitBeforeIncomeTax] / [NetSalesRevenue] END AS [X13],

	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			WHEN [ProfitBeforeIncomeTax] IS NOT NULL AND
				 [IncomeTax] IS NOT NULL AND 
				 [TotalAssets] IS NOT NULL AND [TotalAssets] != 0
			THEN ([ProfitBeforeIncomeTax] - [IncomeTax]) / [TotalAssets]
			WHEN [ProfitBeforeIncomeTax] IS NOT NULL AND
				 [IncomeTax] IS NULL AND 
				 [TotalAssets] IS NOT NULL AND [TotalAssets] != 0
			THEN [ProfitBeforeIncomeTax] / [TotalAssets] 
			ELSE [ProfitBeforeIncomeTax] / [TotalAssets] END AS [X14],
	   
	   -- FAIT
	   CASE WHEN [OperatingProfitEBIT] IS NULL OR [NetSalesRevenue] IS NULL OR [NetSalesRevenue] = 0 THEN NULL
			ELSE [OperatingProfitEBIT] / [NetSalesRevenue] END AS [BruttoMargin],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [CashandCashEquivalents] IS NULL OR [CashandCashEquivalents] = 0 THEN NULL
			ELSE [NetSalesRevenue] / [CashandCashEquivalents] END AS [RevenueToCash],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [EmployeeBenefitExpense] IS NULL OR [EmployeeBenefitExpense] = 0 THEN NULL
			ELSE [NetSalesRevenue] / ABS([EmployeeBenefitExpense]) END AS [RevenueToWages]
FROM [finance].[liquidated]

UNION
-- INVESTIGATED
SELECT [NIP], [NetSalesRevenue], [OperatingProfitEBIT], ABS([EmployeeBenefitExpense]) AS [EmployeeBenefitExpense],
	   [TotalAssets], [NetProfitLossForThePeriod], [PropertyPlantAndEquipment],
	   [CashandCashEquivalents], [TotalEquity], [IssuedCapital],
	   [WorkingCapital], [RetainedEarnings], [TotalLiabilities], [CurrentLiabilities], [NonCurrentLiabilities],
	   [ProfitBeforeIncomeTax], [IncomeTax], [DepreciationImpairment], [DepreciationAmortization], [CurrentAssets], [ROE], [ROA], [ROS], [FiscalYear],
	   CASE WHEN [WorkingCapital] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [WorkingCapital] / [TotalAssets] END AS [A1],
	   CASE WHEN [RetainedEarnings] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [RetainedEarnings] / [TotalAssets] END AS [A2],
	   CASE WHEN [OperatingProfitEBIT] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [OperatingProfitEBIT] / [TotalAssets] END AS [A3],
	   CASE WHEN [TotalEquity] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			ELSE [TotalEquity] / [TotalLiabilities] END AS [A4],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [NetSalesRevenue] / [TotalAssets] END AS [A5],
	  -- OTHERS
	   CASE WHEN [NetSalesRevenue] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			-- ALL VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NOT NULL AND
				 [DepreciationAmortization] IS NOT NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] - [DepreciationImpairment] + [DepreciationAmortization]) / [TotalLiabilities]
			-- NSR I AMORTIZATION VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NULL AND
				 [DepreciationAmortization] IS NOT NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] + [DepreciationAmortization]) / [TotalLiabilities]
			-- NSR I DEPRECIATION VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NOT NULL AND
				 [DepreciationAmortization] IS NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] - [DepreciationImpairment]) / [TotalLiabilities]
			-- ONLY NSR VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NULL AND
				 [DepreciationAmortization] IS NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN [NetSalesRevenue] / [TotalLiabilities] END AS [P3],
	   CASE WHEN [EmployeeBenefitExpense] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE ABS([EmployeeBenefitExpense]) / [CurrentLiabilities] END AS [P4],
	   
	   CASE WHEN [TotalEquity] IS NULL OR [TotalAssets] IS NULL OR ([TotalAssets] - [CurrentAssets]) = 0 THEN NULL
			WHEN [TotalAssets] IS NOT NULL AND [CurrentAssets] IS NOT NULL AND
				 ([TotalAssets] - [CurrentAssets]) = 0 AND
				 [TotalEquity] IS NOT NULL AND [TotalEquity] != 0 AND
				 [NonCurrentLiabilities] IS NULL
			THEN [TotalEquity] / ([TotalAssets] - [CurrentAssets])
			ELSE ([TotalEquity] + [NonCurrentLiabilities]) / ([TotalAssets] - [CurrentAssets])
			END AS [X6],
	   
	   CASE WHEN [CurrentAssets] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE [CurrentAssets] / [CurrentLiabilities] END AS [X8],
	   CASE WHEN [CurrentLiabilities] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [CurrentLiabilities] / [TotalAssets] END AS [X9],
	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE [ProfitBeforeIncomeTax] / [CurrentLiabilities] END AS [X10],
	   CASE WHEN [TotalAssets] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			ELSE [TotalAssets] / [TotalLiabilities] END AS [X11],
	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [NetSalesRevenue] IS NULL OR [NetSalesRevenue] = 0 THEN NULL
			ELSE [ProfitBeforeIncomeTax] / [NetSalesRevenue] END AS [X13],

	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			WHEN [ProfitBeforeIncomeTax] IS NOT NULL AND
				 [IncomeTax] IS NOT NULL AND 
				 [TotalAssets] IS NOT NULL AND [TotalAssets] != 0
			THEN ([ProfitBeforeIncomeTax] - [IncomeTax]) / [TotalAssets]
			WHEN [ProfitBeforeIncomeTax] IS NOT NULL AND
				 [IncomeTax] IS NULL AND 
				 [TotalAssets] IS NOT NULL AND [TotalAssets] != 0
			THEN [ProfitBeforeIncomeTax] / [TotalAssets] 
			ELSE [ProfitBeforeIncomeTax] / [TotalAssets] END AS [X14],
	   
	   -- FAIT
	   CASE WHEN [OperatingProfitEBIT] IS NULL OR [NetSalesRevenue] IS NULL OR [NetSalesRevenue] = 0 THEN NULL
			ELSE [OperatingProfitEBIT] / [NetSalesRevenue] END AS [BruttoMargin],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [CashandCashEquivalents] IS NULL OR [CashandCashEquivalents] = 0 THEN NULL
			ELSE [NetSalesRevenue] / [CashandCashEquivalents] END AS [RevenueToCash],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [EmployeeBenefitExpense] IS NULL OR [EmployeeBenefitExpense] = 0 THEN NULL
			ELSE [NetSalesRevenue] / ABS([EmployeeBenefitExpense]) END AS [RevenueToWages]
FROM [finance].[liquidated]

-- OPRATIONAL
UNION
SELECT [NIP], [NetSalesRevenue], [OperatingProfitEBIT], ABS([EmployeeBenefitExpense]) AS [EmployeeBenefitExpense],
	   [TotalAssets], [NetProfitLossForThePeriod], [PropertyPlantAndEquipment],
	   [CashandCashEquivalents], [TotalEquity], [IssuedCapital],
	   [WorkingCapital], [RetainedEarnings], [TotalLiabilities], [CurrentLiabilities], [NonCurrentLiabilities],
	   [ProfitBeforeIncomeTax], [IncomeTax], [DepreciationImpairment], [DepreciationAmortization], [CurrentAssets], [ROE], [ROA], [ROS], [FiscalYear],
	   CASE WHEN [WorkingCapital] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [WorkingCapital] / [TotalAssets] END AS [A1],
	   CASE WHEN [RetainedEarnings] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [RetainedEarnings] / [TotalAssets] END AS [A2],
	   CASE WHEN [OperatingProfitEBIT] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [OperatingProfitEBIT] / [TotalAssets] END AS [A3],
	   CASE WHEN [TotalEquity] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			ELSE [TotalEquity] / [TotalLiabilities] END AS [A4],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [NetSalesRevenue] / [TotalAssets] END AS [A5],
	  -- OTHERS
	   CASE WHEN [NetSalesRevenue] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			-- ALL VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NOT NULL AND
				 [DepreciationAmortization] IS NOT NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] - [DepreciationImpairment] + [DepreciationAmortization]) / [TotalLiabilities]
			-- NSR I AMORTIZATION VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NULL AND
				 [DepreciationAmortization] IS NOT NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] + [DepreciationAmortization]) / [TotalLiabilities]
			-- NSR I DEPRECIATION VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NOT NULL AND
				 [DepreciationAmortization] IS NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN ([NetSalesRevenue] - [DepreciationImpairment]) / [TotalLiabilities]
			-- ONLY NSR VALID
			WHEN [NetSalesRevenue] IS NOT NULL AND
				 [DepreciationImpairment] IS NULL AND
				 [DepreciationAmortization] IS NULL AND
				 [TotalLiabilities] IS NOT NULL AND [TotalLiabilities] != 0
			THEN [NetSalesRevenue] / [TotalLiabilities] END AS [P3],
	   CASE WHEN [EmployeeBenefitExpense] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE ABS([EmployeeBenefitExpense]) / [CurrentLiabilities] END AS [P4],
	   
	   CASE WHEN [TotalEquity] IS NULL OR [TotalAssets] IS NULL OR ([TotalAssets] - [CurrentAssets]) = 0 THEN NULL
			WHEN [TotalAssets] IS NOT NULL AND [CurrentAssets] IS NOT NULL AND
				 ([TotalAssets] - [CurrentAssets]) = 0 AND
				 [TotalEquity] IS NOT NULL AND [TotalEquity] != 0 AND
				 [NonCurrentLiabilities] IS NULL
			THEN [TotalEquity] / ([TotalAssets] - [CurrentAssets])
			ELSE ([TotalEquity] + [NonCurrentLiabilities]) / ([TotalAssets] - [CurrentAssets])
			END AS [X6],
	   
	   CASE WHEN [CurrentAssets] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE [CurrentAssets] / [CurrentLiabilities] END AS [X8],
	   CASE WHEN [CurrentLiabilities] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			ELSE [CurrentLiabilities] / [TotalAssets] END AS [X9],
	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [CurrentLiabilities] IS NULL OR [CurrentLiabilities] = 0 THEN NULL
			ELSE [ProfitBeforeIncomeTax] / [CurrentLiabilities] END AS [X10],
	   CASE WHEN [TotalAssets] IS NULL OR [TotalLiabilities] IS NULL OR [TotalLiabilities] = 0 THEN NULL
			ELSE [TotalAssets] / [TotalLiabilities] END AS [X11],
	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [NetSalesRevenue] IS NULL OR [NetSalesRevenue] = 0 THEN NULL
			ELSE [ProfitBeforeIncomeTax] / [NetSalesRevenue] END AS [X13],

	   CASE WHEN [ProfitBeforeIncomeTax] IS NULL OR [TotalAssets] IS NULL OR [TotalAssets] = 0 THEN NULL
			WHEN [ProfitBeforeIncomeTax] IS NOT NULL AND
				 [IncomeTax] IS NOT NULL AND 
				 [TotalAssets] IS NOT NULL AND [TotalAssets] != 0
			THEN ([ProfitBeforeIncomeTax] - [IncomeTax]) / [TotalAssets]
			WHEN [ProfitBeforeIncomeTax] IS NOT NULL AND
				 [IncomeTax] IS NULL AND 
				 [TotalAssets] IS NOT NULL AND [TotalAssets] != 0
			THEN [ProfitBeforeIncomeTax] / [TotalAssets] 
			ELSE [ProfitBeforeIncomeTax] / [TotalAssets] END AS [X14],
	   
	   -- FAIT
	   CASE WHEN [OperatingProfitEBIT] IS NULL OR [NetSalesRevenue] IS NULL OR [NetSalesRevenue] = 0 THEN NULL
			ELSE [OperatingProfitEBIT] / [NetSalesRevenue] END AS [BruttoMargin],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [CashandCashEquivalents] IS NULL OR [CashandCashEquivalents] = 0 THEN NULL
			ELSE [NetSalesRevenue] / [CashandCashEquivalents] END AS [RevenueToCash],
	   CASE WHEN [NetSalesRevenue] IS NULL OR [EmployeeBenefitExpense] IS NULL OR [EmployeeBenefitExpense] = 0 THEN NULL
			ELSE [NetSalesRevenue] / ABS([EmployeeBenefitExpense]) END AS [RevenueToWages]
FROM [finance].[operational] ) x

