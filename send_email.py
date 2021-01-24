# coding=utf-8
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import datetime

def send_clock_in_message(msg):
    mail_host="smtp.qq.com"  #
    mail_user="xxx@qq.com"    #
    mail_pass="xxx"   #

    sender = 'xxxxxx@qq.com'
    receivers = ['xxxxx@qq.com']

    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header("xxxxx@qq.com", 'utf-8')
    message['To'] = Header("xxxx@qq.com", 'utf-8')
    now = datetime.datetime.now()
    date_str = now.strftime('%Y.%m.%d')
    subject = '{} {}'.format(msg,date_str)
    # print subject

    message['Subject'] = Header(subject, 'utf-8')

    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 587)  # 25 为 SMTP 端口号
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功")


def main():
    send_clock_in_message('Desktop Success')
    pass


if __name__ == '__main__':
    main()








