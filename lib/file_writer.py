import os

def write_files(files, base_dir):
    for file in files:
        file_path = os.path.join(base_dir, file["filename"])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file["contents"])
