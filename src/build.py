#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tự động đóng gói ứng dụng Python bằng PyInstaller
Tự động cài đặt g4f, PyInstaller và các dependencies khác
Đóng gói toàn bộ thư mục hiện tại với main.py và icon.ico
"""

import os
import sys
import subprocess
import shutil
import platform
import time
from pathlib import Path

# Thiết lập UTF-8 encoding
os.environ["PYTHONUTF8"] = "1"
if platform.system() == "Windows":
    os.environ["PYTHONIOENCODING"] = "utf-8"

def print_step(message):
    """In thông báo với format đẹp"""
    print(f"\n{'='*60}")
    print(f"🔧 {message}")
    print('='*60)

def print_success(message):
    """In thông báo thành công"""
    print(f"✅ {message}")

def print_warning(message):
    """In thông báo cảnh báo"""
    print(f"⚠️ {message}")

def print_error(message):
    """In thông báo lỗi"""
    print(f"❌ {message}")

def run_command(cmd, description="", capture_output=False, timeout=300):
    """Chạy command với xử lý lỗi tốt hơn"""
    try:
        if description:
            print(f"🔄 {description}...")
        
        if capture_output:
            result = subprocess.run(
                cmd, 
                check=True, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                timeout=timeout
            )
            return result
        else:
            result = subprocess.run(cmd, check=True, timeout=timeout)
            return result
    except subprocess.TimeoutExpired:
        print_error(f"Command timeout sau {timeout}s: {' '.join(cmd)}")
        return None
    except subprocess.CalledProcessError as e:
        print_error(f"Lỗi khi chạy command: {' '.join(cmd)}")
        if capture_output and e.stdout:
            print(f"STDOUT: {e.stdout}")
        if capture_output and e.stderr:
            print(f"STDERR: {e.stderr}")
        return None
    except Exception as e:
        print_error(f"Lỗi không mong muốn: {e}")
        return None

def upgrade_pip():
    """Nâng cấp pip lên phiên bản mới nhất"""
    print_step("Nâng cấp pip")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
    result = run_command(cmd, "Đang nâng cấp pip", capture_output=True)
    if result:
        print_success("Pip đã được nâng cấp")
        return True
    else:
        print_warning("Không thể nâng cấp pip, tiếp tục với phiên bản hiện tại")
        return False

def install_package(package_name, import_name=None, version=None):
    """Cài đặt package với xử lý lỗi tốt hơn"""
    if import_name is None:
        import_name = package_name
    
    # Kiểm tra xem package đã cài chưa
    try:
        __import__(import_name)
        print_success(f"{package_name} đã được cài đặt")
        return True
    except ImportError:
        pass
    
    # Cài đặt package
    print(f"📦 Đang cài đặt {package_name}...")
    
    install_cmd = [sys.executable, "-m", "pip", "install"]
    
    if version:
        install_cmd.append(f"{package_name}=={version}")
    else:
        install_cmd.append(package_name)
    
    # Thêm các flag để tránh lỗi
    install_cmd.extend([
        "--no-cache-dir",
        "--upgrade",
        "--user" if not hasattr(sys, 'real_prefix') and not hasattr(sys, 'base_prefix') else ""
    ])
    install_cmd = [cmd for cmd in install_cmd if cmd]  # Loại bỏ string rỗng
    
    result = run_command(install_cmd, f"Cài đặt {package_name}", capture_output=True, timeout=600)
    
    if result:
        # Kiểm tra lại xem đã cài thành công chưa
        try:
            __import__(import_name)
            print_success(f"{package_name} đã được cài đặt thành công")
            return True
        except ImportError:
            print_error(f"Cài đặt {package_name} thất bại - không thể import")
            return False
    else:
        print_error(f"Không thể cài đặt {package_name}")
        return False

def check_requirements():
    """Kiểm tra các file cần thiết"""
    print_step("Kiểm tra file cần thiết")
    
    required_files = ['main.py']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print_error(f"Thiếu các file cần thiết: {', '.join(missing_files)}")
        return False, None
    
    print_success("Tìm thấy main.py")
    
    # Kiểm tra icon.ico (không bắt buộc)
    icon_path = "icon.ico"
    if os.path.exists(icon_path):
        print_success(f"Tìm thấy icon: {icon_path}")
    else:
        print_warning("Không tìm thấy icon.ico, sẽ đóng gói không có icon")
        icon_path = None
    
    return True, icon_path

def install_requirements():
    """Cài đặt tất cả các package cần thiết"""
    print_step("Cài đặt dependencies")
    
    # Nâng cấp pip trước
    upgrade_pip()
    
    # Danh sách packages cần thiết
    requirements = [
        ("setuptools", "setuptools"),
        ("wheel", "wheel"),
        ("pyinstaller", "PyInstaller"),
        ("g4f", "g4f"),  # 👈 Thêm g4f
        ("pillow", "PIL"),
        ("pygame", "pygame"),
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("lxml", "lxml"),
        ("certifi", "certifi"),
        ("charset-normalizer", "charset_normalizer"),
        ("urllib3", "urllib3"),
        ("aiohttp", "aiohttp"),
        ("asyncio", "asyncio"),
        ("websockets", "websockets"),
        ("curl_cffi", "curl_cffi"),
        ("fake-useragent", "fake_useragent"),
        ("pycryptodome", "Crypto")
    ]
    
    failed_packages = []
    
    for pkg, import_name in requirements:
        print(f"\n📋 Xử lý package: {pkg}")
        if not install_package(pkg, import_name):
            failed_packages.append(pkg)
            # Thử cài đặt với pip install thông thường
            print(f"🔄 Thử cài đặt {pkg} với method khác...")
            cmd = [sys.executable, "-m", "pip", "install", pkg, "--no-deps"]
            result = run_command(cmd, f"Cài đặt {pkg} (no-deps)", capture_output=True)
            if not result:
                print_warning(f"Không thể cài đặt {pkg}, tiếp tục...")
    
    if failed_packages:
        print_warning(f"Một số packages không cài được: {', '.join(failed_packages)}")
        print("Tuy nhiên, script sẽ tiếp tục thực hiện...")
    
    print_success("Hoàn thành cài đặt dependencies")
    return True

def collect_all_files():
    """Thu thập tất cả file và thư mục cần đóng gói"""
    print_step("Thu thập files để đóng gói")
    
    current_dir = Path('.')
    data_files = []

    exclude_dirs = {
        '__pycache__', '.git', '.vscode', '.idea',
        'dist', 'build', '.pytest_cache',
        'venv', 'env', '.env', 'node_modules',
        '.mypy_cache', '.coverage', 'htmlcov'
    }
    exclude_extensions = {'.pyc', '.pyo', '.pyd', '.git', '.log', '.tmp'}
    exclude_files = {'build.py', 'setup.py', '.gitignore', 'requirements.txt'}

    separator = ';' if platform.system() == 'Windows' else ':'

    for item in current_dir.rglob('*'):
        # Skip excluded directories
        if any(excluded in item.parts for excluded in exclude_dirs):
            continue
        
        # Skip excluded extensions
        if item.suffix in exclude_extensions:
            continue
            
        # Skip excluded files
        if item.name in exclude_files:
            continue
            
        # Skip main.py và icon.ico (đã được PyInstaller xử lý)
        if item.name in ['main.py', 'icon.ico']:
            continue
        
        if item.is_file():
            relative_path = item.relative_to(current_dir)
            parent_dir = relative_path.parent
            
            try:
                if parent_dir != Path('.'):
                    data_files.append(f"--add-data={relative_path}{separator}{parent_dir}")
                else:
                    data_files.append(f"--add-data={relative_path}{separator}.")
            except Exception as e:
                print_warning(f"Không thể thêm file {relative_path}: {e}")
    
    print_success(f"Tìm thấy {len(data_files)} file để đóng gói")
    return data_files

def create_hidden_imports():
    """Tạo danh sách hidden imports cho g4f và các packages khác"""
    hidden_imports = [
        "g4f",
        "g4f.client",
        "g4f.models",
        "g4f.Provider",
        "g4f.providers",
        "curl_cffi",
        "curl_cffi.requests",
        "fake_useragent",
        "websockets",
        "aiohttp",
        "asyncio",
        "ssl",
        "certifi",
        "urllib3",
        "requests",
        "json",
        "base64",
        "hashlib",
        "hmac",
        "time",
        "random",
        "re",
        "os",
        "sys",
        "typing",
        "dataclasses",
        "enum",
        "abc",
        "collections",
        "Crypto",
        "Crypto.Cipher",
        "Crypto.Cipher.AES",
        "Crypto.Hash",
        "Crypto.Hash.SHA256",
        "Crypto.Random",
        "PIL",
        "PIL.Image",
        "pygame",
        "pygame.mixer",
        "pygame.display",
        "pygame.event",
        "pygame.time"
    ]
    
    return [f"--hidden-import={imp}" for imp in hidden_imports]

def build_executable(icon_path=None):
    """Thực hiện đóng gói bằng PyInstaller"""
    print_step("Bắt đầu đóng gói với PyInstaller")

    # Thu thập files
    data_files = collect_all_files()
    
    # Tạo hidden imports
    hidden_imports = create_hidden_imports()

    # Tạo command cho PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",  # Tạo thư mục thay vì file đơn
        "--windowed",  # Không hiện console (GUI app)
        "--name=GemXcel",
        "--clean",
        "--noconfirm",  # Không hỏi ghi đè
        "--distpath=dist",
        "--workpath=build",
        "--specpath=.",
    ]
    
    # Thêm icon nếu có
    if icon_path and os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
        print_success(f"Sử dụng icon: {icon_path}")
    
    # Thêm hidden imports
    cmd.extend(hidden_imports)
    
    # Thêm data files
    cmd.extend(data_files)
    
    # Thêm các collect options cho g4f
    cmd.extend([
        "--collect-all=g4f",
        "--collect-all=curl_cffi",
        "--collect-all=fake_useragent",
        "--collect-all=certifi",
        "--copy-metadata=g4f",
        "--copy-metadata=curl_cffi",
        "--copy-metadata=certifi"
    ])
    
    # File main
    cmd.append("main.py")

    try:
        print("⚙️ Đang chạy PyInstaller...")
        print(f"🔧 Command: {' '.join(cmd[:10])}... (và {len(cmd)-10} tham số khác)")
        
        # Chạy PyInstaller
        result = run_command(cmd, "Đóng gói ứng dụng", capture_output=True, timeout=1200)  # 20 phút timeout
        
        if result:
            print_success("Đóng gói thành công!")
            
            # Copy icon vào thư mục dist nếu có
            if icon_path and os.path.exists(icon_path):
                dist_dir = Path("dist") / "GemXcel"
                if dist_dir.exists():
                    icon_dst = dist_dir / "icon.ico"
                    try:
                        shutil.copy2(icon_path, icon_dst)
                        print_success(f"Đã copy icon vào dist: {icon_dst}")
                    except Exception as e:
                        print_warning(f"Không thể copy icon: {e}")
            
            # Hiển thị thông tin kích thước
            dist_dir = Path("dist") / "GemXcel"
            if dist_dir.exists():
                try:
                    size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
                    print_success(f"Kích thước ứng dụng: {size / (1024*1024):.1f} MB")
                    
                    # Liệt kê các file chính
                    main_files = list(dist_dir.glob("*.exe")) + list(dist_dir.glob("GemXcel*"))
                    for file in main_files:
                        if file.is_file():
                            print_success(f"File chính: {file.name} ({file.stat().st_size / (1024*1024):.1f} MB)")
                except Exception as e:
                    print_warning(f"Không thể tính kích thước: {e}")
            
            return True
        else:
            print_error("Đóng gói thất bại!")
            return False
            
    except Exception as e:
        print_error(f"Lỗi không mong muốn trong quá trình đóng gói: {e}")
        return False

def cleanup():
    """Dọn dẹp file tạm"""
    print_step("Dọn dẹp files tạm")
    
    cleanup_dirs = ["build"]
    spec_files = list(Path('.').glob('*.spec'))
    
    for dir_name in cleanup_dirs:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print_success(f"Đã xóa thư mục tạm: {dir_name}")
            except Exception as e:
                print_warning(f"Không thể xóa {dir_name}: {e}")
    
    for spec_file in spec_files:
        try:
            spec_file.unlink()
            print_success(f"Đã xóa file spec: {spec_file}")
        except Exception as e:
            print_warning(f"Không thể xóa {spec_file}: {e}")

def main():
    """Hàm main chính"""
    print("=" * 70)
    print("🚀 PYINSTALLER AUTO BUILD SCRIPT WITH G4F")
    print("🔧 Tự động cài đặt g4f, PyInstaller và build ứng dụng")
    print("=" * 70)
    print(f"🖥️ Hệ điều hành: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Thư mục hiện tại: {os.getcwd()}")
    
    start_time = time.time()

    try:
        # Bước 1: Kiểm tra requirements
        has_requirements, icon_path = check_requirements()
        if not has_requirements:
            print_error("Không đủ file cần thiết để tiếp tục!")
            return False
        
        # Bước 2: Cài đặt dependencies
        if not install_requirements():
            print_error("Không thể cài đặt dependencies!")
            return False

        # Bước 3: Build executable
        success = build_executable(icon_path)
        
        if success:
            # Tính thời gian hoàn thành
            elapsed_time = time.time() - start_time
            minutes, seconds = divmod(elapsed_time, 60)
            
            print("\n" + "=" * 70)
            print("🎉 HOÀN THÀNH THÀNH CÔNG!")
            print("=" * 70)
            print_success("File executable đã được tạo trong thư mục 'dist/GemXcel/'")
            print_success(f"Thời gian build: {int(minutes)}m {int(seconds)}s")
            
            # Hướng dẫn sử dụng
            dist_dir = Path("dist") / "GemXcel"
            if dist_dir.exists():
                exe_files = list(dist_dir.glob("*.exe"))
                if exe_files:
                    print_success(f"Chạy ứng dụng: {exe_files[0]}")
                else:
                    main_file = dist_dir / "GemXcel"
                    if main_file.exists():
                        print_success(f"Chạy ứng dụng: {main_file}")
            
            # Hỏi có muốn dọn dẹp không
            print("\n" + "-" * 50)
            cleanup_choice = input("🧹 Bạn có muốn dọn dẹp file tạm không? (y/n): ").lower().strip()
            if cleanup_choice in ["y", "yes", "có", "c"]:
                cleanup()
                print_success("Hoàn tất dọn dẹp!")
            
            return True
        else:
            print_error("Build thất bại!")
            print("💡 Kiểm tra lại các lỗi ở trên và thử lại")
            print("💡 Đảm bảo main.py không có lỗi syntax")
            print("💡 Thử chạy: python main.py để test trước khi build")
            return False
            
    except KeyboardInterrupt:
        print_error("\nNgười dùng hủy quá trình build")
        return False
    except Exception as e:
        print_error(f"Lỗi không mong muốn: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎊 Build script hoàn thành thành công!")
        else:
            print("\n💥 Build script thất bại!")
            sys.exit(1)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        sys.exit(1)
