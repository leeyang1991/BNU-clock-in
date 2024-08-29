# coding=utf-8
import email
import smtplib
import time
import os

server_ip = "192.168.191.2"
hostname = 'UA190' + '_' + server_ip
email_address = 'xxx@email.com'
pwd = 'xxx'
smtp_server = 'xxx'
max_fail_times = 3 # after 3 times fail, no longer send emails

now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def hotmail_email(content,fail_times):
    msg = email.message_from_string(content)
    msg['From'] = email_address
    msg['To'] = email_address
    msg['Subject'] = f"[Server message] {fail_times}"
    s = smtplib.SMTP(smtp_server,587)
    s.ehlo() # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.starttls() #Puts connection to SMTP server in TLS mode
    s.ehlo()
    s.login(email_address, pwd)
    s.sendmail(email_address, email_address, msg.as_string())
    s.quit()

def is_server_online():
    # server_ip = "192.168.191.4"
    ping_server = "ping " + server_ip + " -c 10"
    ping_result = os.popen(ping_server).read()
    if "100% packet loss" in ping_result:
        return False # server online
    else:
        return True # server offline
    pass

def fail_log_add_number():
    fpath = f'{hostname}_fail_times.txt'
    if not os.path.exists(fpath):
        number = init_log()
    else:
        fr = open(fpath, "r")
        number = fr.read()
        number = int(number)
        fr.close()
        number = number + 1
        fr = open(fpath, "w")
        fr.write(str(number))
        fr.close()
    return number

def success_log():
    fpath = f'{hostname}_success_log.txt'
    fa = open(fpath, "a")
    fa.write(f'[{now}] success\n')
    fa.close()

def init_log():
    fpath = f'{hostname}_fail_times.txt'
    fw = open(fpath, "w")
    fw.write("0")
    fw.close()
    return 0

def crontab():
    # every 10 minutes
    # */10 * * * * /usr/bin/python /root/ua_network_test.py
    pass

def main():
    online = is_server_online()
    timezone = time.timezone
    timezone_str = time.strftime("%z", time.localtime(timezone))
    timezone_str = timezone_str[0:3] + ":" + timezone_str[3:5]
    if not online:
        number = fail_log_add_number()
        if number > max_fail_times:
            return
        if number == max_fail_times:
            content = f'{hostname} Down at [{now}]\nTimezone: {timezone_str}'
            hotmail_email(f'{content}\nNo longer send emails',number)
        if number < max_fail_times:
            content = f'{hostname} Down at [{now}]\nTimezone: {timezone_str}'
            hotmail_email(content,number)
    else:
        init_log()
        success_log()
    pass

if __name__ == '__main__':
    main()