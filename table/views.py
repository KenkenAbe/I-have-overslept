from django.shortcuts import render,redirect,HttpResponse
import urllib.request as http_request
from django.http import Http404, JsonResponse
from django.core import serializers
import urllib
import json
import requests
import base64
from table.models import timetables,Users,Teachers
from datetime import datetime, timedelta, timezone
from Crypto import Random
from Crypto.Cipher import AES
import string, random

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
        enc = base64.b64decode(enc)
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
        params["user_id"] = ""
    else:
        encryption_key = "f012c2a1c35e7952"
        encryptor = AESCipher(encryption_key)

        token = encryptor.decrypt(request.COOKIES.get("key")).decode("utf-8")

        current_user = Users.objects.filter(Mail=token)

        if current_user == None:
            params["user_id"] = ""
        else:
            params["user_id"] = ""

        params["user_id"] = current_user.first().UserName

        timetable_data = timetables.objects.filter(target_id=current_user.first().Mail)
        for data in timetable_data:
            params["lessons"][str(data.week) + "_" + str(data.time)] = data

    teachers_data = Teachers.objects.all()
    teachers_arr = []
    for i in teachers_data:
        teachers_arr.append(i.Name)

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

        current_user_data = Users.objects.filter(Mail=user_info["email"])
        if current_user_data.count() == 0:
            print("新規登録")
            new_user_data = Users()
            new_user_data.Mail = user_info["email"]
            new_user_data.Token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            new_user_data.Tag = ""
            new_user_data.UserName = user_info["name"]

            new_user_data.save()
        else:
            print("ユーザーが存在しています")


        encryption_key = "f012c2a1c35e7952"
        encryptor = AESCipher(encryption_key)

        token = encryptor.encrypt(user_info["email"])

        #ひとまず名前をbase64encodeしたものをcookieに入れてるけど、セキュリティ上危ないので変更されるべき

        response.set_cookie("key",token.decode("utf-8"))

        return response

    return redirect("/")



def authorization(request):
    if request.COOKIES.get('key') == None:
        return False

def createTimetable(request):
    """if request.GET["title"] == "" or request.GET["teacher"] == "" or request.GET["start_time"] == None or request.GET["end_time"] == None or request.GET["week"] == "" or request.GET["time"] == "":
        return None"""

    print(request.POST)

    target_user_id = ""

    if request.COOKIES.get("key") != None:
        encryption_key = "f012c2a1c35e7952"
        encryptor = AESCipher(encryption_key)

        token = encryptor.decrypt(request.COOKIES.get("key")).decode("utf-8")

        current_user = Users.objects.filter(Mail=token)

        target_user_id = current_user.first().Mail




    week_dict = {"月":0,"火":1,"水":2,"木":3,"金":4}

    new_data = timetables()
    new_data.title = request.POST["title"]
    new_data.target_id = target_user_id
    new_data.level = 0
    new_data.room = "INIADホール"
    new_data.start_time = 0
    new_data.end_time = 0
    new_data.week = week_dict[request.POST['week']]
    new_data.time = int(request.POST['time'])
    new_data.quater = 0
    new_data.year = 2018
    new_data.teacher = request.POST["teacher"]

    new_data.start_time = 0

    new_data.save()

    return redirect("/")

def timeGet(time):
    JST = timezone(timedelta(hours=+9), 'JST')
    now_time = datetime.now(JST)
    today_oclock_time = datetime(now_time.year,now_time.month,now_time.day,0,0,0,0)
    distance_time = int(time.timestamp() - today_oclock_time.timestamp())
    return distance_time

timeGet(datetime(2018,12,17,16,15,00,00,tzinfo=timezone(timedelta(hours=+9), 'JST')))

def getTableData(request):
    encryption_key = "f012c2a1c35e7952"
    encryptor = AESCipher(encryption_key)

    try:
        encrypted_token = encryptor.decrypt(request.META["HTTP_AUTHORIZATION"]).decode("utf-8")
        print(encrypted_token)
        target_data = timetables.objects.filter(target_id=encrypted_token)
        if target_data == None:
            raise AttributeError
        else:
            json_response = {
                "status" : "accepted",
                "content" : json.loads(serializers.serialize("json", target_data)),
                "error_description" : None
            }

            return JsonResponse(json_response)
    except:
        json_response = {
            "status" : "error",
            "content" : None,
            "error_description" : "Dump Failed"
        }
        return JsonResponse(json_response)