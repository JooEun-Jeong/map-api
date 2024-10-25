from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text
from shapely.geometry import MultiPolygon
import sqlparse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# Kakao REST API Key 설정 (환경 변수에서 가져오기)
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')

# 데이터베이스 엔진 설정 (환경 변수에서 DB 연결 정보 가져오기)
DB_URL = os.getenv('DB_URL')
engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)
# SQL 파일 경로 설정
sql_file_path = './dangsan.sql'

# 컬럼 존재 여부를 먼저 확인하기
def add_geometry_column_if_not_exists():
    check_column_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'dangsan' AND column_name = 'wkb_geometry';
    """
    add_column_query = """
        SELECT AddGeometryColumn('public', 'dangsan', 'wkb_geometry', 4326, 'MULTIPOLYGON', 2);
    """
    
    with engine.connect() as connection:
        result = connection.execute(text(check_column_query))
        if not result.fetchone():
            # 'wkb_geometry' 컬럼이 없을 때만 추가
            try:
                connection.execute(text(add_column_query))
            except SQLAlchemyError as e:
                print(f"Error executing statement: {add_column_query}")
                print(str(e))

# SQL 파일 읽기 및 처리
def load_sql_file(sql_file_path):
    with open(sql_file_path, 'r', encoding='utf-8') as file:
        sql_statements = file.read()

        # SQL 파일에서 여러 개의 SQL 문을 분리
        statements = sqlparse.split(sql_statements)

        is_development = os.getenv('ENV') == 'development'  # 환경 변수를 통해 개발 환경 확인

        session = Session()  # 세션 생성
        try:
            for statement in statements:
                if statement.strip():
                    try:
                        # 개발 환경에서는 특정 실행 불가능한 문장을 무시
                        if is_development and statement.strip().lower().startswith(("create", "alter", "drop", "begin", "commit")):
                            continue
                        session.execute(text(statement))  # 수정된 부분
                    except SQLAlchemyError as e:
                        session.rollback()  # 오류 발생 시 롤백
                        if is_development:
                            print(f"Error executing statement: {statement}")
                            print(str(e))
                        else:
                            # 운영 환경에서는 오류가 발생하면 중단
                            raise e
            session.commit()  # 모든 쿼리 성공 시 커밋
        except SQLAlchemyError as e:
            session.rollback()  # 트랜잭션 롤백
            raise e
        finally:
            session.close()  # 세션 종료


add_geometry_column_if_not_exists()
# 초기 SQL 파일 로드
load_sql_file(sql_file_path)

@app.route('/', methods=['GET'])
def index():
    result = """
    <html>
    <head>
        <style>
            body {
                font-family: 'Noto Sans', sans-serif;
                font-size: 14px;
            }
            .title {
                font-weight: bold;
                font-size: 16px;
            }
            .main {
                font-weight: bold;
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <div class="main">현재 주소와 일제 강점기 주소 매칭 API</div>
        <p>이 Flask 애플리케이션은 지리적 좌표를 기반으로 현재 및 과거 주소 정보를 조회할 수 있는 여러 API들을 제공합니다. <b>현재는 영등포구 일부 지역만 확인 가능합니다.</b></p>
        <br />
        <div class="title">1. /get_address (GET)</div>
        <p>
        - 설명: 주어진 위도와 경도를 사용하여 현재 주소를 조회합니다.<br>
        - 파라미터:<br>
            &emsp;- latitude *(필수): 위치의 위도.<br>
            &emsp;- longitude *(필수): 위치의 경도.<br>
        - 응답: 현재 주소와 도로명 주소(가능한 경우)를 반환합니다.<br>
        - 에러 처리: 파라미터가 없거나 유효하지 않으면 400을 반환하고, 주소를 찾을 수 없으면 404를 반환합니다.<br>
        </p>

        <div class="title">2. /get_past_address (GET)</div>
        <p>
        - 설명: 주어진 위도와 경도를 기반으로 과거 주소 정보를 조회합니다.<br>
        - 파라미터:<br>
            &emsp;- latitude *(필수): 위치의 위도.<br>
            &emsp;- longitude *(필수): 위치의 경도.<br>
        - 응답: 주어진 좌표와 가장 가까운 과거 주소를 반환합니다.<br>
        - 에러 처리: 좌표가 없거나 유효하지 않으면 400을 반환하고, 일치하는 데이터가 없으면 404를 반환합니다.<br>
        </p>

        <div class="title">3. /get_current_and_past_address (GET)</div>
        <p>
        - 설명: 주어진 위도와 경도에 대해 현재 주소와 과거 주소를 모두 조회합니다.<br>
        - 파라미터:<br>
            &emsp;- latitude *(필수): 위치의 위도.<br>
            &emsp;- longitude *(필수): 위치의 경도.<br>
        - 응답: 현재 주소와 과거 주소를 모두 반환합니다.<br>
        - 에러 처리: /get_address와 /get_past_address 라우터의 에러 처리를 사용합니다.<br>
        </p>

        <div class="title">4. /get_coordinates_from_past_address (GET)</div>
        <p>
        - 설명: 주어진 _1 (토지 유형)과 _2 (지번)에 해당하는 과거 주소의 좌표를 반환합니다.<br>
        - 파라미터:<br>
            &emsp;- category (_1) *(필수): 토지 유형.<br>
            &emsp;- jibun (_2) *(필수): 지번 번호.<br>
        - 응답: 과거 주소의 위도와 경도를 반환합니다.<br>
        - 에러 처리: _2 값이 유효하지 않으면 400을 반환하고, 일치하는 데이터가 없으면 404를 반환합니다.<br>
        </p>

        <div class="title">5. /get_current_address_from_past_address (POST)</div>
        <p>
        - 설명: 과거 주소를 입력받아 현재 주소를 반환합니다.<br>
        - 파라미터:<br>
            &emsp;- past_address *(JSON 형식, 필수): 과거 주소 (형식: "경기도 시흥군 북면 당산리 _1 _2").<br>
        - 응답: 현재 주소와 도로명 주소(가능한 경우)를 반환합니다.<br>
        - 에러 처리: past_address가 없거나 잘못된 형식인 경우 400을 반환하고, 데이터 조회 실패 시 에러를 처리합니다.<br>
        </p>
    </body>
    </html>
    """
    return result, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/get_address', methods=['GET'])
def get_address():
    # 요청 파라미터에서 위도(latitude)와 경도(longitude) 가져오기
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if not latitude or not longitude:
        return jsonify({'error': 'latitude and longitude are required'}), 400

    # Kakao 좌표-주소 변환 API 호출
    url = 'https://dapi.kakao.com/v2/local/geo/coord2address.json'
    headers = {
        'Authorization': f'KakaoAK {KAKAO_API_KEY}'
    }
    params = {
        'x': longitude,
        'y': latitude
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to get address from Kakao API'}), response.status_code

    data = response.json()
    if 'documents' not in data or len(data['documents']) == 0:
        return jsonify({'error': 'No address found for the given coordinates'}), 404

    # 주소 정보 추출
    address = data['documents'][0]['address']
    road_address = data['documents'][0].get('road_address')

    result = {
        'address': address['address_name']
    }
    if road_address:
        result['road_address'] = road_address['address_name']

    return jsonify(result)

@app.route('/get_past_address', methods=['GET'])
def get_past_address():
    # 요청 파라미터에서 위도(latitude)와 경도(longitude) 가져오기
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    table_name = 'dangsan'

    if not latitude or not longitude:
        return jsonify({'error': 'latitude and longitude are required'}), 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({'error': 'latitude and longitude must be valid numbers'}), 400

    # 특정 좌표에 해당하는 행의 _1과 _2 값을 조회
    with engine.connect() as connection:
        query = f"""
            SELECT *, ST_Distance(wkb_geometry::geography, ST_SetSRID(ST_Point({longitude}, {latitude}), 4326)::geography) AS distance
            FROM {table_name}
            ORDER BY distance
            LIMIT 1
        """
        try:
            df = gpd.read_postgis(query, connection, geom_col='wkb_geometry')
        except ValueError:
            return jsonify({'error': f'Failed to retrieve data from table {table_name}'}), 500

        if not df.empty:
            result = {
                '주소': f"경기도 시흥군 북면 당산리 {df['_1'].values[0]} {int(df['_2'].values[0])}",
            }
            return jsonify(result)
        else:
            return jsonify({'error': 'No matching row found for the given coordinates'}), 404

@app.route('/get_current_and_past_address', methods=['GET'])
def get_current_and_past_address():
    # 요청 파라미터에서 위도(latitude)와 경도(longitude) 가져오기
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if not latitude or not longitude:
        return jsonify({'error': 'latitude and longitude are required'}), 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({'error': 'latitude and longitude must be valid numbers'}), 400

    # 현재 주소 가져오기
    current_address_result = get_address()
    if current_address_result.status_code != 200:
        return current_address_result

    current_address_data = current_address_result.get_json()

    # 과거 주소 가져오기
    past_address_result = get_past_address()
    if past_address_result.status_code != 200:
        return past_address_result

    past_address_data = past_address_result.get_json()

    # 현재와 과거 주소 모두 반환
    result = {
        'current_address': current_address_data.get('address'),
        'current_road_address': current_address_data.get('road_address'),
        'past_address': past_address_data.get('주소')
    }

    return jsonify(result)


@app.route('/get_coordinates_from_past_address', methods=['GET'])
def get_coordinates_from_past_address():
    # 요청 파라미터에서 컬럼 _1에 해당하는 토지 유형과 컬럼 _2에 해당하는 지번 값 가져오기
    _1_value = request.args.get('category')
    _2_value = request.args.get('jibun')
    table_name = 'dangsan'

    if not _1_value or not _2_value:
        return jsonify({'error': '_1 and _2 values are required'}), 400

    try:
        _2_value = int(_2_value)
    except ValueError:
        return jsonify({'error': '_2 must be a valid integer'}), 400

    # _1과 _2 값에 해당하는 좌표를 조회
    with engine.connect() as connection:
        query = f"""
            SELECT wkb_geometry
            FROM {table_name}
            WHERE _1 = '{_1_value}' AND _2 = {_2_value}
            LIMIT 1
        """
        try:
            df = gpd.read_postgis(query, connection, geom_col='wkb_geometry')
        except ValueError:
            return jsonify({'error': f'Failed to retrieve data from table {table_name}'}), 500

        if not df.empty:
            # 좌표 정보 추출
            geom = df['wkb_geometry'].iloc[0]
            if isinstance(geom, MultiPolygon):
                centroid = geom.centroid
                longitude, latitude = centroid.x, centroid.y
            else:
                longitude, latitude = geom.x, geom.y
            result = {
                'latitude': latitude,
                'longitude': longitude
            }
            return jsonify(result)
        else:
            return jsonify({'error': 'No matching row found for the given _1 and _2 values'}), 404
        
@app.route('/get_current_address_from_past_address', methods=['POST'])
def get_current_address_from_past_address():
    # 요청 JSON에서 과거 주소 정보 가져오기
    data = request.get_json()
    past_address = data.get('past_address')

    if not past_address:
        return jsonify({'error': 'past_address is required'}), 400

    # 과거 주소에서 _1과 _2 값 추출
    try:
        parts = past_address.split()
        _1_value = parts[-2]
        _2_value = int(parts[-1])
    except (IndexError, ValueError):
        return jsonify({'error': 'Invalid past_address format'}), 400

    # _1과 _2 값에 해당하는 좌표를 조회
    with engine.connect() as connection:
        query = f"""
            SELECT wkb_geometry
            FROM dangsan
            WHERE _1 = '{_1_value}' AND _2 = {_2_value}
            LIMIT 1
        """
        try:
            df = gpd.read_postgis(query, connection, geom_col='wkb_geometry')
        except ValueError:
            return jsonify({'error': 'Failed to retrieve data from table dangsan'}), 500

        if not df.empty:
            # 좌표 정보 추출
            geom = df['wkb_geometry'].iloc[0]
            if isinstance(geom, MultiPolygon):
                centroid = geom.centroid
                longitude, latitude = centroid.x, centroid.y
            else:
                longitude, latitude = geom.x, geom.y

            # Kakao 좌표-주소 변환 API 호출
            url = 'https://dapi.kakao.com/v2/local/geo/coord2address.json'
            headers = {
                'Authorization': f'KakaoAK {KAKAO_API_KEY}'
            }
            params = {
                'x': longitude,
                'y': latitude
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                return jsonify({'error': 'Failed to get address from Kakao API'}), response.status_code

            data = response.json()
            if 'documents' not in data or len(data['documents']) == 0:
                return jsonify({'error': 'No address found for the given coordinates'}), 404

            # 주소 정보 추출
            address = data['documents'][0]['address']
            road_address = data['documents'][0].get('road_address')

            result = {
                'current_address': address['address_name']
            }
            if road_address:
                result['road_address'] = road_address['address_name']

            return jsonify(result)
        else:
            return jsonify({'error': 'No matching row found for the given past address'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
