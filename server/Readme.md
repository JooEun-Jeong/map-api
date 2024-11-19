# 현재 주소와 일제 강점기 주소 매칭 API

이 Flask 애플리케이션은 지리적 좌표를 기반으로 현재 및 과거 주소 정보를 조회할 수 있는 여러 API들을 제공합니다. 아래는 사용 가능한 각 라우터와 사용 방법에 대한 요약입니다.

## 요구 사항

- Python 3.8+
- Flask
- Requests
- Pandas
- GeoPandas
- SQLAlchemy
- Shapely
- dotenv

## 환경 설정

`.env` 파일에 다음 변수들이 설정되어 있는지 확인하세요:

- `KAKAO_API_KEY`: Kakao REST API 키.
- `DB_URL`: 데이터베이스에 연결하기 위한 URL.
- `ENV` : development | production

.env.sample 파일을 이용하여 .env를 작성하시면 됩니다.

## 사용 가능한 엔드포인트

Base url(Deployed in AWS): `http://cadastral-map-api.store`

### 1. `/get_address` (GET)

- **설명**: 주어진 위도와 경도를 사용하여 현재 주소를 조회합니다.
- **파라미터**:
  - `latitude` \*(필수): 위치의 위도.
  - `longitude` \*: 위치의 경도.
- **응답**: 현재 주소와 도로명 주소(가능한 경우)를 반환합니다.
- **에러 처리**: 파라미터가 없거나 유효하지 않으면 `400`을 반환하고, 주소를 찾을 수 없으면 `404`를 반환합니다.

### 2. `/get_past_address` (GET)

- **설명**: 주어진 위도와 경도를 기반으로 과거 주소 정보를 조회합니다.
- **파라미터**:
  - `latitude` \*: 위치의 위도.
  - `longitude` \*: 위치의 경도.
- **응답**: 주어진 좌표와 가장 가까운 과거 주소를 반환합니다.
- **에러 처리**: 좌표가 없거나 유효하지 않으면 `400`을 반환하고, 일치하는 데이터가 없으면 `404`를 반환합니다.

### 3. `/get_current_and_past_address` (GET)

- **설명**: 주어진 위도와 경도에 대해 현재 주소와 과거 주소를 모두 조회합니다.
- **파라미터**:
  - `latitude` \*: 위치의 위도.
  - `longitude` \*: 위치의 경도.
- **응답**: 현재 주소와 과거 주소를 모두 반환합니다.
- **에러 처리**: `/get_address`와 `/get_past_address` 라우터의 에러 처리를 사용합니다.

### 4. `/get_coordinates_from_past_address` (GET)

- **설명**: 주어진 `_1` (토지 유형)과 `_2` (지번)에 해당하는 과거 주소의 좌표를 반환합니다.
- **파라미터**:
  - `category` (`_1`) \*: 토지 유형.
  - `jibun` (`_2`) \*: 지번 번호.
- **응답**: 과거 주소의 위도와 경도를 반환합니다.
- **에러 처리**: `_2` 값이 유효하지 않으면 `400`을 반환하고, 일치하는 데이터가 없으면 `404`를 반환합니다.

### 5. `/get_current_address_from_past_address` (POST)

- **설명**: 과거 주소를 입력받아 현재 주소를 반환합니다.
- **파라미터**:
  - `past_address` \*(JSON 형식): 과거 주소 (형식: "경기도 시흥군 북면 당산리 \_1 \_2").
- **응답**: 현재 주소와 도로명 주소(가능한 경우)를 반환합니다.
- **에러 처리**: `past_address`가 없거나 잘못된 형식인 경우 `400`을 반환하고, 데이터 조회 실패 시 에러를 처리합니다.

## 애플리케이션 실행

Flask 서버를 실행하려면 다음 명령어를 사용하세요:

```sh
python app.py
```

애플리케이션은 `http://localhost:5000`에서 사용할 수 있습니다.

## 참고 사항

- 데이터베이스 연결이 `.env` 파일에 올바르게 설정되어 있는지 확인하세요.
- 애플리케이션은 Kakao API와 상호작용하므로 API 키가 유효하고 충분한 사용량이 남아있는지 확인하세요.

## 에러 코드 요약

- **400**: 잘못된 요청 (누락되거나 유효하지 않은 파라미터).
- **404**: 찾을 수 없음 (일치하는 데이터 없음).
- **500**: 내부 서버 오류 (예: 데이터베이스 쿼리 실패).

#### 프로젝트 환경 재설정

```bash
sudo apt-get update
sudo apt-get upgrade
git --version # 2.3 이상
git clone https://github.com/JooEun-Jeong/map-api.git
sudo apt install python3-pip
python3 --version # 3.8 이상
pip3 --version
sudo apt install python3.12-venv

# 가상환경 설정
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
sudo apt-get install libpq-dev

# DB 설정
sudo apt-get install postgresql postgresql-contrib postgresql-16-postgis-3
sudo -u postgres psql
  $ ALTER USER postgres PASSWORD 'yourpassword'; #이 password로 env의 DB_URL 설정할 것
sudo -u postgres psql -d dangsanli
CREATE EXTENSION postgis;
sudo -u postgres psql -d dangsanli -f ./dangsan.sql
sudo systemctl restart postgresql

# 실행
python3 app.py
```

##### 원하는 포트로 도메인 자동 리다이렉트

```bash
sudo iptables -A PREROUTING -t nat -i [이더넷 종류] -p tcp --dport 80 -j REDIRECT --to-port [app.py에 설정한 포트번호]
```

##### 백그라운드 실행

```bash
nohup python3 -u app.py &
```
