SELECT x.* INTO [modeling].[all]
FROM (
SELECT m.[NIP], m.[REGON], m.[KRS], m.[EMISID], m.[DataUpadlosci], f.[FiscalYear], m.[Label], m.[Wiek],
	   m.[Voivodeship], m.[City], m.[LegalForm], m.[EMISLegalForm], m.[RodzajRejestru], m.[FormaFinansowania],
	   m.[FormaWlasnosci], m.[JednostkiLokalne], m.[SpecialLegalForm], LEFT(m.[MainPKD], 3) AS [MainPKD], m.[SecondaryPKDCount],
	   m.[Ryzykowna dzia³alnosc g³ówna], m.[Ryzykowne dzia³alnosci dodatkowe], m.[NoWebsite], m.[PublicMail],
	   m.[NoMail], m.[NoFax], m.[Podmiot zarejestrowany pod adresem wirtualnego biura], m.[Adres z numerem lokalu],
	   m.[CAAC import], m.[CAAC eksport], m.[ActiveLicenses], m.[RevertedLicenses], m.[ExpiredLicenses],
	   m.[EntityListedInVATRegistry], m.[StatusVAT], m.[VirtualAccountsPresence], m.[RiskyRemovalBasis], m.[RemovalDaysAgo],
	   m.[DeclaredAccountsCount], m.[RepresentationCount], m.[PhoneNotPresent], m.[CompanyType], m.[NumberOfEmployees],
	   m.[LatestMarketCapitalization], m.[ExecutivesCount], m.[OwnersCount], m.[AffiliatesCount], m.[ExternalIdsOthers],
	   m.[MainNAICSCodes], m.[MainNAICSCount], m.[SecondaryNAICSCount], m.[MainProductsNull], m.[DescriptionNull],
	   m.[RegisteredCapitalValue], m.[AuditDaysAgo], m.[PreviousNamesCount], m.[PreviousNameChangeYearsAgo],
	   m.[DividendCount], m.[DividendSum], m.[SegmentName], m.[SegmentStockName],
	   --FINANCE
	   f.[NetSalesRevenue], f.[OperatingProfitEBIT], f.[EmployeeBenefitExpense], f.[TotalAssets], f.[NetProfitLossForThePeriod],
	   f.[PropertyPlantAndEquipment], f.[CashandCashEquivalents], f.[TotalEquity], f.[IssuedCapital], f.[WorkingCapital],
	   f.[RetainedEarnings], f.[TotalLiabilities], f.[CurrentLiabilities], f.[NonCurrentLiabilities], f.[ProfitBeforeIncomeTax],
	   f.[IncomeTax], f.[DepreciationImpairment], f.[DepreciationAmortization], f.[CurrentAssets], f.[ROE], f.[ROA], f.[ROS],
	   f.[A1], f.[A2], f.[A3], f.[A4], f.[A5], f.[P3], f.[P4], f.[X6], f.[X8], f.[X9], f.[X10], f.[X11], f.[X13],
	   f.[X14], f.[BruttoMargin], f.[RevenueToCash], f.[RevenueToWages]
FROM [modeling].[merged] m
LEFT JOIN modeling.finance f
ON m.NIP = f.NIP ) x
