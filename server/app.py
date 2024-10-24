from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# Kakao REST API Key 설정 (환경 변수에서 가져오기)
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')

# 데이터베이스 엔진 설정 (환경 변수에서 DB 연결 정보 가져오기)
DB_URL = os.getenv('DB_URL')
engine = create_engine(DB_URL)

# SQL 파일 경로 설정
sql_file_path = './dangsan.sql'

# SQL 파일 읽기 및 처리
def load_sql_file(sql_file_path):
    with open(sql_file_path, 'r', encoding='utf-8') as file:
        sql_statements = file.read()
    with engine.connect() as connection:
        connection.execute(sql_statements)

# 초기 SQL 파일 로드
load_sql_file(sql_file_path)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
