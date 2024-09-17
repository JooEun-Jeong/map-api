# 이미지를 박스에 맞춰 자르기

from PIL import Image
import glob
import os
import re
import sys

source_folder_name = 'source_images'
cropped_folder_name = 'cropped_images'

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

for path in image_file_names:
    try:
        # Ensure path is handled correctly with Unicode encoding
        path = os.fsdecode(path)
        # .jpg 앞의 index 가져오기
        idx = re.search(r'(\d+)\.jpg$', path).group(1)
        
        image = Image.open(path)

        # Define the crop box (left, upper, right, lower) 좌표계
        crop_box = (350, 100, 1600, 1100)

        # 이미지 crop
        cropped_image = image.crop(crop_box)

        # cropped 이미지 저장
        cropped_image_path = os.path.join(cropped_folder_name, f"cropped_경기도_시흥군_북면_당산리_{idx}.jpg")
        cropped_image.save(cropped_image_path)

        print(f"Saved cropped image: {cropped_image_path}")

    except Exception as e:
        print(f"Error processing {path}: {e}")