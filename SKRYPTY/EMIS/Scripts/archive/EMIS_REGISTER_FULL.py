"""
Script used to retrieve and parse register data from EMIS API based on
getFullCompany method and list of companies IDs. Companies IDs have to be
 fist converted into EMIS IDs which is included in script.

Data are processed and exported to xlsx file and used for investigating
analysis purposes and FAIT project.
"""
import datetime as d
import pandas as pd
import re
import time as t

from keys_coded import USER_NAME, PASSWORD

from emis_full import \
    get_session_id, get_nip_name, get_isic_list, get_company_info, flatten_json,\
    parse_employees, parse_affiliates, parse_executives, parse_owners,\
    parse_dividends, parse_outstanting_shares, parse_segment,\
    parse_previous_names, parse_naics, parse_external_ids,\
    cols_drop, known_cols, \
    PUBLIC_DOMAINS, FLATTEN_COLS_DROP, OUTPUT_RENAME, FULL_REGISTER_COLS

START = t.time()

############################ USER PART ###########################
######## DEFINE METHOD, ID CLASS, INPUT NAD OUTPUT PATHS #########
METHOD = 'getFullCompany'
ID_CLASS = 'NIP'
INPUT_FILE = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\NIP_LIST.xlsx'
JSON_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API\JSONS_REGISTER\\'
XLSX_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API\\'
######################## END OF USER PART ########################

def parse_company_info(collected_jsons: dict, collected_errors: dict) -> list:
    """ Parse collected JSONs with register data and errors to list od dicts

    Parameters
    ----------
    collected_jsons : list (of dicts)
        a list of dicts storing company id (key) and collected JSON (value)
    collected_errors : dictionary
        a dictionary stoprzedring NIP (key) and error (value) collected while
        acquiring EMIS IDs and JSONS with financial data

    Returns
    -------
    result_list: list
        a list storing dictionaries with register data for companies
    collected_errors : dictionary
        a dictionary storing NIP (key) and error (value) collected while
        acquiring EMIS IDs and JSONS with financial data
    """

    result_list = []
    # Iterate over dictionary {NIP : JSON}
    for i in collected_jsons:
        #try:
            dictionary = collected_jsons[i]
            dictionary['Data rozpoczęcia współpracy'] = None
            # Drop unnecessary columns
            for k in cols_drop:
                dictionary.pop(k, None)
                
            # Parse collected JSON file
            result = flatten_json(dictionary)
            
            drop_list = []
            for key in result.keys():
                for col in FLATTEN_COLS_DROP:
                    if key.endswith(col):
                        drop_list.append(key)

            for key in drop_list:
                result.pop(key, None)
            for key, value in OUTPUT_RENAME.items():
                result[value] = result.pop(key, None)
                        # PARSING SINGLE FIELDS AND CREATION OF NEW VARIABLES
            result['AddresFlat'] = 1 if re.search(r"\/[0-9]*", result['Address']) is not None else 0
            result['EmailAdressNotPresent'] = 0 if result['EmailAddress'] is not None else 1
            result['EmailAdressPublic'] = 0
            if result['EmailAddress'] is not None:
                for i in PUBLIC_DOMAINS:
                    if i in result['EmailAddress']:
                        result['EmailAdressPublic'] = 1
                        break

            result['FaxNotPresent'] = 0 if result['Fax'] is not None else 1
            result['PhoneNotPresent'] = 0 if result['Phone'] is not None else 1
            result['WebsiteNotPresent'] = 0 if result['Website'] is not None else 1
            # PARSE AUDIT DATE
            if result['AuditDate'] is not None:
                result['AuditDateNull'] = 0
                result['AuditDateYearsAgo'] = int(d.datetime.now().year) - d.datetime.strptime(result['AuditDate'], '%Y-%m-%d').year
            else:
                result['AuditDateNull'] = 1
                result['AuditDateYearsAgo'] = 'n/a'
            # PARSE COMPANY SIZE AND SIZE YEAR
            if result['CompanyRevenueYear'] is not None:
                result['CompanyRevenue2YearsAgo'] = 1 if int(result['CompanyRevenueYear']) < d.datetime.now().year - 2 else 0
            else:
                result['CompanyRevenue2YearsAgo'] = 'n/a'
            # PARSE COUNTRY CODE
            result['CountryForeign'] = 1 if result['Country'] != 'PL' else 0
            result['DescriptionNull'] = 0 if result['Description'] is not None else 1
            # PARSE INCORPORATION YEAR
            result['IncLessThan1YearsAgo'] = 1 if int(result['IncorporationYear']) > int(d.datetime.now().year) - 1 else 0
            result['IncLessThan3YearsAgo'] = 1 if int(result['IncorporationYear']) > int(d.datetime.now().year) - 3 else 0
            result['IncLessThan5YearsAgo'] = 1 if int(result['IncorporationYear']) > int(d.datetime.now().year) - 5 else 0
            result['IncLessThan10YearsAgo'] = 1 if int(result['IncorporationYear']) > int(d.datetime.now().year) - 10 else 0
            result['IncYearsAgo'] = int(d.datetime.now().year) - int(result['IncorporationYear'])
            # PARSE PRODUCTS
            if result['MainProducts'] is None:
                result['MainProductsNull'] = 1
                result['MainProducts'] = 'n/a'
            elif isinstance(result['MainProducts'], str) and not result['MainProducts'].strip():
                result['MainProductsNull'] = 1
                result['MainProducts'] = 'n/a'
            elif isinstance(result['MainProducts'], str) and result['MainProducts'].strip():
                result['MainProductsNull'] = 0
            # PARSE MARKET CAPITALIZATION
            result['MarketCapNull'] = 1 if result['LatestMarketCapitalization'] is None else 0
            
            #Parse numbrer of employees to single field
            parse_employees(result)
            parse_executives(result)
            parse_affiliates(result)
            parse_owners(result)
            parse_dividends(result)
            parse_outstanting_shares(result)
            parse_segment(result)
            parse_previous_names(result)
            parse_naics(result)
            parse_external_ids(result)
            # Create DataFrame as row
            result_df = pd.DataFrame([result])
            # Parse nested columns to single fields
            """executives = parse_field(result_df,
                                     '_executiveNameLocal',
                                     '_executiveUserDefinedPositionLocal',
                                     'KeyExecutives')
            shareholders = parse_field(result_df,
                                       '_ownerNameLocal',
                                       '_ownershipPercentage',
                                       'Shareholders')"""

            # Concat basic output and parsed nested fields
            """result_df = pd.concat([
                result_df, executives, shareholders], axis=1)
            # Append DataFrame (table row) to list"""
            result_list.append(result_df)
            """except Exception as exc:
            # If data could not be parsed raise exception and append error
            # Append existing list of errors
            error = 'Code: {c}, Message: {m}'.format(c=type(exc).__name__, m=str(exc))
            collected_errors[i] = error"""
    print("Data successfully parsed for %s companies." % len(result_list))
    return result_list, collected_errors


