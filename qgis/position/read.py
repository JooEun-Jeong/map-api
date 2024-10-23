import geopandas as gpd
from sqlalchemy import create_engine, inspect
import pandas as pd

# SQL 파일 경로
sql_file_path = './dangsan.sql'

# 데이터베이스 엔진 생성 (PostgreSQL 데이터베이스 사용)
engine = create_engine('postgresql://postgres:jje0524@localhost:5433/dangsanli')

# SQL 파일 읽기
with open(sql_file_path, 'r', encoding='UTF8') as file:
    sql_script = file.read()

# SQL 스크립트 실행
with engine.connect() as connection:
    try:
        connection.execute(sql_script)
    except Exception as e:
        print(f"Error executing script: {e}")
        exit()

# 데이터베이스 내 모든 테이블 이름 가져오기
# table_names = engine.table_names()
inspector = inspect(engine)
table_names = inspector.get_table_names()

# 각 테이블의 컬럼 정보와 데이터 확인
def get_table_info(table_name):
    print(f"\nTable: {table_name}")
    with engine.connect() as connection:
        try:
            df = gpd.read_postgis(f"SELECT * FROM {table_name}", connection)
        except ValueError as e:
            # 지오메트리 컬럼이 없으면 일반 pandas 데이터프레임으로 읽기
            df = pd.read_sql(f"SELECT * FROM {table_name}", connection)
    
    # 컬럼 정보 출력
    print("Columns:")
    for col in df.columns:
        print(f" - {col} ({df[col].dtype})")
    
    # 데이터 출력
    # print("\nSample Data:")
    # print(df.head())

    # CSV 파일로 저장
    csv_file_path = f"./{table_name}.csv"
    df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
    print(f"Data saved to {csv_file_path}")

with engine.connect() as connection:
    for table in table_names:
        get_table_info(table)
