from django.shortcuts import render,redirect,HttpResponse
import urllib.request as http_request
import urllib
import json
import requests
import base64
from table.models import timetables
from datetime import datetime, timedelta, timezone

# Create your views here.
def table(request):
    """時間割画面"""
    lesson = "未登録"
    if request.COOKIES.get("key") == None:
        user_id = ""
    else:
        user_id = base64.b64decode(request.COOKIES.get("key") + '=' * (-len(request.COOKIES.get("key")) % 4)).decode(
            "utf-8")
        if timetables.objects.all() != None:
            lesson = timetables.objects.all()
             
    params = {"user_id":user_id, "lesson":lesson}
    return render(request, 'timetable.html',params)


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
        print(splited_id_token)
        raw_info = json.loads(base64.urlsafe_b64decode(splited_id_token + '=' * (-len(splited_id_token) % 4)).decode("utf-8"))

        """ここから登録処理を作る"""

        url = "https://www.googleapis.com/oauth2/v1/userinfo"

        params = {
            "access_token": result["access_token"]
        }

        user_info_response = requests.get(url,urllib.parse.urlencode(params))
        user_info = json.loads(user_info_response.text)

        response = redirect("/")
        token = base64.b64encode(bytes(user_info["name"], 'utf-8'))

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

    week_dict = {"月":0,"火":1,"水":2,"木":3,"金":4}

    new_data = timetables()
    new_data.title = request.POST["title"]
    new_data.target_id = "hogehoge"
    new_data.level = 0
    new_data.room = "INIADホール"
    new_data.start_time = 0
    new_data.end_time = 0
    new_data.week = week_dict[request.POST['week']]
    new_data.time = int(request.POST['time'])
    new_data.quater = 0
    new_data.year = 2018
    new_data.teacher = "淺野 智之"

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