def create_register_output(result_list: list, parsed_errors: dict) -> list:
    """ Create output tables in pandas DataFrames from parsedJSONs

    Parameters
    ----------
    result_list: list(of dicts)
         list of parsed dictionaries storing processed register data prepared
         for output
    parsed_errors: dictionary
        a dictionary storing NIP (key) and error (value) collected while
        acquiring EMIS IDs and JSONS with financial data and parsing JSONS

    Returns
    -------
    full_output : pd.DataFrame
        a DataFrame storing aggregated both valid nad ivalid collected register data
    output : pd.DataFrame
        a DataFrame storing only valid collected register data
    invalid_output : pd.DataFrame
    a DataFrame storing errors collected while collecting EMIS IDs / JSONS and
    parsing register data
    """

    if result_list:
        # Concat all rows into output table
        output = pd.concat(result_list, ignore_index=True, sort=False)
        output = output[FULL_REGISTER_COLS].sort_values(by=['NIP'], na_position='last')
    else:
        # Create empty DataFrame if there is no valid output
        output = pd.DataFrame(columns=FULL_REGISTER_COLS)

    # Fill null values and change type of columns
    output = output.fillna('')
    output = output.astype(str)
    output["Number of Employees"] = pd.to_numeric(output["Number of Employees"])

    if parsed_errors:
        # Create DataFrame from list of errors
        invalid_output = pd.DataFrame.from_dict(parsed_errors, orient='index').reset_index()
        invalid_output.columns = ['NIP', 'Error']
        invalid_output.sort_values(by=['NIP'], inplace=True, na_position='last')
    else:
        # Create empty DataFrame if there is no valid output
        invalid_output = pd.DataFrame(columns=['NIP', 'Error'])

    # Merge both outputs
    full_output = pd.concat([output, invalid_output.drop(['Error'], axis=1)], sort=True)
    full_output.drop_duplicates(keep='first', subset='NIP', inplace=True)
    full_output.reset_index(drop=True)
    #full_output = full_output[cols].sort_values(by=['NIP'], na_position='last')
    full_output = full_output[FULL_REGISTER_COLS].sort_values(by=['NIP'], na_position='last')
    print("Output successfully created.")
    return full_output, output, invalid_output


def export_output(output_parsed: pd.DataFrame):
    """ Split parsed register data into separated tables and
    export each into Excel sheet in defined file. Exports also EMIS_input table
    which is later used for FAIT purposes.

    Parameters
    ----------
    output_parsed : pd.DataFrame
        a DataFrame storing aggregated parsed financial data merged with invalid output

    """
    try:
        output_list = [i for i in output_parsed]
        sheet_names = ['FullOutput', 'ValidOutput', 'InvalidOutput']

        with pd.ExcelWriter(XLSX_OUTPUT_PATH +
                            'EMIS_REGISTER_' +
                            str(d.date.today()) +
                            '.xlsx') as writer:
            for sheet_name, table in zip(sheet_names, output_list):
                table.to_excel(writer, sheet_name, index=False)
            output_list[0].to_excel(writer, sheet_name='EMIS_input', columns=[
                'NIP', 'EMISID', 'Data rozpoczęcia współpracy'], index=False)
            log_df.to_excel(writer, sheet_name="LOG", index=False)
        print("Output successfully exported to declared location: " + XLSX_OUTPUT_PATH[:-2])
    except PermissionError:
        print("Close previous output file.")
    except Exception as e:
        # Raise exception and print Error if export unsuccessfull
        error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
        print(error)

############### GET OUTPUT ##################
print("Downloading and parsing register data pending. Start time: %s." % d.datetime.now())
nip_list, nips_invalid, log_df = get_nip_name(INPUT_FILE, ID_CLASS)
session_id = get_session_id(USER_NAME, PASSWORD)
nips_isics, nips_errors = get_isic_list(nip_list, session_id, ID_CLASS)
nips_jsons, nips_errors = get_company_info(nips_isics,
                                           nips_errors,
                                           session_id,
                                           JSON_OUTPUT_PATH,
                                           METHOD)
parsed_jsons, nips_errors = parse_company_info(nips_jsons, nips_errors)
register_output = create_register_output(parsed_jsons, nips_errors)
export_output(register_output)

END = t.time()
execution_time = END - START
print("Execution time: ", str(execution_time))
