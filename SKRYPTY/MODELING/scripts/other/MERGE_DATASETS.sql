USE modeling
SELECT x.*  INTO modeling.merged
FROM (
SELECT * FROM [dbo].[modeling_data]
UNION
SELECT * FROM [dbo].[modeling_data_regon])x
