# -*- coding: utf-8 -*-

import logging
import requests
import json
import time
import random
import re
import hashlib
import os
import platform
import sys
import traceback
import getopt
import base64
from urllib import parse

VERSION_NAME = "FxxkSsxx"
ua = ""
max1 = 0
cookie = ""
answer_dictionary = {}
hit_count = 0
starttime = 0
mode_id_list = [
    {"id": "5f71e934bcdbf3a8c3ba51d5", "name": "英雄篇"},
    {"id": "5f71e934bcdbf3a8c3ba51d6", "name": "复兴篇"},
    {"id": "5f71e934bcdbf3a8c3ba51d7", "name": "创新篇"},
    {"id": "5f71e934bcdbf3a8c3ba51d8", "name": "信念篇"},
]
mode_id = None
random_mode_enabled = True
inform_enabled = False
auto_refresh_token_enabled = False
expire_time = -1
way = "1"
maxtime = 0
nowtime = 0
timesort = []

class MyError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "{}({})".format(self.msg, self.code)


def SubmitVerification(header, code=None):
    if code == None:
        if way == "1":
            code = "HD1bhUGI4d/FhRfIX4m972tZ0g3jRHIwH23ajyre9m1Jxyw4CQ1bMKeIG5T/voFOsKLmnazWkPe6yBbr+juVcMkPwqyafu4JCDePPsVEbVSjLt8OsiMgjloG1fPKANShQCHAX6BwpK33pEe8jSx55l3Ruz/HfcSjDLEHCATdKs4="
        elif way == "2":
            code = "BzPdXIQzu5Z2GHMkgWt9iBUQTbo2EWmw7tIuDaIEa4EQSXziGlUmS4aqrzw8Pzo51P+YtbUpAaqKLWF/rG4G41TnHGtItm7NkU90024LysxGUzh4jhy9YO0ivJZ3MSv+WcA8u/1TacORW4cvm9uBejdpTBOdWsDFOjJpTdCkYYE="
    
    submit_data = {
        "activity_id": "5f71e934bcdbf3a8c3ba5061",
        "mode_id": mode_id,
        "way": way,
        "code": code
    }
    url = "https://ssxx.univs.cn/cgi-bin/save/verification/code/"
    header["Content-Type"] = "application/json;charset=utf-8"
    header["origin"]="https://ssxx.univs.cn"
    response = requests.post(url, json=submit_data, headers=header)
    result = json.loads(response.text)
    if result["code"] != 0:
        raise MyError(result["code"], "提交验证码失败: " + str(result))


def CheckVerification(header, code=None):
    if code == None:
        if way == "1":
            code = "E5ZKeoD8xezW4TVEn20JVHPFVJkBIfPg+zvMGW+kx1s29cUNFfNka1+1Fr7lUWsyUQhjiZXHDcUhbOYJLK4rS5MflFUvwSwd1B+1kul06t1z9x0mfxQZYggbnrJe3PKEk4etwG/rm3s3FFJd/EbFSdanfslt41aULzJzSIJ/HWI="
        elif way == "2":
            code = "caap/GndfVmhoudMEhf1C7vjG5Hyc1gMLPNZAT6yfdx2kt8jOTCzUYsbd1dyqUYRCv4/rLZGf++4HIK/7Q2/ZWlOkQDTV9gxOOHjwkKqkF/oZZIOg0714FXPZj8eet44bp481QRDyjqBzwGAM3xzQut5bLqeTLkayexsu2Q3P9g="
    
    submit_data = {
        "activity_id": "5f71e934bcdbf3a8c3ba5061",
        "mode_id": mode_id,
        "way": way,
        "code": code
    }
    url = "https://ssxx.univs.cn/cgi-bin/check/verification/code/"
    header["Content-Type"] = "application/json;charset=utf-8"
    header["origin"]="https://ssxx.univs.cn"
    response = requests.post(url, json=submit_data, headers=header)
    result = json.loads(response.text)
    if result["code"] != 0:
        raise MyError(result["code"], "检查验证码失败: " + str(result))

    return result["status"]


def ParseToken(token):
    data = token.split('.')
    user_info = json.loads(str(base64.b64decode(data[1] + "=="), "utf-8"))

    token_info = {
        "name": user_info["name"],
        "uid": user_info["uid"],
        "time": int(user_info["iat"]),
        "expire": int(user_info["exp"])
    }
    return token_info


