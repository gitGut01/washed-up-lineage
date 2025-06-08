import pandas as pd
from typing import List, Dict, Any

DATATESTS_PATH = "db_stats_integration/example_db/datatests.csv"


def _read_datatests_csv(file_path:str=DATATESTS_PATH) -> pd.DataFrame:
    df = pd.read_csv(file_path, sep=';')
    df['TestTime'] = pd.to_datetime(df['TestTime'])
    df['IsSuccess'] = df['IsSuccess'].map({'true': True, 'false': False})
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
                "IsGlobal": True if row['IsGlobal'] == 'true' else False,
                "ColumnName": column_name,
                "ErrorMessage": error_message,
                "IsSuccess": True if row['IsSuccess'] == 'true' else False
            }
            tests.append(test_info)
        
        entry = {
            "ID": target_id,
            "TestTime": test_time,
            "DataTests": tests
        }
        
        result.append(entry)
    
    # Sort by TestTime in descending order (newest first)
    result.sort(key=lambda x: x['TestTime'], reverse=True)
    
    return result


if __name__ == "__main__":
    print(get_historical_tests("MY_WAREHOUSE.DBO.GET_EGGS"))