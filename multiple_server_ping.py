# coding=utf-8
import time
import os
import requests
import ipaddress
# from pprint import pprint

On_Red='\033[41m' # red background
NC='\033[0m' # No Color
timezone = time.timezone
timezone_str = time.strftime("%z", time.localtime(timezone))
timezone_str = timezone_str[0:3] + ":" + timezone_str[3:5]

def get_conf():
    import configparser
    conf_path = '/root/network_test.conf'
    # conf_path = 'network_test.conf'
    if not os.path.exists(conf_path):
        print(f'{On_Red}Error: {conf_path} not exists!{NC}')
        os.system(f'echo "{On_Red}Error: {conf_path} not exists!{NC}"')
        exit(1)
    config = configparser.ConfigParser()
    config.read(conf_path)
    host_server_name = config['Host_server_info']['name']
    host_server_ip = config['Host_server_info']['ip_addr']
    max_fail_times = config['Host_server_info']['max_fail_times']
    sleep_time_seconds = config['Host_server_info']['sleep_time_seconds']
    APP_TOKEN = config['Pushover_token']['APP_TOKEN']
    USER_KEY = config['Pushover_token']['USER_KEY']

    Clients_info = config['Clients_info']
    server_ip_name_dict = {}
    for host in Clients_info:
        ip = Clients_info[host]
        if '/' in ip:
            subnet = ip.split('/')[0]
            cidr = ip.split('/')[1]
            cidr = int(cidr)
            ip_list = ipaddress.ip_network(ip,False).hosts()
            for i,ip_i in enumerate(ip_list):
                ip_str = ip_i.__str__()
                server_ip_name_dict[ip_str] = f'{host} {i+1}'
        else:
            server_ip_name_dict[ip]=host

    max_fail_times = int(max_fail_times)
    sleep_time_seconds = int(sleep_time_seconds)

    return host_server_name,APP_TOKEN,USER_KEY,server_ip_name_dict,max_fail_times,host_server_ip,sleep_time_seconds
    pass

def pushover(title,message):
    # return
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf()
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
                'html': 1,
            },
        )
        # print(r.content)
    except Exception as e:
        os.system(f'echo "{On_Red}{e}{NC}"')

def gen_message(message_dict,host_status_dict,fail_num_dict,switch_dict,is_init_message):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    Down = html_add_color_red('Down')
    Up = html_add_color_green('Up')
    status_str_dict = {True:Up,False:Down}
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,host_server_ip,sleep_time_seconds = get_conf()
    # title = f''
    content = f'[{now}]' + ' ' + f'Timezone: {timezone_str}' + '\n\n'

    if is_init_message == True:
        title = 'Init'
        for host in host_status_dict:
            switch_status = switch_dict[host].replace('True', Up).replace('False', Down)
            host_name = server_ip_name_dict[host]
            host_name = html_add_color_blue(host_name)
            content += f'{host_name} {host} : {switch_status}\n'
        host_server_name = html_add_color_blue(host_server_name)
        content += f'\nFrom {host_server_name}:{host_server_ip}'
        content += f'\nsleep {sleep_time_seconds} seconds'
        return title, content

    if len(message_dict) == 0:
        return None, None
    current_status_str = ''
    for host in message_dict:
        message = message_dict[host]
        fail_time = fail_num_dict[host]
        if fail_time > 0:
            current_status_str += f'{message}, fail times:{fail_time}\n'
        else:
            current_status_str += f'{message}\n'
    if 'Recover' in current_status_str and 'Down' in current_status_str:
        title = 'Recover and Down'
    elif 'Down' in current_status_str:
        title = 'Down'
    elif 'Recover' in current_status_str:
        title = 'Recover'
    else:
        raise Exception
    # content += '\n------Clients status------\n'
    for host in host_status_dict:
        host_name = server_ip_name_dict[host]
        host_name = html_add_color_blue(host_name)
        switch_status = switch_dict[host].replace('True',Up).replace('False',Down)
        content += f'{host_name} {host} : {switch_status}\n'
    host_server_name = html_add_color_blue(host_server_name)
    content += f'\nFrom {host_server_name}:{host_server_ip}'
    content += f'\nsleep time:{sleep_time_seconds} seconds'
    print(content)
    return title, content