def RefreshToken(header):
    url = "https://ssxx.univs.cn/cgi-bin/authorize/token/refresh/"
    response = requests.get(url, headers=header)

    result = json.loads(response.text)
    if result["code"] != 0:
        raise MyError(result["code"], "更新token失败: " + str(result["message"]))

    new_token = result["token"]

    detail = ParseToken(new_token)
    print("token更新完成，于 ", time.asctime(time.localtime(detail["time"])), " 生效")
    print("将在 ", time.asctime(time.localtime(detail["expire"])), " 失效")

    return new_token


def SendNotification(msg):
    #if not inform_enabled:
        #print("[info] ", msg)
        #return
    #url = "http://localhost:6666"
    #payload = {"type": VERSION_NAME, "msg": msg}
    #response = requests.post(url, json=payload)
    #print(response.text)
    pass


def ReadAnswerFromFile():
    global answer_dictionary
    answer_file = open('answer.txt', 'r')
    answer_dictionary = json.loads(answer_file.read())
    print("已读取", len(answer_dictionary.items()), "个答案！")
    answer_file.close()


def SaveAnswerToFile():
    #global answer_dictionary
    #answer_file = open('answer.txt', 'w')
    #answer_file.write(json.dumps(answer_dictionary))
    #print("已保存", len(answer_dictionary.items()), "个答案！")
    #answer_file.close()
    pass


def BuildHeader(token):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'x-requested-with': 'com.tencent.mm',
        'Host': 'ssxx.univs.cn',
        'Referer': 'https://ssxx.univs.cn/client/exam/5f71e934bcdbf3a8c3ba5061/1/1/' + mode_id,
        'User-Agent': ua,
        'Authorization': 'Bearer ' + token,
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'cookie': cookie
    }

    return headers


def PrintQuizObject(quiz_object):
    pass
    print("问题ID列表: ")
    for i in range(0, 20):
        print("问题", i, ": ", quiz_object["question_ids"][i])


def StartQuiz(header):
    global hit_count
    hit_count = 0

    print("尝试开始考试……")

    url = "https://ssxx.univs.cn/cgi-bin/race/beginning/?t={}&activity_id=5f71e934bcdbf3a8c3ba5061&mode_id={}&way={}".format(
        int(time.time()),
        mode_id,
        way
    )

    for fail in [0, 1, 2]:
        response = requests.request("GET", url, headers=header)
        quiz_object = json.loads(response.text)
        status_code = quiz_object["code"]

        if status_code == 0:
            print("开始考试成功，本次考试信息如下: ")
            print("race_code", quiz_object["race_code"])

            return quiz_object["question_ids"], quiz_object["race_code"]

        elif status_code == 4832:
            print("答题次数用完，等待10分钟")
            if fail == 0:
                SendNotification("...")
            sys.exit(1)

        else:
            raise MyError(status_code, "开始考试失败: " + str(quiz_object))


def GetTitleMd5(title):
    title = re.sub(
        r"<(\w+)[^>]+?(?:display: {0,}none;).*?>.*?<\/\1>", "", title)
    title = re.sub("<.*?>", "", title)
    result = hashlib.md5(title.encode(encoding='UTF-8')).hexdigest()
    print(title, ", hash:", result)
    return result


def GetQuestionDetail(question_id, header):
    url = "https://ssxx.univs.cn/cgi-bin/race/question/?t={}&activity_id=5f71e934bcdbf3a8c3ba5061&question_id={}&mode_id={}&way={}".format(
        int(time.time()),
        question_id,
        mode_id,
        way
    )

    response = requests.request("GET", url, headers=header)

    if response.status_code != 200:
        raise MyError(response.status_code, "获取题目信息失败")

    question_detail_object = json.loads(response.text)
    if question_detail_object["code"] != 0:
        raise MyError(question_detail_object["code"], "获取题目信息失败。问题ID: " +
                      question_id + "错误信息: " + str(question_detail_object))

    print("获取题目信息成功。")

    question = {}
    question["id"] = question_detail_object["data"]["id"]
    question["title"] = GetTitleMd5(question_detail_object["data"]["title"])
    question["answer_list"] = []
    for i in question_detail_object["data"]["options"]:
        question["answer_list"].append((i["id"], GetTitleMd5(i["title"])))

    return question


def BuildAnswerObject(question):
    global answer_dictionary
    global hit_count

    print("正在尝试寻找答案……")

    answer_object = {
        "activity_id": "5f71e934bcdbf3a8c3ba5061",
        "question_id": question["id"],
        "answer": None,
        "mode_id": mode_id,
        "way": way
    }

    if answer_dictionary.__contains__(question["title"]):
        hit_count += 1
        print("答案库中存在该题答案")
        answer_object["answer"] = []
        for i in question["answer_list"]:
            if i[1] in answer_dictionary[question["title"]]:
                answer_object["answer"].append(i[0])
    else:
        print("答案库中不存在该题答案，蒙一个A选项吧")
        answer_object["answer"] = [question["answer_list"][0][0]]

    return answer_object, question


