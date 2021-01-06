USE i2_krs_copy
GO


CREATE FUNCTION dbo.Format_RemoveAccents( @Str varchar(8000) )
RETURNS varchar(8000)
AS
BEGIN
      /*
            EXEMPLE :
                        SELECT dbo.Format_RemoveAccents( 'ñaàeéêèioô; Œuf un œuf' )
                        ==> naaeeeeioo; OEuf un oeuf

           By Domilo
      */
      
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

      RETURN @Str
END
