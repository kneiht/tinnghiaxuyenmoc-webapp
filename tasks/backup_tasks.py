# -*- coding: utf-8 -*-
import requests
from datetime import datetime
import os
import subprocess
import zipfile


# Lấy thời gian thực từ API (Asia/Bangkok)
# def get_date_time():
#     url = "https://timeapi.io/api/time/current/zone?timeZone=Asia%2FBangkok"
#     response = requests.get(url)
#     data_time_json = response.json()
#     date_str = data_time_json['date']
#     time_str = data_time_json['time'].replace(":", "-")
#     date_str = datetime.strptime(date_str, '%m/%d/%Y').date().strftime("%Y-%m-%d")
#     return date_str + "_" + time_str

import pytz


def get_date_time():
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    vn_now = datetime.now(tz)
    date_str = vn_now.strftime("%Y-%m-%d")
    time_str = vn_now.strftime("%H-%M-%S")
    return f"{date_str}_{time_str}"


# Backup database thành file .sql và upload lên Google Drive
def backup_db(db, name, app_name):
    date_time_str = get_date_time()
    filename = f"{name}_{date_time_str}.sql"
    backup_path = os.path.join("backups", filename)

    # Backup MySQL
    cmd = (
        f"mysqldump -u minhthienk "
        f"-h minhthienk.mysql.pythonanywhere-services.com "
        f"--set-gtid-purged=OFF --no-tablespaces --column-statistics=0 "
        f"'minhthienk${db}' > {backup_path}"
    )

    print(f"Backing up {db} to {backup_path}...")
    os.system(cmd)

    # In ra kích thước file backup
    if os.path.exists(backup_path):
        file_size_bytes = os.path.getsize(backup_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        print(
            f"📊 Kích thước file backup: {file_size_mb:.2f} MB ({file_size_bytes:,} bytes)"
        )

    # Upload to Google Drive using rclone
    upload_cmd = f"/home/minhthienk/.local/bin/rclone copy {backup_path} gdrive:/BACKUPS/{app_name}/db/"
    print(f"Uploading {backup_path} to Google Drive...")
    upload_result = subprocess.run(
        upload_cmd, shell=True, capture_output=True, text=True
    )

    if upload_result.returncode == 0:
        print("✅ Upload thành công.")
        try:
            os.remove(backup_path)
            print(f"🗑️ Deleted local SQL backup: {backup_path}")
        except Exception as e:
            print(f"⚠️ Could not delete SQL file: {e}")

    else:
        print("❌ Upload thất bại:")
        print(upload_result.stderr)


def zip_and_upload_media(filename_prefix, source_folder, app_name):
    date_time_str = get_date_time()
    date_today = date_time_str.split("_")[0]  # Get today's date (YYYY-MM-DD)
    zip_filename = f"{filename_prefix}_{date_time_str}.zip"
    zip_path = os.path.join("backups", zip_filename)

    print(
        f"🔍 Zipping media files modified on {date_today} from {source_folder} into {zip_path}..."
    )

    # Create the zip file
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                filepath = os.path.join(root, file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                mod_date = mod_time.strftime("%Y-%m-%d")
                if mod_date == date_today:
                    arcname = os.path.relpath(filepath, source_folder)
                    zipf.write(filepath, arcname=arcname)

    print(f"📦 Zip created: {zip_path}")

    # In ra kích thước file zip
    if os.path.exists(zip_path):
        file_size_bytes = os.path.getsize(zip_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        print(
            f"📊 Kích thước file zip: {file_size_mb:.2f} MB ({file_size_bytes:,} bytes)"
        )

    # Upload to Google Drive
    upload_cmd = f"/home/minhthienk/.local/bin/rclone copy {zip_path} gdrive:/BACKUPS/{app_name}/media/"
    print(f"☁️ Uploading media backup to Google Drive...")
    upload_result = subprocess.run(
        upload_cmd, shell=True, capture_output=True, text=True
    )

    if upload_result.returncode == 0:
        print("✅ Media zip uploaded successfully.")

        # Delete the zip file after upload
        try:
            os.remove(zip_path)
            print(f"🗑️ Deleted local zip: {zip_path}")
        except Exception as e:
            print(f"⚠️ Could not delete zip file: {e}")

    else:
        print("❌ Failed to upload media zip:")
        print(upload_result.stderr)


def zip_and_upload_entire_folder(
    filename_prefix, source_folder, app_name, destination_folder="full_backup"
):
    """
    Zip toàn bộ nội dung của một thư mục và upload lên Google Drive.

    Args:
        filename_prefix (str): Tiền tố cho tên file zip
        source_folder (str): Đường dẫn đến thư mục cần zip
        app_name (str): Tên ứng dụng (dùng để phân loại trong Google Drive)
        destination_folder (str): Thư mục đích trên Google Drive (mặc định là "full_backup")
    """
    date_time_str = get_date_time()
    zip_filename = f"{filename_prefix}_full_{date_time_str}.zip"
    zip_path = os.path.join("backups", zip_filename)

    print(f"🔍 Đang nén toàn bộ thư mục {source_folder} vào {zip_path}...")

    # Tạo thư mục backups nếu chưa tồn tại
    os.makedirs("backups", exist_ok=True)

    # Tạo file zip
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, source_folder)
                # print(f"  ➕ Thêm file: {arcname}")
                zipf.write(filepath, arcname=arcname)

    print(f"📦 Đã tạo file zip: {zip_path}")

    # In ra kích thước file zip
    if os.path.exists(zip_path):
        file_size_bytes = os.path.getsize(zip_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        print(
            f"📊 Kích thước file zip: {file_size_mb:.2f} MB ({file_size_bytes:,} bytes)"
        )

    # Upload lên Google Drive
    upload_cmd = f"/home/minhthienk/.local/bin/rclone copy {zip_path} gdrive:/BACKUPS/{app_name}/{destination_folder}/"
    print(f"☁️ Đang upload file backup lên Google Drive...")
    upload_result = subprocess.run(
        upload_cmd, shell=True, capture_output=True, text=True
    )

    if upload_result.returncode == 0:
        print("✅ Upload thành công.")

        # Xóa file zip sau khi upload
        try:
            os.remove(zip_path)
            print(f"🗑️ Đã xóa file zip cục bộ: {zip_path}")
        except Exception as e:
            print(f"⚠️ Không thể xóa file zip: {e}")

    else:
        print("❌ Upload thất bại:")
        print(upload_result.stderr)


# Tạo thư mục backup nếu chưa có
os.makedirs("backups", exist_ok=True)

# Thực hiện backup và upload
print(get_date_time())
backup_db("tinnghiaxuyenmoc_2025_02_18", "tinnghia", "tinnghia")
backup_db("mycenter", "gen8", "gen8")

# Backup media folder
zip_and_upload_media(
    "media_backup_tinnghia",
    "/home/minhthienk/django-gen8/anh-hung-cons/media",
    "tinnghia",
)
zip_and_upload_media(
    "media_backup_gen8", "/home/minhthienk/django-gen8/mycenter/media", "gen8"
)

# Ví dụ sử dụng function zip toàn bộ folder
# Bỏ comment các dòng dưới đây để sử dụng
# zip_and_upload_entire_folder(
#     "full_backup_tinnghia",
#     "/home/minhthienk/django-gen8/anh-hung-cons",
#     "tinnghia"
# )
#
# zip_and_upload_entire_folder(
#     "full_backup_gen8",
#     "/home/minhthienk/django-gen8/mycenter",
#     "gen8"
# )