def SubmitAnswer(answer_object, header):
    global answer_dictionary

    url = "https://ssxx.univs.cn/cgi-bin/race/answer/"

    header["Content-Type"] = "application/json;charset=utf-8"
    header["origin"]="https://ssxx.univs.cn"
    response = requests.request(
        "POST", url, headers=header, data=json.dumps(answer_object[0]))

    if response.status_code != 200:
        raise MyError(response.status_code, "提交答案失败")
    print(response.text)
    result_object = json.loads(response.text)

    if not result_object["data"]["correct"] and answer_dictionary.__contains__(answer_object[1]["title"]):
        print("答案库中已有答案但不正确！")
    elif result_object["data"]["correct"] and answer_dictionary.__contains__(answer_object[1]["title"]):
        return True
    elif result_object["data"]["correct"] and not answer_dictionary.__contains__(answer_object[1]["title"]):
        SaveAnswerToFile()
        print("运气不错，居然蒙对了，保存答案")
    elif not result_object["data"]["correct"] and not answer_dictionary.__contains__(answer_object[1]["title"]):
        SaveAnswerToFile()
        print("答案错误，更新答案")

    if not answer_dictionary.__contains__(answer_object[1]["title"]):
        answer_dictionary[answer_object[1]["title"]] = []

    for i in result_object["data"]["correct_ids"]:
        print("服务器返回的正确答案: ", i)
        for j in answer_object[1]["answer_list"]:
            if i == j[0]:
                print("已在问题列表中找到该答案，元组为", j)
                answer_dictionary[answer_object[1]["title"]].append(j[1])
                break

    return result_object["data"]["correct"]


def FinishQuiz(race_code, header):
    global maxtime
    global timesort
    url = "https://ssxx.univs.cn/cgi-bin/race/finish/"

    header["Content-Type"] = "application/json;charset=utf-8"
    header["origin"]="https://ssxx.univs.cn"
    payload = "{\"race_code\":\"" + race_code + "\"}"

    result = json.loads(requests.request(
        "POST", url, headers=header, data=payload).text)
    fail = 0
    while result["code"] != 0:
        print("完成考试时出错，错误代码: ", result)
        err_code = result["code"]
        if err_code == 1001 or err_code == 1002:
            raise MyError(err_code, "请重新登录")
        fail += 1
        if fail > 5:
            raise MyError(err_code, "完成时出错: " + str(result))
        time.sleep(0.5)
        result = json.loads(requests.request(
            "POST", url, headers=header, data=payload).text)

    timesort.append(int(time.time()) - nowtime)
    timesort.sort(reverse = False)
    maxtime = timesort[-1]
    print("回答完毕，本次得分: ", result["data"]["owner"]["correct_amount"], "答案库命中数: ", hit_count, "本轮用时：", int(time.time()) - nowtime)


def Start(token):
    global mode_id
    global expire_time
    global nowtime
    global starttime
    ReadAnswerFromFile()
    times = 0
    starttime = int(time.time())
    try:
        while 900 - int(time.time()) + starttime > maxtime + 30:
            mode = mode_id_list[random.randrange(0, 4)]
            mode_id = mode["id"]
            times += 1
            nowtime = int(time.time())
            print("次数：", times)
            print("模式为", mode["name"])
            print("剩余可执行时间", 900 - int(time.time()) + starttime,"最高执行时间：", maxtime)
            time.sleep(1.5)

            header = BuildHeader(token)
            check1 = random.randint(4, 10)

            question_list, race_code = StartQuiz(header)
            for i in range(0, 20):
                try:
                    if SubmitAnswer(BuildAnswerObject(GetQuestionDetail(question_list[i], header)), header):
                        print("第", i + 1, "题正确")
                        time.sleep(float(random.randint(800, 1400)) / 1000)
                    else:
                        print("第", i + 1, "题错误，已更新答案")
                        time.sleep(float(random.randrange(1500, 3000)) / 1000)
                except MyError as err:
                    if err.code == 2104:
                        SendNotification("问题不存在，已跳过: " + question_list[i])
                        pass
                    else:
                        raise err

                if i == check1:
                    if CheckVerification(header):
                        print("验证码已通过")
                    else:
                        SubmitVerification(header)
                        print("验证码状态: ", CheckVerification(header))

            FinishQuiz(race_code, header)
            time.sleep(float(random.randrange(700, 2000)) / 1000)

            if auto_refresh_token_enabled and expire_time - time.time() < 500:
                new_token = RefreshToken(header)
                expire_time = ParseToken(new_token)["expire"]
                token = new_token
                SendNotification(new_token)
                SendNotification(
                    "token已更新至 " + time.asctime(time.localtime(expire_time)))
                time.sleep(5)
        print("剩余时间不足以刷一轮，结束")
    except MyError as err:
        tag = "[{}] ".format(time.asctime(time.localtime(time.time())))

        if err.code == 1001 or err.code == 1002:
            print(tag, "登录无效，通知重新登录")
            SendNotification("请重新登录（代码: {}）".format(err.code))
        elif err.code == 1005:
            print(tag, "当前token已退出登录，请重新获取")
        else:
            msg = "已停止，原因: " + str(err)
            print(tag, msg)
            SendNotification(msg)
        sys.exit(1)
    except Exception as err:
        tag = "[{}] ".format(time.asctime(time.localtime(time.time())))
        print(tag, traceback.format_exc())
        sys.exit(1)

