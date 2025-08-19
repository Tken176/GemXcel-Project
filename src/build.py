#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tự động đóng gói ứng dụng Python bằng PyInstaller
Đóng gói toàn bộ thư mục hiện tại với main.py và icon.ico
"""
import config 
import os
import sys
import subprocess
import shutil
from pathlib import Path

os.environ["PYTHONUTF8"] = "1"
def install_package(package_name, import_name=None):
    """Cài đặt package nếu chưa có"""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        print(f"✅ {package_name} đã được cài đặt")
        return True
    except ImportError:
        print(f"📦 Đang cài đặt {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ {package_name} đã được cài đặt thành công")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Không thể cài đặt {package_name}")
            return False

def install_requirements():
    """Cài đặt tất cả các thư viện cần thiết"""
    requirements = [
        ("pyinstaller", "PyInstaller"),
        ("g4f", "g4f"),
        ("customtkinter", "customtkinter"),
    ]

    success = True
    for package, import_name in requirements:
        if not install_package(package, import_name):
            success = False
    return success

def check_requirements():
    """Kiểm tra các file cần thiết"""
    required_files = ['main.py', 'icon.ico']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Thiếu các file cần thiết: {', '.join(missing_files)}")
        return False
    
    print("✅ Tất cả file cần thiết đều có sẵn")
    return True

def install_pyinstaller():
    """Cài đặt PyInstaller nếu chưa có"""
    try:
        import PyInstaller
        print("✅ PyInstaller đã được cài đặt")
        return True
    except ImportError:
        print("📦 Đang cài đặt PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller đã được cài đặt thành công")
            return True
        except subprocess.CalledProcessError:
            print("❌ Không thể cài đặt PyInstaller")
            return False

def collect_all_files():
    """Thu thập tất cả file và thư mục cần đóng gói"""
    current_dir = Path('.')
    data_files = []
    
    # Loại trừ các thư mục và file không cần thiết
    exclude_dirs = {
        '__pycache__', 
        '.git', 
        '.vscode', 
        '.idea', 
        'dist', 
        'build',
        '.pytest_cache',
        'venv',
        'env',
        '.env'
    }
    
    exclude_extensions = {'.pyc', '.pyo', '.pyd', '.git'}
    
    print("📁 Đang thu thập file...")
    
    for item in current_dir.rglob('*'):
        # Bỏ qua thư mục loại trừ
        if any(excluded in item.parts for excluded in exclude_dirs):
            continue
        
        # Bỏ qua file có extension loại trừ
        if item.suffix in exclude_extensions:
            continue
        
        # Bỏ qua file main.py và icon.ico vì đã được xử lý riêng
        if item.name in ['main.py', 'icon.ico']:
            continue
        
        if item.is_file():
            # Tạo đường dẫn tương đối từ thư mục hiện tại
            relative_path = item.relative_to(current_dir)
            parent_dir = relative_path.parent
            
            if parent_dir != Path('.'):
                data_files.append(f"--add-data={relative_path};{parent_dir}")
            else:
                data_files.append(f"--add-data={relative_path};.")
    
    print(f"📊 Tìm thấy {len(data_files)} file để đóng gói")
    return data_files

def build_executable():
    """Thực hiện đóng gói bằng PyInstaller"""
    print("🔨 Bắt đầu quá trình đóng gói...")

    # Thu thập tất cả file
    data_files = collect_all_files()

    # Lấy đường dẫn icon từ config (đảm bảo chạy được ở bất kỳ đâu)
    icon_path = config.ICON_PATH

    # Tạo lệnh PyInstaller
    cmd = [
        'pyinstaller',
        '--onedir',
        '--windowed',
        f'--icon={icon_path}',   # dùng icon chuẩn từ config
        '--name=GemXcel',
        '--clean',
    ]

    # Thêm tất cả file data
    cmd.extend(data_files)
    cmd.append('main.py')

    try:
        print("⚙️ Đang chạy PyInstaller...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        print("✅ Đóng gói thành công!")
        dist_dir = Path('dist') / 'GemXcel'

        # Copy icon vào dist
        if dist_dir.exists():
            icon_dst = dist_dir / 'icon.ico'
            shutil.copy2(icon_path, icon_dst)
            print(f"🖼️ Đã copy icon vào dist: {icon_dst}")

        return True
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi trong quá trình đóng gói:")
        print(e.stderr)
        return False

def cleanup():
    """Dọn dẹp file tạm"""
    cleanup_dirs = ['build', '__pycache__']
    
    for dir_name in cleanup_dirs:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"🧹 Đã xóa thư mục tạm: {dir_name}")
            except Exception as e:
                print(f"⚠️ Không thể xóa {dir_name}: {e}")

def main():
    """Hàm main chính"""
    print("=" * 50)
    print("🚀 PYINSTALLER AUTO BUILD SCRIPT")
    print("=" * 50)
    
    # Kiểm tra file cần thiết
    if not check_requirements():
        return
    
    # Cài đặt PyInstaller nếu cần
    if not install_pyinstaller():
        return
    
    # Thực hiện đóng gói
    success = build_executable()
    
    if success:
        print("\n🎉 HOÀN THÀNH!")
        print("📁 File executable đã được tạo trong thư mục 'dist/'")
        
        # Hỏi có muốn dọn dẹp không
        cleanup_choice = input("\n🧹 Bạn có muốn dọn dẹp file tạm không? (y/n): ").lower()
        if cleanup_choice in ['y', 'yes', 'có']:
            cleanup()
    else:
        print("\n❌ Đóng gói thất bại!")
        print("💡 Hãy kiểm tra lại các lỗi ở trên và thử lại")

if __name__ == "__main__":
    main()
