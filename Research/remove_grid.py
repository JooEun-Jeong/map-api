import cv2 as cv
import numpy as np
import os

# 이미지 불러오기
image_path = './grid_images/goyang_gangmeri_10.jpg'  # 업로드된 이미지 경로

if not os.path.exists(image_path):
    print(f"Error: File {image_path} does not exist.")
else:
    img = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: OpenCV cannot read the file {image_path}.")
    else:
        # 1. Gaussian 블러를 적용하여 이미지 노이즈 완화
        blurred_img = cv.GaussianBlur(img, (5, 5), 0)

        # 2. Canny Edge Detection을 사용하여 에지 추출
        edges = cv.Canny(blurred_img, 50, 150, apertureSize=3)

        # 3. Hough Line Transform을 사용하여 직선 검출
        lines = cv.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

        # 4. 원본 이미지에서 검출된 직선을 제거
        # 모든 직선(기울기가 일정한)을 흰색으로 덮음으로써 삭제합니다.
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # 직선의 기울기를 계산하여 모든 직선을 제거
                slope = np.abs((y2 - y1) / (x2 - x1 + 1e-6))  # 기울기 계산
                # 기울기 상관없이 검출된 모든 직선을 지움
                cv.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)  # 흰색 선으로 격자를 지웁니다

        # 5. 모폴로지 연산(침식 + 팽창)을 사용하여 작은 노이즈 제거
        kernel = np.ones((3, 3), np.uint8)
        img = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)

        # 결과 출력
        cv.imshow('Processed Image', img)
        cv.waitKey(0)
        cv.destroyAllWindows()

        # 처리된 이미지를 저장
        output_path = './remove_grid_images/processed_image3.jpg'
        cv.imwrite(output_path, img)
        print(f'Processed image saved to {output_path}')