def main_handler(event, context):
    global ua
    global cookie
    ua = os.environ.get('ua')
    uid = os.environ.get('uid')
    avatar = os.environ.get('avatar')
    if ua is None:
        print("没有在环境变量中设置ua，已使用默认值")
        ua = "Mozilla/5.0 (Linux; Android 11; M2006J10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.62 XWEB/2767 MMWEBSDK/20210302 Mobile Safari/537.36 Author MMWEBID/1354 By MicroMessenger/8.0.2.1860(0x2800023B) lzz Process/toolsmp WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64"
    if os.environ.get('max') is None:
        print("没有在环境变量中设置最高分数，默认10000")
        max1 = 10000
    else:
        max1 = int(os.environ.get('max'))
    if uid is None:
        print("没有在环境变量中设置uid")
        return
    if avatar is None:
        print("没有在环境变量中设置avatar，已使用默认值")
        avatar = "https://node2d-public.hep.com.cn/avatar-{}-{}".format(uid, str(int(time.time()))+str(random.randrange(100,999)))
    print("uid:", uid)
    print("最高刷到", max1, "分")
    cookie = "_ga=GA1.2." + str(random.randrange(50000000,59999999)) + "." + str(time.time()-random.randrange(30000,120000)) + "; _gid=GA1.2." + str(random.randrange(500000000,599999999)) + "." + str(time.time()-random.randrange(30000,120000)) + "; tgw_l7_route=" + hashlib.md5(str(random.randrange(10000,99999)).encode('utf8')).hexdigest() + "; _gat=1"
    print("随机生成的Cookie:", cookie)
    print("访问所用的User-Agent:", ua)
    print("访问所用的Avatar:", avatar)
    url = 'https://ssxx.univs.cn/cgi-bin/authorize/token/?t={}&uid={}&avatar={}&activity_id=5f71e934bcdbf3a8c3ba5061'.format(int(time.time()),uid,parse.quote(avatar))
    a = requests.get(url=url)
    print(a.text)
    token = a.json()['token']
    try:
        if token.find("token:") == 0:
            token = token[6:]
        token = token.strip("\" ")
        token_info = ParseToken(token)
        expire_time = token_info["expire"]
        print("Token:", token)
        print("Uid: ", token_info["uid"])
        print("token有效期剩余: ", time.strftime(
            "%Hh %Mm %Ss", time.gmtime(expire_time - time.time())))
        url = "https://ssxx.univs.cn/cgi-bin/race/grade/?t={}&activity_id=5f71e934bcdbf3a8c3ba5061".format(int(time.time()))
        headers = {
            'accept': 'application/json, text/plain, */*',
            'authorization': 'Bearer %s' % (token),
            'x-requested-with': 'com.tencent.mm',
            'user-agent': ua,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://ssxx.univs.cn/client/detail/5f71e934bcdbf3a8c3ba5061/score',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cookie': cookie
        }
        response = requests.request("GET", url, headers=headers)
        print(response.text)
        score = int(response.json()["data"]["integral"])
        print("目前", score, "分")
        if score > max1 :
            print("总分数已达到环境变量中设置的", max1, "分以上")
            return
    except Exception as err:
        print(traceback.format_exc())
        sys.exit(1)

    time.sleep(1)
    Start(token)
