import pandas as pd
from typing import List, Dict, Any

DATATESTS_PATH = "db_stats_integration/example_db/datatests.csv"


def _read_datatests_csv(file_path:str=DATATESTS_PATH) -> pd.DataFrame:
    df = pd.read_csv(file_path, sep=';')
    df['TestTime'] = pd.to_datetime(df['TestTime'])
    return df


def get_latest_test_runs(file_path: str = DATATESTS_PATH) -> pd.DataFrame:
    df = _read_datatests_csv(file_path)
    df['IsSuccess'] = df['IsSuccess'].astype(str).str.lower() == 'true'
    latest_times = df.groupby('ID')['TestTime'].transform('max')
    latest_df = df[df['TestTime'] == latest_times]
    result = latest_df.groupby(['ID', 'TestTime'])['IsSuccess'].all().reset_index()
    return result



def get_historical_tests(target_id: str, file_path:str=DATATESTS_PATH) -> List[Dict[str, Any]]:
    df = _read_datatests_csv(file_path)
    
    filtered_df = df[df['ID'] == target_id]
    time_groups = filtered_df.groupby('TestTime')
    result = []
    
    for test_time, group in time_groups:
        tests = []
        for _, row in group.iterrows():
            column_name = row['ColumnName'] if pd.notna(row['ColumnName']) else ""
            error_message = row['ErrorMessage'] if pd.notna(row['ErrorMessage']) else ""
            
            test_info = {
                "TestName": row['DataTestName'],
                "IsGlobal": row['IsGlobal'],
                "ColumnName": column_name,
                "ErrorMessage": error_message,
                "IsSuccess": row['IsSuccess']
            }
            tests.append(test_info)
        
        tests.sort(key=lambda test: (not test["IsGlobal"], test["TestName"], test["ColumnName"]))
        all_tests_successful = all(test["IsSuccess"] for test in tests)
        
        entry = {
            "ID": target_id,
            "TestTime": test_time,
            "IsSuccess": all_tests_successful,
            "DataTests": tests
        }
        
        result.append(entry)
    
    result.sort(key=lambda x: x['TestTime'], reverse=True)
    
    return result
