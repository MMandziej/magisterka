SELECT REGON, KRS,
CASE WHEN DataUpadlosci IS NULL OR DataUpadlosci < '2016-01-01' THEN '2016-01-01'
	 WHEN DataUpadlosci > '2020-07-16' THEN '2020-07-15'
	 ELSE DataUpadlosci END AS [DataUpadlosci],
DATEADD(year, -1, CASE WHEN DataUpadlosci IS NULL OR DataUpadlosci < '2016-01-01' THEN '2016-01-01'
	 WHEN DataUpadlosci > '2020-07-16' THEN '2020-07-15'
	 ELSE DataUpadlosci END) AS [CheckDate]
FROM [modeling].[merged]
WHERE EntityListedInVATRegistry IS NULL
ORDER BY DataUpadlosci