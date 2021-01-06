USE modeling
SELECT x.* INTO modeling_data
FROM (
-- LIQUIDATED
SELECT g.NIP, g.REGON, g.KRS, r.EMISID, r.[DataUpadlosci], g.[CompanyName], 1 AS [Label],
	   g.[Wiek], g.[Voivodeship], g.[City], g.[LegalForm], r.[EMISLegalForm], g.[RodzajRejestru],
	   g.[FormaFinansowania], g.[FormaWlasnosci], g.[JednostkiLokalne], g.[SpecialLegalForm], g.[MainPKD],
	   CASE WHEN g.[SecondaryPKDCount] IS NULL THEN 0 ELSE g.[SecondaryPKDCount] END AS [SecondaryPKDCount],
	   g.[Ryzykowna dzia³alnosc g³ówna], g.[Ryzykowne dzia³alnosci dodatkowe], --g.[Dzialalnosc zawieszona (i niewznowiona)], 
	   CASE WHEN g.[Brak strony WWW] = 1 AND r.[WebsiteNotPresent] = 1 THEN 1 ELSE 0 END AS [NoWebsite], -- g.[Brak strony WWW], r.[WebsiteNotPresent], 
	   CASE WHEN g.[Adres email na domenie publicznej] = 1 OR r.[EmailAdressPublic] = 1 THEN 1 ELSE 0 END AS [PublicMail], -- g.[Adres email na domenie publicznej], r.[EmailAdressPublic], 
	   CASE WHEN g.[NoMailAdress] = 1 AND r.[EmailAdressNotPresent] = 1 THEN 1 ELSE 0 END AS [NoMail], -- g.[NoMailAdress], r.[EmailAdressNotPresent], 
	   CASE WHEN g.[NoFax] = 1 AND r.[FaxNotPresent] = 1 THEN 1 ELSE 0 END AS [NoFax], -- g.[NoFax], r.[FaxNotPresent],
	   g.[Podmiot zarejestrowany pod adresem wirtualnego biura],
	   g.[Adres z numerem lokalu], --r.[AddresFlat], CASE WHEN g.[Adres z numerem lokalu] = 1 AND r.[AddresFlat] = 1 THEN 1 ELSE 0 END AS [FlatAdress],
	   g.[CAAC import], g.[CAAC eksport],
	   CASE WHEN g.[ActiveLicenses] IS NULL THEN 0 ELSE g.[ActiveLicenses] END AS [ActiveLicenses],
	   CASE WHEN g.[RevertedLicenses] IS NULL THEN 0 ELSE g.[RevertedLicenses] END AS [RevertedLicenses],
	   CASE WHEN g.[ExpiredLicenses] IS NULL THEN 0 ELSE g.[ExpiredLicenses] END AS [ExpiredLicenses],
	   v.[EntityListedInVATRegistry], v.[StatusVAT], v.[VirtualAccountsPresence],
	   CASE WHEN v.[RiskyRemovalBasis] IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL
			WHEN v.[RiskyRemovalBasis] IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 'NeverRemoved'
			WHEN v.[RiskyRemovalBasis] = 0 THEN 'NaturalReason'
			WHEN v.[RiskyRemovalBasis] = 1 THEN 'PotentialyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 2 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 2.5 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 3 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 4 THEN 'LikelyFraudulent'
			END AS [RiskyRemovalBasis],
	   CASE WHEN DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL -- r.DataUpadlosci v.[CheckDate]
			WHEN DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 0
			ELSE DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) END AS [RemovalDaysAgo],
	   CASE WHEN v.[DeclaredAccountsCount] IS NOT NULL THEN v.[DeclaredAccountsCount]
			WHEN v.[DeclaredAccountsCount] IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 0
			WHEN v.[DeclaredAccountsCount] IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL END AS [DeclaredAccountsCount],
	   CASE WHEN v.[RepresentationCount] IS NOT NULL THEN v.[RepresentationCount]
			WHEN v.[RepresentationCount] IS NULL AND v.[RepresentationCount] = 1 THEN 0
			WHEN v.[RepresentationCount] IS NULL AND v.[RepresentationCount] = 0 THEN NULL END AS [RepresentationCount],
	   r.[PhoneNotPresent], r.[CompanyType], r.[NumberOfEmployees],
	   --CAST(r.[LatestMarketCapitalization] AS float),
	   CASE WHEN r.[LatestMarketCapitalization] IS NULL THEN '0'
			ELSE r.[LatestMarketCapitalization] END AS [LatestMarketCapitalization],
	   r.[ExecutivesCount], r.[OwnersCount], r.[AffiliatesCount], r.[ExternalIdsOthers], r.[MainNAICSCodes], r.[MainNAICSCount],
	   CASE WHEN r.[SecondaryNAICSCount] IS NULL THEN 0 ELSE r.[SecondaryNAICSCount] END AS [SecondaryNAICSCount],
	   r.[MainProductsNull], r.[DescriptionNull], r.[RegisteredCapitalValue],
	   CASE WHEN DATEDIFF(day, r.[AuditDate], r.[DataUpadlosci]) IS NULL THEN 0
			ELSE DATEDIFF(day, r.[AuditDate], r.[DataUpadlosci]) END AS [AuditDaysAgo],
	   r.[PreviousNamesCount],
	   CASE WHEN r.[PreviousNameChangeYearsAgo] - (2020 - YEAR(r.DataUpadlosci)) IS NULL THEN 0
			ELSE r.[PreviousNameChangeYearsAgo] - (2020 - YEAR(r.DataUpadlosci)) END AS [PreviousNameChangeYearsAgo],
	   r.[DividendCount], r.[DividendSum],
	   CASE WHEN r.[SegmentName] IS NULL THEN 'Not listed' ELSE r.[SegmentName] END AS [SegmentName],
	   CASE WHEN r.[SegmentStockName] IS NULL THEN 'Not listed' ELSE r.[SegmentStockName] END AS [SegmentStockName]
