USE MKot
GO

/****** Object:  Table [emis].[AdvScrCompanyInfo]    Script Date: 03.03.2017 13:42:03 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [SPOLKI]
(
	[Index] int  NOT NULL ,
	[id] [int]  NULL ,
	[nip] numeric(35,0) NOT NULL ,
	[regon] numeric(20,0) NULL ,
	[krs] numeric(20,0) NULL ,
	[nazwa] [nvarchar] (max) NULL ,
	[main_pkd] [nvarchar] (20) NULL ,
	[pkd] [nvarchar] (max) NULL ,
	[miasto] [nvarchar] (50) NULL ,
	[adres] [nvarchar] (100) NULL ,
	[numer_lokalu] [nvarchar] (max) NULL ,
	[numer_nieruchomosci] [nvarchar] (20) NULL ,
	[wojew] [nvarchar] (30) NULL ,
	[powiat] [nvarchar] (50) NULL ,
	[kod_pocztowy] [nvarchar] (10) NULL ,
	[poczta] [nvarchar] (30) NULL ,
	[www] [nvarchar] (max) NULL ,
	[phone] [nvarchar] (max) NULL ,
	[email] [nvarchar] (max) NULL ,
	[forma_pr] [nvarchar] (30) NULL ,
	[data_rejestracji] [date] NULL,
	[kapital] numeric(30,0) NULL,
	[liczba_zatrud] numeric(10,0) NULL ,
	[status] [nvarchar] (40) NULL ,
	[egzekucje] [nvarchar] (max) NULL ,
	[ograniczenia] [nvarchar] (max) NULL ,
	[uprawnienia] [nvarchar] (max) NULL ,
	[zakazy] [nvarchar] (max) NULL ,
	[negatywne] [nvarchar] (max) NULL ,
	[rubryka_kurator] [nvarchar] (max) NULL ,
	[data_zakonczenia] [date] NULL,
	[last_update] [nvarchar] (30) NULL ,
	[czas][date]NOT NULL,
	CONSTRAINT PK_SPOLKI_NIP PRIMARY KEY CLUSTERED (nip)  
)


CREATE TABLE [AKTYWNOSC]
(
	[Index] int  NOT NULL ,
	[id] int  NULL ,
	[nip] numeric(35,0) NOT NULL ,
	[regon] numeric(20,0) NULL ,
	[krs] numeric(20,0) NULL ,
	[nip_aktywnosc] numeric(35,0) NULL ,
	[rola2] [nvarchar] (max) NULL ,
	[nazwa] [nvarchar] (max) NULL ,
	[ilosc] numeric(30,0)  NULL ,
	[wartosc] numeric(20,0) NULL ,
	[kapital] numeric(30,0)  NULL ,
	[start] [date] NULL ,
	[koniec] [date] NULL ,
	[czas][date]NOT NULL,
	CONSTRAINT PK_AKTYWNOSC_indeks PRIMARY KEY CLUSTERED ([Index]),
	CONSTRAINT FK_AKTYWNOSC_SPOLKI FOREIGN KEY (nip)
	REFERENCES SPOLKI (nip) 
)

CREATE TABLE [ROLA]
(
	[Index] int  NOT NULL ,
	[id] [int]  NULL ,
	[nip] numeric(35,0) NOT NULL ,
	[ident] [nvarchar] (25) NULL ,
	[imie] [nvarchar] (50) NULL ,
	[nazwisko] [nvarchar] (30) NULL ,
	[pesel] numeric(20,0) NULL ,
	[rola] [nvarchar] (max) NULL ,
	[rola2] [nvarchar] (50) NULL ,
	[start] [date] NULL ,
	[koniec] [date] NULL ,
	[czas][date]NOT NULL,
	CONSTRAINT PK_ROLA_indeks PRIMARY KEY CLUSTERED ([Index]),
	CONSTRAINT FK_ROLA_SPOLKI FOREIGN KEY (nip)
	REFERENCES SPOLKI (nip)  
)

CREATE TABLE [ROLA_H]
(
	[Index] int  NOT NULL ,
	[id] [int]  NULL ,
	[nip] numeric(35,0) NOT NULL ,
	[ident] [nvarchar] (25) NULL ,
	[imie] [nvarchar] (100) NULL ,
	[nazwisko] [nvarchar] (100) NULL ,
	[pesel] numeric(20,0) NULL ,
	[rola] [nvarchar] (max) NULL ,
	[rola2] [nvarchar] (50) NULL ,
	[start] [date] NULL ,
	[koniec] [date] NULL ,
	[czas][date]NOT NULL,
	CONSTRAINT PK_ROLA_H_indeks PRIMARY KEY CLUSTERED ([Index]),
	CONSTRAINT FK_ROLA_H_SPOLKI FOREIGN KEY (nip)
	REFERENCES SPOLKI (nip)  
)

CREATE TABLE [UDZIALOWCY]
(
	[Index] int  NOT NULL ,
	[id] int  NULL ,
	[nip] numeric(35,0) NOT NULL ,
	[regon] numeric(20,0) NULL ,
	[krs] numeric(20,0) NULL ,
	[nazwa] [nvarchar] (max) NULL ,
	[imie] [nvarchar] (max) NULL ,
	[pesel] numeric(20,0) NULL ,
	[ilosc] numeric(30,0)  NULL ,
	[wartosc] numeric(30,2)  NULL ,
	[procent] numeric(30,2) NULL ,
	[typ] [nvarchar] (30) NULL ,
	[czas][date]NOT NULL,
	CONSTRAINT PK_UDZIALOWCY_indeks PRIMARY KEY CLUSTERED ([Index]),
	CONSTRAINT FK_UDZIALOWCY_SPOLKI FOREIGN KEY (nip)
	REFERENCES SPOLKI (nip)  
)

CREATE TABLE [UOKIK]
(
	[Index] int  NOT NULL ,
	[id] int  NULL ,
	[nip] numeric(35,0) NOT NULL ,
	[numer] [nvarchar] (20) NULL ,
	[sygnatura] [nvarchar] (50) NULL ,
	[data] [date] NULL ,
	[uczestnicy] [nvarchar] (max) NULL ,
	[kara] [nvarchar] (10) NULL ,
	[odwolanie] [nvarchar] (10) NULL ,
	[czas][date]NOT NULL,
	CONSTRAINT PK_UOKIK_indeks PRIMARY KEY CLUSTERED ([Index]),
	CONSTRAINT FK_UOKIK_SPOLKI FOREIGN KEY (nip) REFERENCES SPOLKI (nip),
	
)

	CREATE TABLE [ZALEGLOSCI]
(
	[Index] int  NOT NULL ,
	[nip] numeric(35,0) NOT NULL ,
	[zaleglosci_charakter] [nvarchar] (max) NULL ,
	[zaleglosci_organ] [nvarchar] (250) NULL ,
	[zaleglosci_wysokosc] [nvarchar] (50) NULL ,
	[zaleglosci_zakonczenie] [nvarchar] (max) NULL ,
	[czas][date]NOT NULL,
	CONSTRAINT PK_ZALEGLOSCI_indeks PRIMARY KEY CLUSTERED ([Index]),
	CONSTRAINT FK_ZALEGLOSCI_SPOLKI FOREIGN KEY (nip)
	REFERENCES SPOLKI (nip) 

)

CREATE TABLE [ZALEZNE]
(
	[Index] int  NOT NULL ,
	[id] [int]  NULL ,
	[nazwa] [nvarchar] (max) NULL ,
	[nip] numeric(35,0) NOT NULL ,
	[regon] numeric(30,0) NULL ,
	[krs] numeric(30,0) NULL ,
	[ilosc] numeric(30,0) NULL ,
	[wartosc] numeric(30,0) NULL ,
	[kapital]numeric(30,0)NULL ,
	[procent] numeric(30,2) NULL ,
	[czas][date]NOT NULL
 	CONSTRAINT PK_ZALEZNE_indeks PRIMARY KEY CLUSTERED ([Index]),
	CONSTRAINT FK_ZALEZNE_SPOLKI FOREIGN KEY (nip)
	REFERENCES SPOLKI (nip)  
)

"""
CREATE SCHEMA hist

SELECT * INTO [hist].[SPOLKI] FROM [dbo].[SPOLKI] 
TRUNCATE TABLE [hist].[SPOLKI]

SELECT * INTO [hist].[AKTYWNOSC] FROM [dbo].[AKTYWNOSC] 
TRUNCATE TABLE [hist].[AKTYWNOSC]

SELECT * INTO [hist].[ROLA] FROM [dbo].[ROLA] 
TRUNCATE TABLE [hist].[ROLA]

SELECT * INTO [hist].[ROLA_H] FROM [dbo].[ROLA_H] 
TRUNCATE TABLE [hist].[ROLA_H]

SELECT * INTO [hist].[UDZIALOWCY] FROM [dbo].[UDZIALOWCY] 
TRUNCATE TABLE [hist].[UDZIALOWCY]

SELECT * INTO [hist].[UOKIK] FROM [dbo].[UOKIK] 
TRUNCATE TABLE [hist].[UOKIK]


SELECT * INTO [hist].[ZALEGLOSCI] FROM [dbo].[ZALEGLOSCI] 
TRUNCATE TABLE [hist].[ZALEGLOSCI]

SELECT * INTO [hist].[ZALEZNE] FROM [dbo].[ZALEZNE] 
TRUNCATE TABLE [hist].[ZALEZNE]
"""

"""
DROP TABLE [hist].[AKTYWNOSC]
DROP TABLE [hist].[ROLA]
DROP TABLE [hist].[ROLA_H]
DROP TABLE [hist].[UDZIALOWCY]
DROP TABLE [hist].[UOKIK]
DROP TABLE [hist].[ZALEGLOSCI]
DROP TABLE [hist].[ZALEZNE]
DROP TABLE [hist].[SPOLKI]
"""

"""
DROP TABLE [AKTYWNOSC]
DROP TABLE [ROLA]
DROP TABLE [ROLA_H]
DROP TABLE [UDZIALOWCY]
DROP TABLE [UOKIK]
DROP TABLE [ZALEGLOSCI]
DROP TABLE [ZALEZNE]
DROP TABLE [SPOLKI]
"""


"""
SELECT column_name, data_type, character_maximum_length    
FROM information_schema.columns  
WHERE table_name = 'SPOLKI'

SELECT column_name, data_type, character_maximum_length    
FROM information_schema.columns  
WHERE table_name = 'AKTYWNOSC'

SELECT column_name, data_type, character_maximum_length    
FROM information_schema.columns  
WHERE table_name = 'ROLA'

SELECT column_name, data_type, character_maximum_length    
FROM information_schema.columns  
WHERE table_name = 'ROLA_H'

SELECT column_name, data_type, character_maximum_length    
FROM information_schema.columns  
WHERE table_name = 'UDZIALOWCY'

SELECT column_name, data_type, character_maximum_length    
FROM information_schema.columns  
WHERE table_name = 'UOKIK'

SELECT column_name, data_type, character_maximum_length    
FROM information_schema.columns  
WHERE table_name = 'ZALEGLOSCI'

SELECT column_name, data_type, character_maximum_length    
FROM information_schema.columns  
WHERE table_name = 'ZALEZNE'
""""
