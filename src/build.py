#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tự động đóng gói ứng dụng Python bằng PyInstaller
Đóng gói toàn bộ thư mục hiện tại với main.py và icon.ico
"""

import os
import sys
import subprocess
import shutil
import platform
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

def check_requirements():
    """Kiểm tra các file cần thiết"""
    required_files = ['main.py']
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Thiếu các file cần thiết: {', '.join(missing_files)}")
        return False, None
    
    # Kiểm tra icon.ico (không bắt buộc)
    icon_path = "icon.ico"
    if os.path.exists(icon_path):
        print(f"✅ Tìm thấy icon: {icon_path}")
    else:
        print("⚠️ Không tìm thấy icon.ico, sẽ đóng gói không có icon")
        icon_path = None
    
    return True, icon_path

def install_requirements():
    """Cài đặt PyInstaller + Pillow"""
    requirements = [
        ("pyinstaller", "PyInstaller"),
        ("pillow", "PIL"),
    ]
    ok = True
    for pkg, import_name in requirements:
        if not install_package(pkg, import_name):
            ok = False
    return ok

def collect_all_files():
    """Thu thập tất cả file và thư mục cần đóng gói"""
    current_dir = Path('.')
    data_files = []

    exclude_dirs = {
        '__pycache__', '.git', '.vscode', '.idea',
        'dist', 'build', '.pytest_cache',
        'venv', 'env', '.env'
    }
    exclude_extensions = {'.pyc', '.pyo', '.pyd', '.git'}

    print("📁 Đang thu thập file...")

    separator = ';' if platform.system() == 'Windows' else ':'

    for item in current_dir.rglob('*'):
        if any(excluded in item.parts for excluded in exclude_dirs):
            continue
        if item.suffix in exclude_extensions:
            continue
        if item.name in ['main.py', 'icon.ico', 'build.py']:
            continue
        if item.is_file():
            relative_path = item.relative_to(current_dir)
            parent_dir = relative_path.parent
            if parent_dir != Path('.'):
                data_files.append(f"--add-data={relative_path}{separator}{parent_dir}")
            else:
                data_files.append(f"--add-data={relative_path}{separator}.")
    
    print(f"📊 Tìm thấy {len(data_files)} file để đóng gói")
    return data_files

def build_executable(icon_path=None):
    """Thực hiện đóng gói bằng PyInstaller"""
    print("🔨 Bắt đầu quá trình đóng gói...")

    data_files = collect_all_files()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",
        "--windowed",
        "--name=GemXcel",
        "--clean",
    ]
    
    if icon_path and os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
        print(f"🖼️ Sử dụng icon: {icon_path}")
    
    cmd.extend(data_files)
    cmd.append("main.py")

    try:
        print("⚙️ Đang chạy PyInstaller...")
        print("🔧 Command:", " ".join(cmd))
        subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        print("✅ Đóng gói thành công!")
        
        if icon_path and os.path.exists(icon_path):
            dist_dir = Path("dist") / "GemXcel"
            if dist_dir.exists():
                icon_dst = dist_dir / "icon.ico"
                try:
                    shutil.copy2(icon_path, icon_dst)
                    print(f"🖼️ Đã copy icon vào dist: {icon_dst}")
                except Exception as e:
                    print(f"⚠️ Không thể copy icon: {e}")
        
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi trong quá trình đóng gói:")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False

def cleanup():
    """Dọn dẹp file tạm"""
    cleanup_dirs = ["build"]
    spec_files = list(Path('.').glob('*.spec'))
    
    for dir_name in cleanup_dirs:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"🧹 Đã xóa thư mục tạm: {dir_name}")
            except Exception as e:
                print(f"⚠️ Không thể xóa {dir_name}: {e}")
    
    for spec_file in spec_files:
        try:
            spec_file.unlink()
            print(f"🧹 Đã xóa file spec: {spec_file}")
        except Exception as e:
            print(f"⚠️ Không thể xóa {spec_file}: {e}")

def main():
    print("=" * 50)
    print("🚀 PYINSTALLER AUTO BUILD SCRIPT")
    print("=" * 50)
    print(f"🖥️ Hệ điều hành: {platform.system()}")
    print(f"🐍 Python: {sys.version}")

    has_requirements, icon_path = check_requirements()
    if not has_requirements:
        return
    
    if not install_requirements():
        return

    success = build_executable(icon_path)
    if success:
        print("\n🎉 HOÀN THÀNH!")
        print("📁 File executable đã được tạo trong thư mục 'dist/'")
        dist_dir = Path("dist") / "GemXcel"
        if dist_dir.exists():
            try:
                size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
                print(f"📏 Kích thước: {size / (1024*1024):.1f} MB")
            except:
                pass
        cleanup_choice = input("\n🧹 Bạn có muốn dọn dẹp file tạm không? (y/n): ").lower()
        if cleanup_choice in ["y", "yes", "có"]:
            cleanup()
    else:
        print("\n❌ Đóng gói thất bại!")
        print("💡 Hãy kiểm tra lại các lỗi ở trên và thử lại")

if __name__ == "__main__":
    main()