FROM gus.liquidated g
LEFT JOIN vat.closed_liquidated v
ON g.NIP = v.NIP
LEFT JOIN register.liquidated r
ON g.NIP = r.NIP
WHERE g.NIP IS NOT NULL


-- CLOSED
UNION
SELECT g.NIP, g.REGON, g.KRS, r.EMISID, r.[DataUpadlosci], g.[CompanyName], 1 AS [Label],
	   g.[Wiek], g.[Voivodeship], g.[City], g.[LegalForm], r.[EMISLegalForm], g.[RodzajRejestru],
	   g.[FormaFinansowania], g.[FormaWlasnosci], g.[JednostkiLokalne], g.[SpecialLegalForm], g.[MainPKD],
	   CASE WHEN g.[SecondaryPKDCount] IS NULL THEN 0 ELSE g.[SecondaryPKDCount] END AS [SecondaryPKDCount],
	   g.[Ryzykowna dzia³alnosc g³ówna], g.[Ryzykowne dzia³alnosci dodatkowe], --g.[Dzialalnosc zawieszona (i niewznowiona)], 
	   CASE WHEN g.[Brak strony WWW] = 1 AND r.[WebsiteNotPresent] = 1 THEN 1 ELSE 0 END AS [NoWebsite], -- g.[Brak strony WWW], r.[WebsiteNotPresent], 
	   CASE WHEN g.[Adres email na domenie publicznej] = 1 OR r.[EmailAdressPublic] = 1 THEN 1 ELSE 0 END AS [PublicMail], -- g.[Adres email na domenie publicznej], r.[EmailAdressPublic], 
	   CASE WHEN g.[NoMailAdress] = 1 AND r.[EmailAdressNotPresent] = 1 THEN 1 ELSE 0 END AS [NoMail], -- g.[NoMailAdress], r.[EmailAdressNotPresent], 
	   CASE WHEN g.[NoFax] = 1 AND r.[FaxNotPresent] = 1 THEN 1 ELSE 0 END AS [NoFax], -- g.[NoFax], r.[FaxNotPresent],
	   g.[Podmiot zarejestrowany pod adresem wirtualnego biura],
	   g.[Adres z numerem lokalu], --r.[AddresFlat], CASE WHEN g.[Adres z numerem lokalu] = 1 AND r.[AddresFlat] = 1 THEN 1 ELSE 0 END AS [FlatAdress],
	   g.[CAAC import], g.[CAAC eksport],
	   CASE WHEN g.[ActiveLicenses] IS NULL THEN 0 ELSE g.[ActiveLicenses] END AS [ActiveLicenses],
	   CASE WHEN g.[RevertedLicenses] IS NULL THEN 0 ELSE g.[RevertedLicenses] END AS [RevertedLicenses],
	   CASE WHEN g.[ExpiredLicenses] IS NULL THEN 0 ELSE g.[ExpiredLicenses] END AS [ExpiredLicenses],
	   v.[EntityListedInVATRegistry], v.[StatusVAT], v.[VirtualAccountsPresence],
	   CASE WHEN v.[RiskyRemovalBasis] IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL
			WHEN v.[RiskyRemovalBasis] IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 'NeverRemoved'
			WHEN v.[RiskyRemovalBasis] = 0 THEN 'NaturalReason'
			WHEN v.[RiskyRemovalBasis] = 1 THEN 'PotentialyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 2 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 2.5 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 3 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 4 THEN 'LikelyFraudulent'
			END AS [RiskyRemovalBasis],
	   CASE WHEN DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL -- r.DataUpadlosci v.[CheckDate]
			WHEN DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 0
			ELSE DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) END AS [RemovalDaysAgo],
	   CASE WHEN v.[DeclaredAccountsCount] IS NOT NULL THEN v.[DeclaredAccountsCount]
			WHEN v.[DeclaredAccountsCount] IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 0
			WHEN v.[DeclaredAccountsCount] IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL END AS [DeclaredAccountsCount],
	   CASE WHEN v.[RepresentationCount] IS NOT NULL THEN v.[RepresentationCount]
			WHEN v.[RepresentationCount] IS NULL AND v.[RepresentationCount] = 1 THEN 0
			WHEN v.[RepresentationCount] IS NULL AND v.[RepresentationCount] = 0 THEN NULL END AS [RepresentationCount],
	   r.[PhoneNotPresent], r.[CompanyType], r.[NumberOfEmployees],
	   --CAST(r.[LatestMarketCapitalization] AS float),
	   CASE WHEN r.[LatestMarketCapitalization] IS NULL THEN '0'
			ELSE r.[LatestMarketCapitalization] END AS [LatestMarketCapitalization],
	   r.[ExecutivesCount], r.[OwnersCount], r.[AffiliatesCount], r.[ExternalIdsOthers], r.[MainNAICSCodes], r.[MainNAICSCount],
	   CASE WHEN r.[SecondaryNAICSCount] IS NULL THEN 0 ELSE r.[SecondaryNAICSCount] END AS [SecondaryNAICSCount],
	   r.[MainProductsNull], r.[DescriptionNull], r.[RegisteredCapitalValue],
	   CASE WHEN DATEDIFF(day, r.[AuditDate], r.[DataUpadlosci]) IS NULL THEN 0
			ELSE DATEDIFF(day, r.[AuditDate], r.[DataUpadlosci]) END AS [AuditDaysAgo],
	   r.[PreviousNamesCount],
	   CASE WHEN r.[PreviousNameChangeYearsAgo] - (2020 - YEAR(r.DataUpadlosci)) IS NULL THEN 0
			ELSE r.[PreviousNameChangeYearsAgo] - (2020 - YEAR(r.DataUpadlosci)) END AS [PreviousNameChangeYearsAgo],
	   r.[DividendCount], r.[DividendSum],
	   CASE WHEN r.[SegmentName] IS NULL THEN 'Not listed' ELSE r.[SegmentName] END AS [SegmentName],
	   CASE WHEN r.[SegmentStockName] IS NULL THEN 'Not listed' ELSE r.[SegmentStockName] END AS [SegmentStockName]
