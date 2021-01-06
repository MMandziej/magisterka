USE MMandziej
GO

CREATE TABLE PWG_finance_data
(
[NIP] [nvarchar] (255) NULL,
[Ident] [nvarchar] (255) NULL,
[Label_ID] int NULL,
[Label] [nvarchar] (255) NULL,
[Amount] [nvarchar] (255) NULL,
[Day] date NULL,
[Year] [nvarchar] (255) NULL
)

BULK INSERT [dbo].[PWG_finance_data]
FROM 'D:\Marcin Mandziej\PWG_dane\export_dataframe.txt'
WITH
(
	CODEPAGE ='ACP',
	--DATAFILETYPE ='widenative',
    FIRSTROW = 2,
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '\n',
    TABLOCK
)

SELECT * FROM dbo.PWG_finance_data
ORDER BY NIP

SELECT DISTINCT(NIP) FROM dbo.PWG_finance_data

/**** CLEANSING DATA WITH FUNCTION dbo.Format_PWG_RemoveAccents ******/

UPDATE PWG_finance_data SET [Label] = dbo.Format_PWG_RemoveAccents([Label])

