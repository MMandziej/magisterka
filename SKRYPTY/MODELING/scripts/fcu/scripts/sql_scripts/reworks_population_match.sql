-- Population matches
SELECT * FROM [monitoring].[monitoring_production_dataset]
--WHERE pqc_timestamp ='2020-05-27 08:34:15.000'
WHERE [Population_match] = 0
ORDER BY pqc_timestamp DESC



-- Reworks vs QC_sent
SELECT a.GRID, a.week, a.pqc, a.Should_be_send_to_QC, b.Label FROM [monitoring].[production_backlog] a
LEFT JOIN [monitoring].[monitoring_production_dataset] b
ON a.GRID = b.GRID
WHERE a.Should_be_send_to_QC = 0 and b.Label = 1
ORDER BY week DESC, Label DESC