import unittest
from app import app
import json

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # 테스트 클라이언트를 설정
        self.app = app.test_client()
        self.app.testing = True

    def test_get_address_valid_params(self):
        # 정상적인 위도와 경도로 요청을 테스트
        response = self.app.get('/get_address?latitude=37.5665&longitude=126.9780')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('address', data)

    def test_get_address_missing_params(self):
        # 파라미터가 없는 경우
        response = self.app.get('/get_address')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_get_past_address_valid_params(self):
        # 정상적인 위도와 경도로 과거 주소 요청을 테스트
        response = self.app.get('/get_past_address?latitude=37.5665&longitude=126.9780')
        self.assertIn(response.status_code, [200, 404])  # 데이터가 없을 수도 있으므로 404도 허용합니다.

    def test_get_past_address_missing_params(self):
        # 파라미터가 없는 경우를 테스트
        response = self.app.get('/get_past_address')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_get_current_and_past_address(self):
        # 정상적인 위도와 경도로 현재와 과거 주소를 동시에 요청을 테스트
        response = self.app.get('/get_current_and_past_address?latitude=37.5665&longitude=126.9780')
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('current_address', data)
            self.assertIn('past_address', data)

    def test_get_coordinates_from_past_address_valid_params(self):
        # 정상적인 과거 주소의 카테고리와 지번으로 좌표 요청을 테스트
        response = self.app.get('/get_coordinates_from_past_address?category=전&jibun=1')
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('latitude', data)
            self.assertIn('longitude', data)

    def test_get_current_address_from_past_address(self):
        # 정상적인 과거 주소로 현재 주소를 요청을 테스트
        response = self.app.post('/get_current_address_from_past_address', data=json.dumps({'past_address': '경기도 시흥군 북면 당산리 전 1'}), content_type='application/json')
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('current_address', data)

if __name__ == '__main__':
    unittest.main()
