engine = sqlalchemy.create_engine("mssql+pyodbc://PL-WAWFTS002/" +
                                  database_name + "?driver=SQL+Server")
output[0].to_sql(table_name, engine)
output[1].to_sql(table_name + '_FAIT', engine)
