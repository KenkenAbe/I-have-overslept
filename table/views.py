from django.shortcuts import render

# Create your views here.
def table(request):
    """時間割画面"""
    return render(request, 'timetable.html')

def setting(request):
    """時間割画面"""
    return render(request, 'setting.html')