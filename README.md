# Automatic Facebook Python  

**Automatic Facebook Python** là một dự án Python giúp tự động hóa các tác vụ liên quan đến Facebook, sử dụng các thư viện và API hiện đại.  

---

## 🚀 Tính năng hiện tại  

- **AI trả lời tin nhắn**: Tự động phản hồi tin nhắn Messenger bằng Google Generative AI (Gemini).  
- **Tự động chấp nhận kết bạn**: Xử lý tự động lời mời kết bạn trên Facebook.  
- **Tự động làm nhiệm vụ**: Tương tác với [traodoisub.com](https://traodoisub.com) để tự động hoàn thành nhiệm vụ.  

---

## ⚙️ Thiết lập Secrets  

Để chạy workflows, bạn cần thiết lập các secrets:  

- **`GENKEY`**: Google Developer API key để sử dụng Gemini AI.  
- **`PASSWORD`**: Mật khẩu để giải mã các tệp zip trong thư mục `secrets`.
- **`TDS_TOKEN`**: Token dùng API của `traodoisub.com`


---

### 📁 Nội dung thư mục `secrets`  

#### 1. `one-time-code.zip`  
- Chứa một tệp `.txt` với mã gồm **6 chữ cái**, dùng để giải mã các cuộc trò chuyện bị mã hóa.  

#### 2. `logininfo.zip`  
- Chứa một tệp `.json` với cấu trúc như sau:  

```json
{
	"username": "facebook_number_or_email",
	"password": "facebook_password",
	"otp_sec": "PYOTP_TOKEN_SECRET_CODE",
	"alt": "0"
}
```

#### 3. `traodoisub_fbconfig.zip`

Chứa danh sách các tài khoản Facebook để sử dụng trên traodoisub.com.


Cấu trúc mẫu:

```json
[
    {
        "username": "facebook_number_or_email_1",
        "password": "facebook_password_1",
        "otp_sec": "PYOTP_TOKEN_SECRET_CODE_1",
        "alt": "0"
    },
    {
        "username": "facebook_number_or_email_2",
        "password": "facebook_password_2",
        "otp_sec": "PYOTP_TOKEN_SECRET_CODE_2",
        "alt": "1"
    }
]
```

📌 Lưu ý

Bảo mật: Đảm bảo tất cả các tệp và thông tin trong thư mục secrets được bảo vệ nghiêm ngặt.

