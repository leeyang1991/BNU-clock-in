# coding=utf-8
import time
import os
import requests
import json

server_ip_name_file = '/root/net_test_conf.json'
json_file = json.load(open(server_ip_name_file, 'r'))
host_server_name = json_file['host_server_name']
APP_TOKEN = json_file['APP_TOKEN']
USER_KEY = json_file['USER_KEY']
server_ip_name_dict = json_file['server_ip_name_dict']
max_fail_times=2

def pushover(title,message):
    title = host_server_name + ' ' + title
    # print('title----------',title)
    # print('message----------',message)
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
        os.system(f'echo {e}')

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

def send_fail_message(host,fail_num):
    hostname = server_ip_name_dict[host]
    timezone = time.timezone
    timezone_str = time.strftime("%z", time.localtime(timezone))
    timezone_str = timezone_str[0:3] + ":" + timezone_str[3:5]
    fail_num += 1
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # print(f'fail times: [{fail_num}] {host} [{now}] offline')
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
                os.system(f'echo [{now}] {host} is offline')
            else:
                os.system(f'echo [{now}] {host} is online')
                if fail_num > 0:
                    fail_num = 0
                    fail_num_dict[host] = fail_num
                    send_recover_message(host)
        os.system(f'echo ------sleep 10 min------')

        time.sleep(600)

if __name__ == '__main__':
    main()