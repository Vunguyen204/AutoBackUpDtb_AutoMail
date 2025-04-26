import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import shutil
import schedule
import time

load_dotenv('mail.env')

folder_dtb = 'D:\Hoc\TuDongHoaQuyTrinh\database'
folder_backUp = 'D:\Hoc\TuDongHoaQuyTrinh\backUpDatabase'

sender_mail = os.getenv("sender_mail")
app_password = os.getenv("app_password")
receiver_email = os.getenv("receiver_mail")
    
def send_email(sender, receiver, subject, body, password):
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    
    message.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())
        print(f"Email đã được gửi đến {receiver}")
        server.quit()
    except Exception as e:
        print(f'Email gửi thất bại: {e}')
        
def backUp_database():
    try:
        if not os.path.exists(folder_dtb):
            raise FileNotFoundError(f"Không tìm thấy file database: {folder_dtb}")
        
        os.makedirs(folder_backUp, exist_ok=True) #Tạo thư mục nếu chưa tồn tại
        
        backUp_list = []
        
        for filename in os.listdir(folder_dtb): 
            if filename.endswith('.sql') or filename.endswith('.sqlite3'):  # Kiểm tra và backup file .sql hoặc .sqlite3
                file_goc = os.path.join(folder_dtb, filename)
                file_saoLuu = os.path.join(folder_backUp, filename)
                shutil.copy(file_goc, file_saoLuu)
                print(f"Backup thành công: {file_saoLuu}")
                backUp_list.append(filename)

        if backUp_list:
            files_list = "\n".join(backUp_list)
            send_email(
                sender_mail,
                receiver_email,
                subject="Thông báo! Backup Database Thành Công",
                body=f"Các file database sau đã được sao lưu thành công vào {folder_backUp}:\n{files_list}",
                password=app_password
            )
        else:
            send_email(
                sender_mail,
                receiver_email,
                subject="Thông báo! Không tìm thấy file Database để Backup",
                body="Không có file .sql hoặc .sqlite3 nào để sao lưu.",
                password=app_password
            )
    except Exception as e:
        print(f"Backup thất bại: {e}")

        send_email(
            sender_mail,
            receiver_email,
            subject="Thông báo! Backup Database Thất Bại",
            body=f"Đã xảy ra lỗi khi backup database: {e}",
            password=app_password
        )
    
if __name__ == '__main__':
    schedule.every().day.at('00:00').do(backUp_database)

    while True:
        schedule.run_pending()
        time.sleep(1)