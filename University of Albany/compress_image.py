from PIL import Image
import os

input_folder = 'Image Station-re-upload'
output_folder = 'Image Station-compress--1'

# Buat folder output jika belum ada
os.makedirs(output_folder, exist_ok=True)

# Format gambar yang didukung
supported_formats = ('.jpg', '.jpeg', '.png')

# Loop semua file di folder input
for filename in os.listdir(input_folder):
    if filename.lower().endswith(supported_formats):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        try:
            img = Image.open(input_path)

            if filename.lower().endswith(('.jpg', '.jpeg')):
                img.save(output_path, optimize=True, quality=70)  # 85 = kompresi sedang, aman
            elif filename.lower().endswith('.png'):
                img.save(output_path, optimize=True)

            print(f'Compressed: {filename}')
        except Exception as e:
            print(f'Error compressing {filename}: {e}')
