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
inspector = inspect(engine)
table_names = inspector.get_table_names()

# 각 테이블의 컬럼 정보와 데이터 확인
def get_table_info(table_name):
    print(f"\nTable: {table_name}")
    with engine.connect() as connection:
        try:
            df = gpd.read_postgis(f"SELECT * FROM {table_name}", connection)
        except ValueError:
            # 지오메트리 컬럼이 없으면 일반 pandas 데이터프레임으로 읽기
            df = pd.read_sql(f"SELECT * FROM {table_name}", connection)
    
    # 컬럼 정보 출력
    print("Columns:")
    for col in df.columns:
        print(f" - {col} ({df[col].dtype})")

with engine.connect() as connection:
    for table in table_names:
        get_table_info(table)

# 특정 좌표에 해당하는 행의 _1과 _2 값을 출력
def get_values_from_coordinates(table_name):
    latitude = float(input("Enter latitude: "))
    longitude = float(input("Enter longitude: "))
    with engine.connect() as connection:
        query = f"SELECT *, ST_Distance(wkb_geometry::geography, ST_SetSRID(ST_Point({longitude}, {latitude}), 4326)::geography) AS distance FROM {table_name} ORDER BY distance LIMIT 1"
        df = gpd.read_postgis(query, connection, geom_col='wkb_geometry')
        if not df.empty:
            print(f"\nClosest row for coordinates ({latitude}, {longitude}):")
            print(f"_1: {df['_1'].values[0]}, _2: {int(df['_2'].values[0])}")
        else:
            print("No matching row found.")

# 사용자 입력 사용
table_name = 'dangsan'
get_values_from_coordinates(table_name)

