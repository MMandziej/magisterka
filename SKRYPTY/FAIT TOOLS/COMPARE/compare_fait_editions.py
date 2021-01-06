import ctypes
import numpy as np
import sys
import pandas as pd
import time as t

from tkinter.filedialog import askopenfilename

START = t.time()

########################## USER PART #########################
######## DEFINE COLUMN NAME TO DISTINGUISH COMPANIES #########
ID_COL = 'TaxID (NIP)'
###################### END OF USER PART ######################


def define_input():
    ctypes.windll.user32.MessageBoxW(0, "Please, choose first input xlsx file.", "Choose input file.", 1)
    fist_xlsx_file = askopenfilename()
    if not fist_xlsx_file.lower().endswith('.xlsx'):
        print("Wrong input file format.")
    
    ctypes.windll.user32.MessageBoxW(0, "Please, choose second input xlsx file.", "Choose input file.", 1)
    second_xlsx_file = askopenfilename()
    if not second_xlsx_file.lower().endswith('.xlsx'):
        print("Wrong input file format.")
    
    print("File paths and names successfully imported.")
    return fist_xlsx_file, second_xlsx_file


def load_xlsx_tables(xlsx1_path: str, xlsx2_path) -> list:
    table1 = pd.read_excel(xlsx1_path)
    table2 = pd.read_excel(xlsx2_path)
    print("Files successfully loaded as pandas dataframes.")
    return table1, table2


def compare_id_list(table1: pd.DataFrame, 
                    table2: pd.DataFrame,
                    id_col_name: str) -> list:
    id_list1 = table1[ID_COL].drop_duplicates().tolist()
    id_list2 = table2[ID_COL].drop_duplicates().tolist()
    intersected_ids = list(set(id_list1).intersection(set(id_list2)))
    intersected_ids.sort()
    print("%s intersected company ids detected." % len(intersected_ids))
    return intersected_ids


def trim_output(table1: pd.DataFrame,
                table2: pd.DataFrame,
                intesecting_ids: list) -> list:

    trimmed_table1 = table1.loc[table1[ID_COL].isin(intesecting_ids)]
    trimmed_table2 = table2.loc[table2[ID_COL].isin(intesecting_ids)]

    del trimmed_table1['TURNOVER_EUR']
    del trimmed_table1['TURNOVER_CZK_ORG']

    del trimmed_table2['TURNOVER_EUR']
    del trimmed_table2['TURNOVER_CZK_ORG']

    """
    trimmed_table1.drop(['TURNOVER_EUR', 'TURNOVER_CZK_ORG'],
                        axis=1,
                        inplace=True,
                        errors='ignore')

    trimmed_table2.drop(['TURNOVER_EUR	', 'TURNOVER_CZK_ORG'],
                        axis=1,
                        inplace=True,
                        errors='ignore')
    """

    cols = list(trimmed_table1.columns)
    cols = cols[0:6] + cols[-1:] + cols[6:-1]

    trimmed_table1 = trimmed_table1[cols]
    trimmed_table2 = trimmed_table2[cols]

    trimmed_table1.sort_values(by=[ID_COL], inplace=True)
    trimmed_table2.sort_values(by=[ID_COL], inplace=True)

    trimmed_table1 = trimmed_table1.reset_index(drop=True)
    trimmed_table2 = trimmed_table2.reset_index(drop=True)
    print("Tables successfully trimmed.")
    return trimmed_table1, trimmed_table2


def merge_output(trim_table1: pd.DataFrame, trim_table2: pd.DataFrame) -> pd.DataFrame:
    trimmed_df_all = pd.concat([trim_table1, trim_table2], axis='columns', keys=['First', 'Second'])
    swaped_df_all = trimmed_df_all.swaplevel(axis='columns')[trim_table1.columns[1:]]
    swaped_df_all = swaped_df_all.fillna('')
    swaped_df_all = swaped_df_all.astype(str)
    print("Tables successfully merged and adjusted.")
    return swaped_df_all


def highlight_diff(final_df: pd.DataFrame, color='yellow'):
    attr = 'background-color: {}'.format(color)
    other = final_df.xs('First', axis='columns', level=-1)
    return pd.DataFrame(np.where(final_df.ne(other, level=0), attr, ''),
                        index=final_df.index, columns=final_df.columns)

############### GET OUTPUT ##################
filename1, filename2 = define_input()
full_df1, full_df2 = load_xlsx_tables(filename1, filename2)
common_ids = compare_id_list(full_df1, full_df2, ID_COL)
trimmed_df1, trimmed_df2 = trim_output(full_df1, full_df2, common_ids)
merged_df = merge_output(trimmed_df1, trimmed_df2)
diff_df = merged_df[(trimmed_df1 != trimmed_df2).any(1)].style.apply(highlight_diff, axis=None)
diff_df.to_excel(sys.path[0].replace('/', '\\') + "\\FAIT_Compared.xlsx")
print("Tables successfully compared and exported.")

END = t.time()
execution_time = END - START
print("Execution time: ", str(execution_time))
