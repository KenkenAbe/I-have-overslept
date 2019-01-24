from django.shortcuts import render,redirect,HttpResponse
import urllib.request as http_request
from django.http import Http404, JsonResponse
from django.core import serializers
import urllib
import json
import requests
import base64
from table.models import timetables,users,teachers,notifications,devices
from datetime import datetime, timedelta, timezone
from Crypto import Random
from Crypto.Cipher import AES
import string, random
import time, datetime
import re
import sendgrid
from sendgrid.helpers.mail import *

class AESCipher(object):
    def __init__(self, key, block_size=32):
        self.bs = block_size
        if len(key) >= len(str(block_size)):
            self.key = key[:block_size]
        else:
            self.key = self._pad(key)

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc + '=' * (-len(enc) % 4))
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


# Create your views here.
def table(request):
    """時間割画面"""

    params = {"user_id": "", "lessons": {}}

    if request.COOKIES.get("key") == None:
        return redirect("/login")
        params["user_id"] = ""
    else:
        encryption_key = "f012c2a1c35e7952"
        encryptor = AESCipher(encryption_key)

        token = encryptor.decrypt(request.COOKIES.get("key")).decode("utf-8").split(":")

        current_user = users.objects.filter(target_id=token[0],token=token[1])

        if current_user == None:
            params["user_id"] = ""
        else:
            params["user_id"] = ""

        params["user_id"] = current_user.first().userName

        timetable_data = timetables.objects.filter(target_id=current_user.first().target_id,quater=4)
        for i in range(0,7):
            for j in range(1,7):
                dummy_data = timetables()
                dummy_data.title = "　"
                params["lessons"][str(i) + "_" + str(j)] = dummy_data
        for data in timetable_data:
            params["lessons"][str(data.week) + "_" + str(data.time)] = data

    teachers_data = teachers.objects.all()
    teachers_arr = []
    for i in teachers_data:
        teachers_arr.append(i.name)

    params["teachers"] = teachers_arr

    return render(request, 'timetable.html', params)


def setting(request):
    """設定画面"""
    return render(request, 'setting.html')

def login(request):
    """Googleへのログイン（そのままリダイレクト）"""
    return redirect("https://accounts.google.com/o/oauth2/auth?client_id=428921365707-kmk7u4ns6djre3lqa4k8mbdopeb41742.apps.googleusercontent.com&redirect_uri=https://scheduler.iniadstulab.jp/login/g/callback&scope=openid%20email%20profile&response_type=code&hd=iniad.org")

