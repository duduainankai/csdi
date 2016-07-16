# -*- coding:utf-8 -*-


# nohup python -u csdi.py > csdi.out & ssh远程连接云主机运行的命令,保证会话结束后程序依旧运行

import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import time
from email.header import Header
import ConfigParser
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = "lizheming"

ISOTIMEFORMAT = '%Y-%m-%d %X'


def send(text,count,_user,_password,_to):
    """
    发送邮件
    :param text:爬取的文章链接和题目
    :return:
    """

    smtps = re.findall(r"@(\S+)",_user)
    smtp = "smtp." + smtps[0]

    msg = MIMEText(text,'plain','utf-8')
    msg["Subject"] = Header("CSDI作业" + str(count),"utf-8").encode()
    msg["From"] = _user
    msg["To"] = _to

    s = smtplib.SMTP(smtp, timeout=30)
    try:
        s.login(_user, _password)
        #s.sendmail(_user, _to, msg.as_string())
    except Exception,e:
        print e
    s.close()


def fetch(count):
    """
    爬取页面 判断是否有新的内容发布
    :return: 有新内容则返回新的文章和问题 否则返回None
    """
    url = "http://ipads.se.sjtu.edu.cn/courses/csdi/2016/papers.html"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    weeks = soup.select(".panel.panel-default")
    if count >= len(weeks):
        print "没有新内容 进行休眠,当前时间:%s" %(time.strftime( ISOTIMEFORMAT, time.localtime()))
        time.sleep(60 * 30) #半小时查询一次
        return None
    print "发现新作业"
    content = weeks[count].find("a").text
    content += '\n'
    content += weeks[count].find("a").get("href")
    questions = [li.text for li in soup.select("ol")[count].select("li")]
    for ques in questions:
        content += '\n'
        content += ques

    print content
    return content


def main():
    cf = ConfigParser.ConfigParser()
    cf.read("config.ini")
    '''
    _user表示用户发送邮箱
    _to表示接收邮件到邮箱,推荐QQ邮箱,因为微信上也有提示
    '''
    _user = cf.get("mail","user")
    _password = cf.get("mail","password")
    _to = cf.get("mail","to")

    mode = re.compile(r'\S+@\S+(.\S)+')
    if not re.match(mode,_user):
        print "用户邮箱输入不正确"
        sys.exit()
    if not re.match(mode,_to):
        print "用户邮箱输入不正确"
        sys.exit()
    count = 0
    while True:
        res = fetch(count)
        if res:
            count += 1
            send(res,count,_user,_password,_to)

if __name__ == "__main__":
    main()