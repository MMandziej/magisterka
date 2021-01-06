USE MMandziej
GO


CREATE FUNCTION dbo.Format_PWG_RemoveAccents( @Str varchar(8000) )
RETURNS varchar(8000)
AS
BEGIN
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'ą', 'a' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Ą', 'A' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'ć', 'c' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Ć', 'C' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'ę', 'e' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Ę', 'E' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'ł', 'l' )

      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Ł', 'L' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'ń', 'n' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Ń', 'N' )

      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'ó', 'o' )


      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Ó', 'O' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'ś', 's' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Ś', 'S' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'ż', 'z' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Ż', 'Z' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'ź', 'z' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Ź', 'Z' )

	  --Specific for financial data from PWG
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Ls', 'S' )
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'A…', 'a' )
      SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'LL', 'z' )
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'L›', 's' )
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'A‡', 'c' )
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'L‚', 'l' )
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'L„', 'n' )
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'A™', 'e' )
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, '"b.', 'b.' )
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Alt', 'ot' )
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'Alw', 'ow' )
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'All', 'ol' )
	  SET @Str = Replace( @Str COLLATE Latin1_General_CS_AI, 'krAltkoterminowe', 'krotkoterminowe' )
	  RETURN @Str
END