# coding=utf-8
import time
import os

rules = '''


iptables -t nat -I POSTROUTING -p udp -d 10.10.12.150 --dport 1194 -j MASQUERADE
iptables -t nat -I PREROUTING -p udp --dport 7778 -j DNAT --to 10.10.12.150:1194

iptables -t nat -I PREROUTING -p udp --dport 53 -j DNAT --to 103.79.79.142:53
iptables -t nat -I POSTROUTING -p udp -d 103.79.79.142 --dport 53 -j MASQUERADE

iptables -t nat -I PREROUTING -p udp --dport 7777 -j DNAT --to 103.79.79.142:1194
iptables -t nat -I POSTROUTING -p udp -d 103.79.79.142 --dport 1194 -j MASQUERADE


'''

def check_and_add_rule(rules):
    for rule in rules.split('\n'):
        if len(rule) == 0:
            continue
        rule_command_check = rule.replace('-I', '-C')
        rule_command_check = rule_command_check.replace('-A', '-C')
        flag = os.system(rule_command_check)
        if flag == 0:
            print_to_console(f"Rule already exists: {rule_command_check}")
        else:
            print_to_console(f"No rule exists: {rule_command_check}")
            os.system(rule)
            print_to_console(f"Rule added: {rule}")

def print_to_console(text):
    os.system(f'echo {text}')

while 1:
    check_and_add_rule(rules)
    time.sleep(60)