
# **Tài liệu hướng dẫn Workflow: Chạy AI Chat trên tài khoản Messenger**

Hỗ trợ giao diện Facebook hiện tại: [Xem giao diện](https://huskydg.github.io/automatic_fb/static_page/static_page_www_facebook_com_messages_e2ee_t_29050446974570740.html)

## **Tên Workflow**  
`Run AI Chat on Messenger Account`

---

## **1. Sự kiện kích hoạt Workflow**

Workflow được kích hoạt bởi hai sự kiện chính:

- **Lịch định kỳ (`schedule`)**

  Workflow sẽ chạy mỗi 4 giờ vào các thời điểm 0h, 4h, 8h, 12h, 16h, 20h theo định dạng cron:
  ```cron
  0 0,4,8,12,16,20 * * *
  ```

- **Thủ công (`workflow_dispatch`)**

  Cho phép người dùng thiết lập chạy workflows các thông số nhập tùy chọn.

---

## **2. Thông số nhập (Inputs)**

- `username`: Nhập tài khoản Facebook (email hoặc số điện thoại). **Bắt buộc**.
- `password`: Nhập mật khẩu Facebook. Không bắt buộc.
- `otp_secret`: Nhập mã OTP Secret từ App Authenticator. Mã này là cần thiết để hoàn tất bước xác thực đăng nhập 2 yếu tố (Không bắt buộc)
- `onetimecode`: Nhập mã một lần để giải mã tin nhắn đầu cuối (Mã hoá End-to-End Encryption E2EE). Nếu không có thì có thể không chat được với các cuộc trò chuyện đã mã hóa đầu cuối. Không bắt buộc.
- `alt_account`: Nhập chỉ số tài khoản nếu Facebook có tài khoản phụ (0 là tài khoản chính). Giá trị mặc định là `0`. Không bắt buộc.
- `cookies_text`: Nhập cookies nếu có. Không bắt buộc.
- `ai_prompt`: Nhập lời giới thiệu cho AI (tham khảo file `setup/introduction.txt`). Không bắt buộc.
- `work_jobs`: Nhập các tác vụ cần thực hiện, ví dụ: `aichat=normal,friends`. Mặc định là `aichat=normal,friends`.
  + `aichat=normal` - Chatbot bình thường
  + `aichat=devmode` - Chatbot ở chế độ debug. Chế độ này có thể tạo các nội dung không lành mạnh, ví dụ ảnh khiêu dâm.
  + `friends` - Tự động chấp nhận kết bạn
  + `aichat_nobye` - Không cho phép chatbot tự dừng cuộc trò chuyện
  + `aichat_resetat=<regex pattern>` - Nếu tin nhắn nhận được khớp với `<regex pattern>`, thì bot sẽ xóa bộ nhớ cuộc trò chuyện. Ví dụ lệnh reset: `aichat_resetat=^\(\s*\)\/reset\(\s*\)\$`
  + `aichat_resetmsg=<msg>` - Tin nhắn mà bot sẽ gửi khi xóa bộ nhớ cuộc trò chuyện
  + `aichat_stopat=<regex pattern>` - Nếu tin nhắn nhận được khớp với `<regex pattern>`, thì bot sẽ dừng cuộc trò chuyện. Ví dụ lệnh mute: `aichat_stopat=^\(\s*\)\/mute\(\s*\)\$`
  + `aichat_stopmsg=<msg>` - Tin nhắn mà bot sẽ gửi khi dừng cuộc trò chuyện
  + `aichat_startat=<regex pattern>` - Nếu tin nhắn nhận được khớp với `<regex pattern>`, thì bot sẽ tiếp tục cuộc trò chuyện. Ví dụ lệnh unmute: `aichat_stopat=^\(\s*\)\/unmute\(\s*\)\$`
  + `aichat_startmsg=<msg>` - Tin nhắn mà bot sẽ gửi khi bắt đầu cuộc trò chuyện
  + Nếu bạn chỉ muốn áp dụng `aichat_*at` cho một số ID cụ thể. Hãy sử dụng `aichat_<name>_*at=<regex pattern>, aichat_<name>_*msg=<msg>, aichat_<fbid>_rules=<name>`
- `check_only`: Nếu đặt là `true`, chỉ kiểm tra đăng nhập và lưu cấu hình cookies, không chạy AI Chat. Mặc định là `false`.

---

## **3. Các bước công việc (Jobs)**

- Lần đầu tiên, bạn cần chạy workflow dispatch `Run AI Chat on Messenger Account` để đăng nhập Facebook và sao lưu cookies vào nhánh `caches/schedule`.
- Cookies và các file liên quan sẽ được mã hóa bằng mật khẩu của bạn (`PASSWORD` secret) để không ai có thể truy cập tài khoản Facebook của bạn thông qua việc sử dụng cookies.
- Khi thay đổi tài khoản Facebook, hãy xóa nhánh `cache/schedule` rồi chạy lại workflow `Run AI Chat on Messenger Account`

### **Job: run-aichat**

- **Chạy trên môi trường:** `windows-latest`
- **Thời gian chờ tối đa:** `300 phút`
- **Biến môi trường quan trọng:**  
  - `SCPDIR`: Thư mục lưu trữ cục bộ trong workflow.
  - `COOKIESFILE`: Đường dẫn file cookies.
  - `GITHUB_TOKEN`: Token GitHub.
  - `STORAGE_BRANCE`: Nhánh lưu trữ thông tin đăng nhập Facebook (`caches/schedule`)

---

## **4. Các bước thực hiện (Steps)**

### **1. Checkout repository**
Sử dụng GitHub Action `actions/checkout@v3` để lấy mã nguồn từ repository.

### **2. Thiết lập Python**
Sử dụng `actions/setup-python@v4` để cài đặt Python 3.9.

### **3. Cài đặt thư viện phụ thuộc**
Chạy lệnh:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### **4. Kiểm tra Selenium**
Chạy script kiểm tra:
```bash
python test_selenium.py
```

### **5. Chờ các workflow khác hoàn tất**
Nếu workflow được kích hoạt bởi `schedule`, chạy script:
```bash
python wait_for_other_runs.py
```

### **6. Đăng nhập tài khoản Facebook**
Chạy script đăng nhập:
```bash
python fb_getcookies_test.py
```

### **7. Chạy AI Chat trên tài khoản Messenger**
Nếu không phải chỉ kiểm tra login (`check_only`), chạy script:
```bash
python aichat_timeout.py
```

---

## **5. Ghi chú**

- Cần sử dụng biến môi trường `GITHUB_SECRET` để lưu trữ thông tin nhạy cảm như `PASSWORD` và `GENKEY`.  
- Đảm bảo cấu hình đầy đủ và kiểm tra repository trước khi triển khai workflow.