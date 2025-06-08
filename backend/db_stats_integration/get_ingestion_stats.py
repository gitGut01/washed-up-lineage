import pandas as pd

INGESTION_PATH = "db_stats_integration/example_db/ingestion.csv"


def _read_ingestion_csv(file_path:str=INGESTION_PATH) -> pd.DataFrame:
    df = pd.read_csv(file_path, sep=';')
    df['LoadTime'] = pd.to_datetime(df['LoadTime'])
    df['IsSuccess'] = df['IsSuccess'].map({'true': True, 'false': False})
    return df


def get_latest_ingestions(file_path:str=INGESTION_PATH) -> pd.DataFrame:
    df = _read_ingestion_csv(file_path)
    return df.sort_values('LoadTime', ascending=False).drop_duplicates('ID')


def get_latest_ingestion_by_id(target_id: str, file_path:str=INGESTION_PATH) -> pd.DataFrame:
    df = _read_ingestion_csv(file_path)
    return df[df['ID'] == target_id].sort_values('LoadTime', ascending=False)