FROM gus.closed g
LEFT JOIN vat.closed_liquidated v
ON g.NIP = v.NIP
LEFT JOIN register.closed r
ON g.NIP = r.NIP
WHERE g.NIP IS NOT NULL

-- OPERATIONAL
UNION 
SELECT g.NIP, g.REGON, g.KRS, r.EMISID, r.[DataUpadlosci], g.[CompanyName], 0 AS [Label],
	   g.[Wiek], g.[Voivodeship], g.[City], g.[LegalForm], r.[EMISLegalForm], g.[RodzajRejestru],
	   g.[FormaFinansowania], g.[FormaWlasnosci], g.[JednostkiLokalne], g.[SpecialLegalForm], g.[MainPKD],
	   CASE WHEN g.[SecondaryPKDCount] IS NULL THEN 0 ELSE g.[SecondaryPKDCount] END AS [SecondaryPKDCount],
	   g.[Ryzykowna dzia³alnosc g³ówna], g.[Ryzykowne dzia³alnosci dodatkowe], --g.[Dzialalnosc zawieszona (i niewznowiona)], 
	   CASE WHEN g.[Brak strony WWW] = 1 AND r.[WebsiteNotPresent] = 1 THEN 1 ELSE 0 END AS [NoWebsite], -- g.[Brak strony WWW], r.[WebsiteNotPresent], 
	   CASE WHEN g.[Adres email na domenie publicznej] = 1 OR r.[EmailAdressPublic] = 1 THEN 1 ELSE 0 END AS [PublicMail], -- g.[Adres email na domenie publicznej], r.[EmailAdressPublic], 
	   CASE WHEN g.[NoMailAdress] = 1 AND r.[EmailAdressNotPresent] = 1 THEN 1 ELSE 0 END AS [NoMail], -- g.[NoMailAdress], r.[EmailAdressNotPresent], 
	   CASE WHEN g.[NoFax] = 1 AND r.[FaxNotPresent] = 1 THEN 1 ELSE 0 END AS [NoFax], -- g.[NoFax], r.[FaxNotPresent],
	   g.[Podmiot zarejestrowany pod adresem wirtualnego biura],
	   g.[Adres z numerem lokalu], --r.[AddresFlat], CASE WHEN g.[Adres z numerem lokalu] = 1 AND r.[AddresFlat] = 1 THEN 1 ELSE 0 END AS [FlatAdress],
	   g.[CAAC import], g.[CAAC eksport],
	   CASE WHEN g.[ActiveLicenses] IS NULL THEN 0 ELSE g.[ActiveLicenses] END AS [ActiveLicenses],
	   CASE WHEN g.[RevertedLicenses] IS NULL THEN 0 ELSE g.[RevertedLicenses] END AS [RevertedLicenses],
	   CASE WHEN g.[ExpiredLicenses] IS NULL THEN 0 ELSE g.[ExpiredLicenses] END AS [ExpiredLicenses],
	   v.[EntityListedInVATRegistry], v.[StatusVAT], v.[VirtualAccountsPresence],
	   CASE WHEN v.[RiskyRemovalBasis] IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL
			WHEN v.[RiskyRemovalBasis] IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 'NeverRemoved'
			WHEN v.[RiskyRemovalBasis] = 0 THEN 'NaturalReason'
			WHEN v.[RiskyRemovalBasis] = 1 THEN 'PotentialyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 2 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 2.5 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 3 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 4 THEN 'LikelyFraudulent'
			END AS [RiskyRemovalBasis],
	   CASE WHEN DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL -- r.DataUpadlosci v.[CheckDate]
			WHEN DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 0
			ELSE DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) END AS [RemovalDaysAgo],
	   CASE WHEN v.[DeclaredAccountsCount] IS NOT NULL THEN v.[DeclaredAccountsCount]
			WHEN v.[DeclaredAccountsCount] IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 0
			WHEN v.[DeclaredAccountsCount] IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL END AS [DeclaredAccountsCount],
	   CASE WHEN v.[RepresentationCount] IS NOT NULL THEN v.[RepresentationCount]
			WHEN v.[RepresentationCount] IS NULL AND v.[RepresentationCount] = 1 THEN 0
			WHEN v.[RepresentationCount] IS NULL AND v.[RepresentationCount] = 0 THEN NULL END AS [RepresentationCount],
	   r.[PhoneNotPresent], r.[CompanyType], r.[NumberOfEmployees],
	   --CAST(r.[LatestMarketCapitalization] AS float),
	   CASE WHEN r.[LatestMarketCapitalization] IS NULL THEN '0'
			ELSE r.[LatestMarketCapitalization] END AS [LatestMarketCapitalization],
	   r.[ExecutivesCount], r.[OwnersCount], r.[AffiliatesCount], r.[ExternalIdsOthers], r.[MainNAICSCodes], r.[MainNAICSCount],
	   CASE WHEN r.[SecondaryNAICSCount] IS NULL THEN 0 ELSE r.[SecondaryNAICSCount] END AS [SecondaryNAICSCount],
	   r.[MainProductsNull], r.[DescriptionNull], r.[RegisteredCapitalValue],
	   CASE WHEN DATEDIFF(day, r.[AuditDate], r.[DataUpadlosci]) IS NULL THEN 0
			ELSE DATEDIFF(day, r.[AuditDate], r.[DataUpadlosci]) END AS [AuditDaysAgo],
	   r.[PreviousNamesCount],
	   CASE WHEN r.[PreviousNameChangeYearsAgo] - (2020 - YEAR(r.DataUpadlosci)) IS NULL THEN 0
			ELSE r.[PreviousNameChangeYearsAgo] - (2020 - YEAR(r.DataUpadlosci)) END AS [PreviousNameChangeYearsAgo],
	   r.[DividendCount], r.[DividendSum],
	   CASE WHEN r.[SegmentName] IS NULL THEN 'Not listed' ELSE r.[SegmentName] END AS [SegmentName],
	   CASE WHEN r.[SegmentStockName] IS NULL THEN 'Not listed' ELSE r.[SegmentStockName] END AS [SegmentStockName]
