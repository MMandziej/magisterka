import pandas as pd
import pyodbc

from copy import deepcopy

def export_data_to_db(server: str,
                      database: str,
                      table_to_append: pd.DataFrame,
                      temp_table_name: str,
                      final_table_name: str):
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; \
                       SERVER=' + server + '; \
                       DATABASE=' + database + ';\
                       Trusted_Connection=yes;')

    cursor = cnxn.cursor()
    # read data from sql table
    data_backlog = pd.read_sql("SELECT * FROM" + final_table_name, cnxn)
    cols = list(data_backlog)
    if final_table_name == '[dbo].[reports_backlog]':
        dedup_cols = deepcopy(cols)
        dedup_cols.remove('ScoreTimestamp')
    elif final_table_name == '[dbo].[scored_cases_backlog]':
        dedup_cols = deepcopy(cols)
        dedup_cols.remove('pqc_timestamp')
    else:
        dedup_cols = cols

    data_all = pd.concat([data_backlog, table_to_append], ignore_index=True)
    data_dedup = data_all.drop_duplicates(subset=dedup_cols,
                                          keep='last',
                                          ignore_index=True)

    insert_values_list = []
    for num, a in data_dedup.iterrows():
        single_insert_list = [x for x in data_dedup.loc[num]]
        list_to_str = "', '".join(str(elem) for elem in single_insert_list)
        single_values = "('{}')".format(list_to_str)
        single_values = single_values.replace(", 'nan'", ", NULL")
        insert_values_list.append(single_values)

    insert_values = ", \n".join(str(val) for val in insert_values_list)
    all_cols = ", ".join('[' + str(header) + ']' for header in cols)
    insert_statement = "INSERT INTO {} ({}) VALUES {}".format(temp_table_name,
                                                              all_cols,
                                                              insert_values)
    try:
        cursor.execute(insert_statement)
        print("Data sucessfully exported into %s ." % temp_table_name)

    except pyodbc.ProgrammingError:
        print("Could not insert values into {} table." % temp_table_name)

    insert_temp_to_final = "INSERT INTO {} \
                SELECT * FROM {} t \
                WHERE NOT EXISTS \
                    (SELECT 1 FROM {} f \
                     WHERE t.GRID = f.GRID AND t.Score = f.Score)".format(
                        final_table_name,
                        temp_table_name,
                        final_table_name)

    try:
        cursor.execute(insert_temp_to_final)
        print("Data sucessfully exported into %s ." % final_table_name)
    except pyodbc.ProgrammingError:
        print("Could not insert values into %s table." % final_table_name)
    cursor.commit()
    cursor.close()
    cnxn.close()
    return data_dedup
