## Automatic Facebook Python

### Chức năng tự động hiện tại
- AI trả lời tin nhắn (google.generativeai)
- Tự động chấp nhận kết bạn

### Thiết lập Secrets
- `GENKEY`: Google developer API key để sử dụng Gemini
- `PASSWORD`: Để giải mã file `one-time-code.zip` và `logininfo.zip`

### Nội dung file nén
- `one-time-code.zip` chứa `one-time-code.txt`. Nôi dung là mật mã 6 chữ để giải mã các cuộc trò truyện bị mã hóa
- `logininfo.zip` chứa `logininfo.json` với nội dung:

```json
{
	"username" : "facebook_number_or_email",
	"password" : "facebook_password",
	"otp_sec" : "PYOTP_TOKEN_SECRET_CODE",
	"alt" : "0"
}
```