FROM gus.operational g
LEFT JOIN vat.operational v
ON g.NIP = v.NIP
LEFT JOIN register.operational r
ON g.NIP = r.NIP
WHERE g.NIP IS NOT NULL

--INVESTIGATED
UNION
SELECT g.NIP, g.REGON, g.KRS, r.EMISID, r.[DataUpadlosci], g.[CompanyName], 0 AS [Label],
	   g.[Wiek], g.[Voivodeship], g.[City], g.[LegalForm], r.[EMISLegalForm], g.[RodzajRejestru],
	   g.[FormaFinansowania], g.[FormaWlasnosci], g.[JednostkiLokalne], g.[SpecialLegalForm], g.[MainPKD],
	   CASE WHEN g.[SecondaryPKDCount] IS NULL THEN 0 ELSE g.[SecondaryPKDCount] END AS [SecondaryPKDCount],
	   g.[Ryzykowna dzia³alnosc g³ówna], g.[Ryzykowne dzia³alnosci dodatkowe], --g.[Dzialalnosc zawieszona (i niewznowiona)], 
	   CASE WHEN g.[Brak strony WWW] = 1 AND r.[WebsiteNotPresent] = 1 THEN 1 ELSE 0 END AS [NoWebsite], -- g.[Brak strony WWW], r.[WebsiteNotPresent], 
	   CASE WHEN g.[Adres email na domenie publicznej] = 1 OR r.[EmailAdressPublic] = 1 THEN 1 ELSE 0 END AS [PublicMail], -- g.[Adres email na domenie publicznej], r.[EmailAdressPublic], 
	   CASE WHEN g.[NoMailAdress] = 1 AND r.[EmailAdressNotPresent] = 1 THEN 1 ELSE 0 END AS [NoMail], -- g.[NoMailAdress], r.[EmailAdressNotPresent], 
	   CASE WHEN g.[NoFax] = 1 AND r.[FaxNotPresent] = 1 THEN 1 ELSE 0 END AS [NoFax], -- g.[NoFax], r.[FaxNotPresent],
	   g.[Podmiot zarejestrowany pod adresem wirtualnego biura],
	   g.[Adres z numerem lokalu], --r.[AddresFlat], CASE WHEN g.[Adres z numerem lokalu] = 1 AND r.[AddresFlat] = 1 THEN 1 ELSE 0 END AS [FlatAdress],
	   g.[CAAC import], g.[CAAC eksport],
	   CASE WHEN g.[ActiveLicenses] IS NULL THEN 0 ELSE g.[ActiveLicenses] END AS [ActiveLicenses],
	   CASE WHEN g.[RevertedLicenses] IS NULL THEN 0 ELSE g.[RevertedLicenses] END AS [RevertedLicenses],
	   CASE WHEN g.[ExpiredLicenses] IS NULL THEN 0 ELSE g.[ExpiredLicenses] END AS [ExpiredLicenses],
	   v.[EntityListedInVATRegistry], v.[StatusVAT], v.[VirtualAccountsPresence],
	   CASE WHEN v.[RiskyRemovalBasis] IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL
			WHEN v.[RiskyRemovalBasis] IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 'NeverRemoved'
			WHEN v.[RiskyRemovalBasis] = 0 THEN 'NaturalReason'
			WHEN v.[RiskyRemovalBasis] = 1 THEN 'PotentialyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 2 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 2.5 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 3 THEN 'LikelyFraudulent'
			WHEN v.[RiskyRemovalBasis] = 4 THEN 'LikelyFraudulent'
			END AS [RiskyRemovalBasis],
	   CASE WHEN DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL -- r.DataUpadlosci v.[CheckDate]
			WHEN DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 0
			ELSE DATEDIFF(day, v.[RemovalDate], r.[DataUpadlosci]) END AS [RemovalDaysAgo],
	   CASE WHEN v.[DeclaredAccountsCount] IS NOT NULL THEN v.[DeclaredAccountsCount]
			WHEN v.[DeclaredAccountsCount] IS NULL AND v.[EntityListedInVATRegistry] = 1 THEN 0
			WHEN v.[DeclaredAccountsCount] IS NULL AND v.[EntityListedInVATRegistry] = 0 THEN NULL END AS [DeclaredAccountsCount],
	   CASE WHEN v.[RepresentationCount] IS NOT NULL THEN v.[RepresentationCount]
			WHEN v.[RepresentationCount] IS NULL AND v.[RepresentationCount] = 1 THEN 0
			WHEN v.[RepresentationCount] IS NULL AND v.[RepresentationCount] = 0 THEN NULL END AS [RepresentationCount],
	   r.[PhoneNotPresent], r.[CompanyType], r.[NumberOfEmployees],
	   CASE WHEN r.[LatestMarketCapitalization] IS NULL THEN '0'
			ELSE r.[LatestMarketCapitalization] END AS [LatestMarketCapitalization],
	   r.[ExecutivesCount], r.[OwnersCount], r.[AffiliatesCount], r.[ExternalIdsOthers], r.[MainNAICSCodes], r.[MainNAICSCount],
	   CASE WHEN r.[SecondaryNAICSCount] IS NULL THEN 0 ELSE r.[SecondaryNAICSCount] END AS [SecondaryNAICSCount],
	   r.[MainProductsNull], r.[DescriptionNull], r.[RegisteredCapitalValue],
	   CASE WHEN DATEDIFF(day, r.[AuditDate], r.[DataUpadlosci]) IS NULL THEN 0
			ELSE DATEDIFF(day, r.[AuditDate], r.[DataUpadlosci]) END AS [AuditDaysAgo],
	   r.[PreviousNamesCount],
	   CASE WHEN r.[PreviousNameChangeYearsAgo] - (2020 - YEAR(r.DataUpadlosci)) IS NULL THEN 0
			ELSE r.[PreviousNameChangeYearsAgo] - (2020 - YEAR(r.DataUpadlosci)) END AS [PreviousNameChangeYearsAgo],
	   r.[DividendCount], r.[DividendSum],
	   CASE WHEN r.[SegmentName] IS NULL THEN 'Not listed' ELSE r.[SegmentName] END AS [SegmentName],
	   CASE WHEN r.[SegmentStockName] IS NULL THEN 'Not listed' ELSE r.[SegmentStockName] END AS [SegmentStockName]
FROM gus.investigated g
LEFT JOIN vat.investigated v
ON g.NIP = v.NIP
LEFT JOIN register.investigated r
ON g.NIP = r.NIP
WHERE g.NIP IS NOT NULL

) x