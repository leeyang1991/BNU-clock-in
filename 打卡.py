# coding:utf-8
import datetime
import time
from selenium import webdriver

url = "https://onewechat.bnu.edu.cn/ncov/wap/default/index"
egde_drive_path = ''
account = '20173148xxxx'
passwd = 'xxxxxxxx'
daka_time = '00:05:00' # Hour:Minute:Second

def open_edge():
    driver = webdriver.Edge(egde_drive_path)
    time.sleep(4)
    driver.get(url)
    time.sleep(1)

    input = driver.find_elements_by_tag_name("input")
    time.sleep(3)
    if input[0].get_attribute("placeholder") == "账号":
        input[0].send_keys(account)
        time.sleep(2)
        input[1].send_keys(passwd)
        time.sleep(2)
        try:
            driver.find_element_by_class_name("btn").click()
        except:
            driver.find_element_by_class_name("login-btn").click()
        time.sleep(10)

    js = "var q=document.documentElement.scrollTop=800"
    driver.execute_script(js)
    locs = driver.find_elements_by_tag_name("input")
    for loc in locs:
        if loc.get_attribute("placeholder") == "点击获取地理位置":
            loc.click()
    time.sleep(10)
    driver.execute_script(js)
    driver.execute_script(js)
    driver.execute_script(js)
    submit = driver.find_element_by_link_text("提交信息（Submit）")
    submit.click()
    time.sleep(10)
    try:
        xpath = "//div[@class='wapcf-btn wapcf-btn-ok']"
        affirm = driver.find_element_by_xpath(xpath)
        affirm.click()
    except:
        xpath = "//div[@class='wapat-btn wapat-btn-ok']"
        affirm = driver.find_element_by_xpath(xpath)
        affirm.click()
    time.sleep(3)
    driver.close()

now = datetime.datetime.now()
day = str(now)[:10]
print("今天是",day)

while 1:
    now = datetime.datetime.now()
    now_str = str(now)[10:19]
    # print(now_str)
    if  any([t in str(now)[14:19] for t in ["00:00","15:00","30:00","45:00"]]):
        print(now_str)

    if daka_time in now_str:
        open_edge()

    time.sleep(1)
#