def is_server_online():
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf()

    ###### for debug ######
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
    ###### for debug ######

    server_ip_list = list(server_ip_name_dict.keys())
    ping_server = "fping " + ' '.join(server_ip_list) + " -A"
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

def init_is_server_online():
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf()

    server_ip_list = list(server_ip_name_dict.keys())
    # print(server_ip_list);exit()
    status_dict = {}
    for ip in server_ip_list:
        status_dict[ip] = None
    return status_dict

def fail_message(host):
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf()
    hostname = server_ip_name_dict[host]
    Down = 'Down'
    content = f'{hostname}:{host} {Down}'
    return content

def recover_message(host):
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf()

    hostname = server_ip_name_dict[host]
    Recover = 'Recover'
    content = f'{hostname}:{host} {Recover}'
    return content

def html_add_color_blue(text):
    text = f'<b>{text}</b>'
    text = f'<font color="#0000ff">{text}</font>'
    return text

def html_add_color_red(text):
    text = f'<b>{text}</b>'
    text = f'<font color="#ff0000">{text}</font>'
    return text

def html_add_color_green(text):
    text = f'<b>{text}</b>'
    text = f'<font color="#00ff00">{text}</font>'
    return text

def main():
    init_status_dict = init_is_server_online()
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf()
    fail_num_dict = {}
    for host in server_ip_name_dict:
        fail_num_dict[host] = 0
    is_init_message = True
    while 1:
        host_status_dict = is_server_online()
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        message_dict = {}
        switch_dict = {}
        for host in host_status_dict:
            online = host_status_dict[host]
            if not host in fail_num_dict:
                fail_num_dict[host] = 0
            if not host in init_status_dict:
                init_status_dict[host] = None
            init_online = init_status_dict[host]

            init_status_dict[host] = online
            if init_online == None:
                switch_dict[host] = f'{online}'
            else:
                if online != init_online:
                    # switch_dict[host] = f'{init_online} -> {online}'
                    switch_dict[host] = f'{init_online} &#8594 {online}'
                else:
                    switch_dict[host] = f'{online}'
            fail_num = fail_num_dict[host]
            if not online:
                os.system(f'echo "[{now}] {host} is {On_Red}offline{NC}"')
                fail_num += 1
                fail_num_dict[host] = fail_num
                if fail_num <= max_fail_times:
                    fail_content = fail_message(host)
                    message_dict[host] = fail_content
            else:
                os.system(f'echo "[{now}] {host} is online"')
                if fail_num > 0:
                    fail_num = 0
                    fail_num_dict[host] = fail_num
                    recover_content = recover_message(host)
                    message_dict[host] = recover_content
        title, content = gen_message(message_dict,host_status_dict,fail_num_dict,switch_dict,is_init_message)
        is_init_message = False
        # print(title, content)
        if title is not None and content is not None:
            content_lines = content.split('\n')
            split_content_dict = {}
            split_content_block_flag = 1
            line_len_sum = 0
            split_content = ''
            for line in content_lines:
                line_len = len(line)
                line_len_sum += line_len
                split_content += line + '\n'

                if line_len_sum >= 900:
                    split_content_dict[split_content_block_flag] = split_content
                    split_content_block_flag += 1
                    line_len_sum = 0
                    split_content = ''
                    continue

            if not len(split_content) == 0:
                split_content_dict[split_content_block_flag] = split_content
            if len(split_content_dict) == 1:
                pushover(title,content)
            else:
                for i in range(len(split_content_dict)):
                    content = split_content_dict[i+1]
                    new_title = title + f' ({i+1}/{len(split_content_dict)})'
                    pushover(new_title,content)
                    time.sleep(1)
        _, _, _, _, _, _, sleep_time_seconds = get_conf()
        os.system(f'echo ------sleep {sleep_time_seconds} seconds------')
        time.sleep(sleep_time_seconds)

if __name__ == '__main__':
    main()