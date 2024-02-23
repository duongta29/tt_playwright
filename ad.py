# Đọc nội dung từ file txt
with open('cookies.txt', 'r') as file:
    cookies_content = file.read()

# Tách các dòng cookies
lines = cookies_content.strip().split('\n')

# Tạo từ điển từ các dòng cookies
cookies_dict = {}
for line in lines:
    key, value = line.strip().split(':', 1)
    cookies_dict[key.strip()] = value.strip()

# Chuyển từ điển thành chuỗi
cookies_string = '; '.join([f"{key}={value}" for key, value in cookies_dict.items()])

# In chuỗi cookies mới
print(cookies_string)
