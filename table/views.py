from django.shortcuts import render,redirect
import urllib.request as http_request
import urllib
import json
import requests
import base64

# Create your views here.
def table(request):
    """時間割画面"""
    return render(request, 'timetable.html')

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
        user_info = json.loads(base64.urlsafe_b64decode(splited_id_token + '=' * (-len(splited_id_token) % 4)).decode("utf-8"))

        """ここから登録処理を作る"""

        print(user_info)


    return render(request, 'timetable.html')