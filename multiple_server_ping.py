# coding=utf-8
import time
import os
import requests
On_Red='\033[41m' # red background
NC='\033[0m' # No Color
timezone = time.timezone
timezone_str = time.strftime("%z", time.localtime(timezone))
timezone_str = timezone_str[0:3] + ":" + timezone_str[3:5]

def get_conf():
    import configparser
    conf_path = '/root/network_test.conf'
    config = configparser.ConfigParser()
    config.read(conf_path)
    host_server_name = config['Host_server_info']['name']
    host_server_ip = config['Host_server_info']['ip_addr']
    APP_TOKEN = config['Pushover_token']['APP_TOKEN']
    USER_KEY = config['Pushover_token']['USER_KEY']

    Clients_info = config['Clients_info']
    server_ip_name_dict = {}
    for host in Clients_info:
        ip = Clients_info[host]
        server_ip_name_dict[ip]=host
    # exit()
    max_fail_times=2
    return host_server_name,APP_TOKEN,USER_KEY,server_ip_name_dict,max_fail_times,host_server_ip
    pass

def pushover(title,message):
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_ = get_conf()
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
        # print(r.content)
    except Exception as e:
        os.system(f'echo "{On_Red}{e}{NC}"')

def gen_message(message_dict,host_status_dict,fail_num_dict):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,host_server_ip = get_conf()
    title = f'{host_server_name}'
    content = f'[{now}]' + ' ' + f'Timezone: {timezone_str}' + '\n'
    if len(message_dict) == 0:
        return None, None
    for host in message_dict:
        message = message_dict[host]
        fail_time = fail_num_dict[host]
        if fail_time > 0:
            content += f'{message}, fail times:{fail_time}\n'
        else:
            content += f'{message}\n'
    content += '\n------Hosts status------\n'
    for host in host_status_dict:
        host_name = server_ip_name_dict[host]
        online = host_status_dict[host]
        if not online:
            content += f'{host_name}:{host} is Down\n'
        else:
            content += f'{host_name}:{host} is Up\n'
    content += '------Hosts status------\n\n'
    content += f'From {host_server_name}:{host_server_ip}'
    return title, content

def is_server_online():
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_ = get_conf()
    # fpath = 'net_test_conf_test.txt'
    # fr = open(fpath, "r")
    # lines = fr.readlines()
    # fr.close()
    # status_dict = {}
    #
    # for line in lines:
    #     line = line.split('\n')[0]
    #     host, status = line.split(' ')
    #     status = eval(status)
    #     status_dict[host] = status

    server_ip_list = list(server_ip_name_dict.keys())
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

def fail_message(host,fail_num):
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_ = get_conf()
    hostname = server_ip_name_dict[host]
    content = f'{hostname}:{host} Down'
    return content

def recover_message(host):
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_ = get_conf()

    hostname = server_ip_name_dict[host]
    content = f'{hostname}:{host} Recover'
    # pushover(title,content)
    return content

def main():
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_ = get_conf()
    fail_num_dict = {}
    for host in server_ip_name_dict:
        fail_num_dict[host] = 0
    while 1:
        host_status_dict = is_server_online()
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        message_dict = {}
        for host in host_status_dict:
            # print(host)
            online = host_status_dict[host]
            if not host in fail_num_dict:
                fail_num_dict[host] = 0
            fail_num = fail_num_dict[host]
            if not online:
                os.system(f'echo "[{now}] {host} is {On_Red}offline{NC}"')
                fail_num += 1
                fail_num_dict[host] = fail_num
                if fail_num <= max_fail_times:
                    fail_content = fail_message(host,fail_num)
                    message_dict[host] = fail_content
            else:
                os.system(f'echo "[{now}] {host} is online"')
                if fail_num > 0:
                    fail_num = 0
                    fail_num_dict[host] = fail_num
                    recover_content = recover_message(host)
                    message_dict[host] = recover_content

        title, content = gen_message(message_dict,host_status_dict,fail_num_dict)
        print(title)
        print(content)
        if title is not None and content is not None:
            # print('push')
            pushover(title,content)
        os.system(f'echo ------sleep 10 min------')
        time.sleep(600)

if __name__ == '__main__':
    main()