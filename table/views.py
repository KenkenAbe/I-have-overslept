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
    if request.COOKIES.get("key") == None:
        return redirect("/login")

    user_id = base64.b64decode(request.COOKIES.get("key") + '=' * (-len(request.COOKIES.get("key")) % 4)).decode("utf-8")
    params = {"user_id":user_id}
    return render(request, 'timetable.html',params)

def setting(request):
    """時間割画面"""
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
        print(token)
        response.set_cookie("key",token.decode("utf-8"))

        print(user_info)
        return response

    return redirect("/")


    return render(request, 'timetable.html')