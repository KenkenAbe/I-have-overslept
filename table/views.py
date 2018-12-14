from django.shortcuts import render,redirect

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