def g_callback(request):
    url = "https://accounts.google.com/o/oauth2/token"
    params = {
        "code":request.GET["code"],
        "client_id":"428921365707-kmk7u4ns6djre3lqa4k8mbdopeb41742.apps.googleusercontent.com",
        "client_secret":"9RoqcGBwCgl7d1mJI2BIv5Uq",
        "redirect_uri":"https://scheduler.iniadstulab.jp/login/g/callback",
        "grant_type":"authorization_code"
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    print(params)
    print(json.dumps(params).encode())

    res = requests.post(url,urllib.parse.urlencode(params),headers=headers)



    print(res.text)

    if res.status_code == 200:
        result = json.loads(res.text)
        id_token = result["id_token"]
        splited_id_token = id_token.split(".")[1]
        raw_info = json.loads(base64.urlsafe_b64decode(splited_id_token + '=' * (-len(splited_id_token) % 4)).decode("utf-8"))

        """OpenID Connectの検証処理をここで行う"""

        url = "https://www.googleapis.com/oauth2/v1/userinfo"

        params = {
            "access_token": result["access_token"]
        }

        user_info_response = requests.get(url,urllib.parse.urlencode(params))
        user_info = json.loads(user_info_response.text)
        print(user_info)

        response = redirect("/")

        if user_info["hd"] != "iniad.org":
            return redirect("/")

        current_user_data = users.objects.filter(email=user_info["email"])
        if current_user_data.count() == 0:
            print("新規登録")
            new_user_data = users()
            new_user_data.email = user_info["email"]
            new_user_data.token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            new_user_data.target_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            new_user_data.userName = user_info["name"]
            new_user_data.admission_year = 2018
            new_user_data.permission_level = 0
            new_user_data.offset_time = 0

            new_user_data.save()

            encryption_key = "f012c2a1c35e7952"
            encryptor = AESCipher(encryption_key)

            token = encryptor.encrypt(new_user_data.target_id+":"+new_user_data.token)
        else:
            print("ユーザーが存在しています")

            encryption_key = "f012c2a1c35e7952"
            encryptor = AESCipher(encryption_key)

            token = encryptor.encrypt(current_user_data[0].target_id+":"+current_user_data[0].token)




        #ひとまず名前をbase64encodeしたものをcookieに入れてるけど、セキュリティ上危ないので変更されるべき

        response.set_cookie("key",token.decode("utf-8"))

        return response

    return redirect("/")



def authorization(request):
    if request.COOKIES.get('key') == None:
        return False

def user_settings(request):
    try:
        if request.method != "POST":
            raise AttributeError

        encryption_key = "f012c2a1c35e7952"
        encryptor = AESCipher(encryption_key)

        token = encryptor.decrypt(request.COOKIES.get("key")).decode("utf-8").split(":")

        current_user = users.objects.filter(target_id=token[0], token=token[1])
        target_user = current_user.first()

        target_user.offset_time = int(request.POST["offset"])*60

        target_user.save()

        return redirect("/")
    except:
         return HttpResponse("System Error! InternalError or Invalid User, Please contact to administrator")

def createTimetable(request):
    """if request.GET["title"] == "" or request.GET["teacher"] == "" or request.GET["start_time"] == None or request.GET["end_time"] == None or request.GET["week"] == "" or request.GET["time"] == "":
        return None"""

    print(request.POST)

    target_user_id = ""

    if request.COOKIES.get("key") != None:
        encryption_key = "f012c2a1c35e7952"
        encryptor = AESCipher(encryption_key)

        token = encryptor.decrypt(request.COOKIES.get("key")).decode("utf-8").split(":")

        current_user = users.objects.filter(target_id=token[0],token=token[1])

        target_user_id = current_user.first().target_id




    week_dict = {"月":0,"火":1,"水":2,"木":3,"金":4}

    conflict_data = timetables.objects.filter(target_id=target_user_id,week=week_dict[request.POST['week']],time=int(request.POST['time']),quater=int(request.POST['quater']))

    #POSTされた曜日、時間に既にデータが存在するかを確認

    if len(conflict_data) != 0: #存在する場合は邪魔なので削除
        print("重複データあり")
        conflict_data.delete()

    new_data = timetables()
    new_data.title = request.POST["title"]
    new_data.target_id = target_user_id
    new_data.level = 0
    new_data.room = request.POST["room"]


    #曜日ごとに開始時間と終了時間を指定
    if int(request.POST['time']) == 1:
        new_data.start_time = 32400
        new_data.end_time = 37800
    elif int(request.POST['time']) == 2:
        new_data.start_time = 38400
        new_data.end_time = 43800
    elif int(request.POST['time']) == 3:
        new_data.start_time = 46800
        new_data.end_time = 52200
    elif int(request.POST['time']) == 4:
        new_data.start_time = 53100
        new_data.end_time = 58500
    elif int(request.POST['time']) == 5:
        new_data.start_time = 59400
        new_data.end_time = 64800
    elif int(request.POST['time']) == 6:
        new_data.start_time = 65700
        new_data.end_time = 71100
    else:
        new_data.start_time = 0
        new_data.end_time = 0

    new_data.week = week_dict[request.POST['week']]
    new_data.time = int(request.POST['time'])
    new_data.quater = int(request.POST['quater'])
    new_data.year = 2018 #授業開講年度
    new_data.teacher = request.POST["teacher"]
    new_data.isNotification = False

    print(new_data.title)
    print(new_data.isNotification)

    new_data.save()

    return redirect("/")

def timeGet():
    UTC = timezone.utc
    now_time = datetime.now(UTC)
    today_oclock_time = datetime(now_time.year,now_time.month,now_time.day,0,0,0,0)

    time = datetime(now_time.year,now_time.month,now_time.day,16,15,00,00,tzinfo=timezone.utc)

    distance_time = int(time.timestamp() - today_oclock_time.timestamp())
    return distance_time

def getTableData(request):
    encryption_key = "f012c2a1c35e7952"
    encryptor = AESCipher(encryption_key)

    print(request.META["HTTP_AUTHORIZATION"])
    encrypted_token = encryptor.decrypt(request.META["HTTP_AUTHORIZATION"]).decode("utf-8").split(":")
    print(encrypted_token)
    user = users.objects.filter(target_id=encrypted_token[0], token=encrypted_token[1])[0]
    target_data = timetables.objects.filter(target_id=user.target_id,week=request.GET["week"],time=request.GET["time"],quater=4)


    try:
        if len(target_data) == 0:
            raise AttributeError
        else:
            json_response = {
                "status": "accepted",
                "content": json.loads(serializers.serialize("json", target_data)),
                "error_description": None
            }

            return JsonResponse(json_response)
    except:
        json_response = {
            "status" : "error",
            "content" : None,
            "error_description" : "Dump Failed"
        }
        return JsonResponse(json_response)

def checkAlermStatus(request):
    pended_notify_data = notifications.objects.all()
    now_time = datetime.datetime.today() + datetime.timedelta(hours=9)

    now_time_from_oclock = datetime.datetime(1970,1,1,now_time.hour,now_time.minute)

    print("現在時刻：",int(now_time_from_oclock.timestamp()))
    pending_start_call_tokens = []
    pending_timeout_call_tokens = []

    for i in pended_notify_data:
        if i.fireTime <= int(now_time_from_oclock.timestamp()) and i.status == 0 and i.isContact == False:
            #時間を超過している未発火の通知を発射（えいっ）
            target_device = devices.objects.filter(target_id=i.target).first()
            token = target_device.device_token

            pending_start_call_tokens.append(token)

            i.status = 1  # DBの状態変更
            i.save()



        elif i.fireTime+600 <= int(now_time_from_oclock.timestamp()) and i.status == 1 and i.isContact == False and i.isProcessOnRails == False:
            #通知発火から10分後+まだ起きてない = ぼくはねぼうしました
            #ここで引っかかった時点でもう遅い

            #TODO:SendGridを通して教員にメール
            target_device = devices.objects.filter(target_id=i.target)
            token = target_device[0].device_token

            pending_timeout_call_tokens.append(token)

            target_teacher = teachers.objects.filter(name=i.targetTeacher)[0]

            target_teacher_email = target_teacher.mail
            target_teacher_name = target_teacher.name

            sendgrid_api_key = "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"

            this_user = users.objects.filter(target_id=i.target)[0]

            this_user_mail = this_user.email
            this_user_name = this_user.userName

            text = "{0}先生\nお世話になっております。\n{1}を受講している　{2}（学籍番号：{3}）です。\n本日の授業ですが、ぼくはねぼうしました。".format(target_teacher_name,i.title,this_user_name,re.search("s(.*).@iniad.org", this_user_mail)[1])

            sg_client = sendgrid.SendGridAPIClient(sendgrid_api_key)

            from_email = Email(this_user_mail)
            to_email = Email(target_teacher_email)
            subject = "今日の{0}の授業について".format(i.title)
            content = Content("text/plain", text)
            mail = Mail(from_email, subject, to_email, content)
            response = sg_client.client.mail.send.post(request_body=mail.get())

            i.status = 2  # DBの状態変更
            i.save()


    #Gaurunに対して通知の発火処理
    notify_server_url = "http://localhost:1057/push"
    params_start = {
        "notifications": [
            {
                "token": pending_start_call_tokens,
                "platform": 1,
                "message": "{\"action\":\"call\"}"
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json'
    }

    requests.post(notify_server_url,json.dumps(params_start),headers=headers)

    #着信停止の処理（いつまでも鳴り続けるため）
    params_stop = {
        "notifications": [
            {
                "token": pending_timeout_call_tokens,
                "platform": 1,
                "message": "{\"action\":\"timeout\"}"
            }
        ]
    }

    requests.post(notify_server_url, json.dumps(params_stop), headers=headers)
            #ぼくはねぼうしました

    json_response = {
        "status": "accepted",
        "content": None,
        "error_description": None
    }

    return JsonResponse(json_response)

def alertTime():
    timetable_data = timetables.objects.filter(week=datetime.date.today().weekday(),quater=4)
    start = timetable_data.start_time()
    #setTime = 
    #fireTime = start - setTime

def initialize_alert(request):
    today_time = datetime.datetime.today() + datetime.timedelta(hours=9)
    timetable_data = timetables.objects.filter(week=today_time.weekday(),quater=4) #今日開講予定で登録されている時間割を取得

    current_notify_queue = notifications.objects.filter(isProcessOnRails=False)

    if current_notify_queue != None:
        current_notify_queue.delete()

    for i in timetable_data:
        user_device = devices.objects.filter(target_id=i.target_id)
        target_user = users.objects.filter(target_id=i.target_id)
        print(i.target_id)
        print(i.title)
        if user_device == None:
            continue
        else:
            new_pending_alert = notifications()
            new_pending_alert.target = i.target_id
            new_pending_alert.targetTeacher = i.teacher
            new_pending_alert.fireTime = i.start_time - target_user.first().offset_time
            new_pending_alert.status = 0
            new_pending_alert.isContact = False
            new_pending_alert.title = i.title
            new_pending_alert.isProcessOnRails = False

            new_pending_alert.save()

    json_response = {
        "status": "accepted",
        "content": None,
        "error_description": None
    }

    return JsonResponse(json_response)