from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = Flask(__name__)

# Kakao REST API Key
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)