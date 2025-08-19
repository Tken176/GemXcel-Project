# 🌟 GemXcel Project

> **GemXcel** là một ứng dụng học tập kết hợp **gamification** (game hóa) giúp học sinh vừa học vừa chơi.  
> Dự án do học sinh lớp 11, Trường THPT Chuyên Bến Tre phát triển với mục tiêu mang lại trải nghiệm học tập thú vị, sáng tạo và có tính tương tác cao.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Tken176/GemXcel-Project)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[![Python](https://img.shields.io/badge/python-3.8+-orange.svg)](https://python.org)
---

## 📖 Mục lục
- [Giới thiệu](#-giới-thiệu)
- [Tính năng](#-tính-năng)
- [Ảnh minh họa](#-ảnh-minh-họa)
- [Cài đặt](#-cài-đặt)
- [Cách sử dụng](#-cách-sử-dụng)
- [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
- [Đóng góp](#-đóng-góp)
- [Lộ trình phát triển](#-lộ-trình-phát-triển)
- [Giấy phép](#-giấy-phép)
- [Liên hệ](#-liên-hệ)

---

## 🚀 Giới thiệu
**GemXcel** được xây dựng bằng Python (dùng [pygame] cho phần game) và có các thành phần học tập, quiz, cửa hàng, hệ thống tài khoản và bộ sưu tập gem.  
Mục tiêu: tạo một môi trường học tập vui vẻ, tăng động lực thông qua **điểm, phần thưởng và thành tựu**.

---

## 🎮 Tính năng
| Tính năng | Mô tả |
|-----------|-------|
| 📚 **Bài học** | Cung cấp kiến thức dạng gọn nhẹ, kèm hình minh họa. |
| ❓ **Quiz** | Câu hỏi trắc nghiệm nhanh để ôn tập, có chấm điểm. |
| 💎 **Gem Collection** | Học và làm quiz để nhận gem, có thể trưng bày trong bộ sưu tập. |
| 🛒 **Shop** | Đổi gem lấy vật phẩm trang trí hoặc bonus trong game. |
| 👤 **Tài khoản** | Lưu trữ thông tin người dùng, điểm số, tiến độ học tập. |
| ⚙️ **Cài đặt** | Tùy chỉnh âm thanh, theme, và các tuỳ chọn khác. |

---

## 🖼 Ảnh minh họa
![GemXcel Logo](https://sf-static.upanhlaylink.com/img/image_2025081939b154f7796f5fd26683315cdd3dbb2a.jpg)

---

## 🔧 Cài đặt

### Yêu cầu
- Python **3.10+**
- pip

### Cách cài
# 🚀 Hướng dẫn chạy GemXcel (phiên bản exe)

## 📥 1. Tải dự án từ GitHub
1. Vào trang GitHub dự án:  
   👉 [GemXcel Project](https://github.com/username/GemXcel-Project)  
2. Nhấn **Code → Download ZIP**.  
3. Giải nén file `.zip` vừa tải về.

---

## 🛠 2. Build ra file `.exe`
1. Mở **Command Prompt (cmd)** tại thư mục vừa giải nén.  
2. Chạy lệnh sau để build:
```bash
python build.py
```
👉 Sau khi build xong, bạn sẽ có thư mục:
```bash
dist/
└── GemXcel/
    ├── GemXcel.exe   ← file chạy chính
    ├── assets/       ← chứa hình ảnh, âm thanh
    └── data/         ← chứa file lessons, quiz

▶️ 3. Chạy ứng dụng
Vào thư mục: dist/GemXcel/

Nhấp đúp vào file: GemXcel.exe

Ứng dụng sẽ chạy ngay mà không cần cài Python hoặc thư viện phụ thuộc.
```

> ⚠️ **Lưu ý
Khi copy ứng dụng sang máy khác, cần copy nguyên thư mục GemXcel/ chứ không chỉ riêng GemXcel.exe.

> ⚠️ **Lưu ý về bảo mật**: Một số phần mềm antivirus có thể báo cảnh báo với file `.exe` được tạo bởi PyInstaller. Đây là hiện tượng phổ biến với các ứng dụng Python được đóng gói. Vui lòng thêm GemXcel vào danh sách ngoại lệ của antivirus hoặc tải từ nguồn chính thức để đảm bảo an toàn.

---

## 🚀 Cách sử dụng

### 📖 Hướng dẫn cơ bản

1. **Khởi động ứng dụng**: Mở GemXcel.exe
2. **Tải tài liệu**: Nhấn "Upload" và chọn file học liệu
3. **Bắt đầu học**: Chọn bài học được tạo tự động
4. **Làm bài kiểm tra**: Hoàn thành quiz để nhận Gem
5. **Mua sắm**: Sử dụng Gem trong cửa hàng ảo

### 🎯 Mẹo sử dụng hiệu quả

- 💡 Tải lên tài liệu có cấu trúc rõ ràng để AI xử lý tốt hơn
- 💡 Hoàn thành đầy đủ các bài quiz để tối ưu hóa việc học
- 💡 Sử dụng tính năng "Hỏi AI" khi gặp khó khăn

---
## 👥 Đội ngũ phát triển
Thành viên:    

Đinh Minh Toàn 11 Lý

Hồ Tấn Phát    11 Tin 

Lý Gia Phúc    11 Lý

---


## 📩 Hỗ trợ & Liên hệ

### 🎯 Kênh hỗ trợ chính thức

- 📧 **Email hỗ trợ**: [dinhminhtoan17062009@gmail.com](https://mail.google.com/mail/u/0/#inbox?compose=GTvVlcSKkwsmPGpHDNvVJTqcJdVvLwPPtzFSmpDHQLgHNTHVzfhtsTlQNdRvdZwMjJwFxvkCXbCxD)
- 🌐 **GitHub**: [https://github.com/Tken176](https://github.com/Tken176)
- 💬 **Issues**: [GitHub Issues](https://github.com/Tken176/GemXcel-Project/issues)

### 📱 Mạng xã hội
- 🔗 **Facebook**: [Đinh Minh Toàn](https://www.facebook.com/minh.toan.708322/?locale=vi_VN)


---

## 📄 Giấy phép

Dự án này được phân phối dưới giấy phép MIT. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

## 🙏 Lời cảm ơn

Xin chân thành cảm ơn:
- Các thầy cô giáo đã hướng dẫn và hỗ trợ
- Cộng đồng open source đã đóng góp các thư viện và công cụ
- Tất cả người dùng đã tin tưởng và sử dụng sản phẩm

