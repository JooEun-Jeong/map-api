### 일제강점기 시대의 서울 영등포 당산리 연속지적원도 정보 API 제작

#### Research/  
> OpenCV를 이용하여 지적원도를 자동으로 매칭하기 위해 연구한 폴더입니다.


#### Server/
> Flask 기반의 애플리케이션으로, 지리적 좌표를 기반으로 현재 및 과거 주소 정보를 조회할 수 있는 여러 API들을 제공합니다.  
> AWS를 이용하여 API를 배포하였기 때문에, [http://cadastral-map-api.store/](http://cadastral-map-api.store/)에서 테스트해 보실 수 있습니다. (다시 오픈)

#### 시스템 구성도
```mermaid
graph LR
    User[User] -->|Inputs latitude/longitude| FlaskAPI[Flask API Server]
    FlaskAPI -->|Queries spatial data| PostGIS[PostGIS Database]
    FlaskAPI -->|Fetches location info| KakaoAPI[Kakao Map API]
    FlaskAPI -->|Processes georeferencing| QGIS[QGIS Tool]
    QGIS -->|Aligns historical maps| CadastralMaps[Cadastral Maps]
    CadastralMaps -->|Stores georeferenced data| PostGIS
    FlaskAPI -->|Returns JSON response| User

    style User fill:#b3e5fc,stroke:#0288d1,stroke-width:2px
    style FlaskAPI fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    style PostGIS fill:#e0e0e0,stroke:#424242,stroke-width:2px
    style KakaoAPI fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px
    style QGIS fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    style CadastralMaps fill:#d1c4e9,stroke:#673ab7,stroke-width:2px

```

### 프로젝트 소개
<img src="https://github.com/user-attachments/assets/2ff5f26c-29b5-4aa3-b509-4786122ccd20" width="75%" />
<img src="https://github.com/user-attachments/assets/58267194-1817-44e9-86b2-1db8371ee362" width="75%" />
<img src="https://github.com/user-attachments/assets/d185bfdd-807a-441f-bed6-b656774aa25a" width="75%" />
<img src="https://github.com/user-attachments/assets/35c34958-e05f-46f7-82fd-15a8e9582652" width="75%" />
<img src="https://github.com/user-attachments/assets/4312b217-5c41-4f20-9746-6913a82345fb" width="75%" />
<img src="https://github.com/user-attachments/assets/1b7b4a6f-a3e9-4596-873d-67534a3f1503" width="75%" />
<img src="https://github.com/user-attachments/assets/d50d3d80-2a0f-4885-ad74-d098076c0918" width="75%" />
<img src="https://github.com/user-attachments/assets/2b10dcf5-1005-43c7-afd8-d4f090161fca" width="75%" />
<img src="https://github.com/user-attachments/assets/fdb8142e-b981-4a4f-b4d6-6e345ba0a6d9" width="75%" />
<img src="https://github.com/user-attachments/assets/39c17ce4-091f-46c9-bbd3-676b9b9c89e1" width="75%" />
<img src="https://github.com/user-attachments/assets/e3c04ca4-f953-4be7-a917-1458397b3053" width="75%" />
<img src="https://github.com/user-attachments/assets/856c16dc-3525-4385-b4e5-604082ec86d9" width="75%" />
<img src="https://github.com/user-attachments/assets/d967e272-e740-4cf9-86ec-5a755142124f" width="75%" />
<img src="https://github.com/user-attachments/assets/957415c6-3d13-466b-a5f3-00261765bcd0" width="75%" />
