# coding=utf-8
import time
import os
import requests

server_ip_name_file = '/root/server_ip_name.txt'
server_ip_name_file_r = open(server_ip_name_file, 'r')
host_server_name = server_ip_name_file_r.readline().split('\n')[0]
server_ip_name_dict = eval(server_ip_name_file_r.read())

# host_server_name = 'server_name'

# server_ip_name_dict = {
#     "192.168.100.2":'home',
#     "192.168.100.3":'work',
# }


APP_TOKEN = 'xxxxxx'
USER_KEY = 'xxxxxx'

def pushover(title,message):
    title = host_server_name + ' ' + title
    print('title----------',title)
    print('message----------',message)
    print(title,message)
    try:
        r = requests.post(
            'https://api.pushover.net/1/messages.json',
            data={
                'token': APP_TOKEN,
                'user': USER_KEY,
                'message': message,
                'title': title,
            },
        )
    except Exception as e:
        print(e)

def is_server_online():
    server_ip_list = list(server_ip_name_dict.keys())
    # ping_server = "fping " + ' '.join(server_ip_list) + " -c2 -t1000"
    ping_server = "fping " + ' '.join(server_ip_list)
    ping_results = os.popen(ping_server).read()
    ping_results_lines = ping_results.split('\n')
    status_dict = {}
    for line in ping_results_lines:
        try:
            host,status = line.split(' is ')
            if status == 'alive':
                status = True
            else:
                status = False
        except:
            continue
        status_dict[host] = status
    return status_dict

def send_fail_message(host,fail_num,max_fail_times=3):
    hostname = server_ip_name_dict[host]
    timezone = time.timezone
    timezone_str = time.strftime("%z", time.localtime(timezone))
    timezone_str = timezone_str[0:3] + ":" + timezone_str[3:5]
    fail_num += 1
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f'fail times: [{fail_num}] {host} [{now}] offline')
    if fail_num > max_fail_times:
        return fail_num
    if fail_num == max_fail_times:
        content = f'{hostname}:{host} Down at [{now}]\nTimezone: {timezone_str}'
        title = f'{hostname}:{host} Down'
        pushover(title,f'{content}\nNo longer send messages, fail times:{fail_num}')
    if fail_num < max_fail_times:
        content = f'{hostname}:{host} Down at [{now}]\nTimezone: {timezone_str}\nfail times: {fail_num}'
        title = f'{hostname}:{host} Down'
        pushover(title,content)
    return fail_num

def send_recover_message(host):
    timezone = time.timezone
    timezone_str = time.strftime("%z", time.localtime(timezone))
    timezone_str = timezone_str[0:3] + ":" + timezone_str[3:5]
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    hostname = server_ip_name_dict[host]
    title = f'{hostname}:{host} Recover'
    content = f'{hostname}:{host} Recover at [{now}]\nTimezone: {timezone_str}'
    pushover(title,content)

def main():
    fail_num_dict = {}
    for host in server_ip_name_dict:
        fail_num_dict[host] = 0
    while 1:
        host_status_dict = is_server_online()
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        for host in host_status_dict:
            # print(host)
            online = host_status_dict[host]
            fail_num = fail_num_dict[host]
            if not online:
                fail_num = send_fail_message(host,fail_num)
                fail_num_dict[host] = fail_num
            else:
                print(f'[{now}] {host} is online')
                if fail_num > 0:
                    fail_num = 0
                    fail_num_dict[host] = fail_num
                    send_recover_message(host)
            pass

        time.sleep(600)

if __name__ == '__main__':
    main()