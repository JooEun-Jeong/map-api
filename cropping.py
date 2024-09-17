# 이미지를 박스에 맞춰 자르기

from PIL import Image
import glob
import os
import re
import sys
import cv2
import numpy as np

source_folder_name = 'source_images'
cropped_folder_name = 'auto_cropped_images'

# enable UTF-8 support
if sys.platform == 'win32':
    os.system('chcp 65001')

# 폴더 없으면 만들기
if not os.path.exists(cropped_folder_name):
    os.makedirs(cropped_folder_name)

# 폴더 내에 있는 이미지들 불러오기
image_files = glob.glob(os.path.join(source_folder_name, '*.[pjgPJG][npNP]*'))

# 파일 이름 추출
image_file_names = [os.path.join(source_folder_name, os.path.basename(image)) for image in image_files]

def load_image_unicode(file_path):
    with open(file_path, 'rb') as f:
        img_array = np.frombuffer(f.read(), np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)

def crop_to_rectangle(image_cv):
    # Check if the image has multiple channels (BGR) or is already grayscale
    if len(image_cv.shape) == 3:
        # Convert to grayscale only if the image has multiple channels
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_cv
    
    # Apply GaussianBlur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection: Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # 윤곽선 찾기
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 가장 큰 사각형 찾기
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # 이미지 자르기
    cropped_image_cv = image_cv[y:y+h, x:x+w]
    
    return cropped_image_cv

for path in image_file_names:
    try:
        # Ensure path is handled correctly with Unicode encoding
        path = os.fsdecode(path)

        # .jpg 앞의 index 가져오기
        idx = re.search(r'(\d+)\.jpg$', path).group(1)
        
        image = load_image_unicode(path)

        # 이미지 crop
        cropped_image = crop_to_rectangle(image)

        # cropped 이미지 저장
        cropped_image_path = os.path.join(cropped_folder_name, f"auto_cropped_image_{idx}.jpg")

        # Ensure that the cropped image has valid dimensions
        if cropped_image.size > 0:
            cv2.imwrite(cropped_image_path, cropped_image)
            print(f"Saved cropped image: {cropped_image_path}")
        else:
            print(f"Failed to crop image: {path}")

    except Exception as e:
        print(f"Error processing {path}: {e}")