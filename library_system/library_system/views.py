from django.shortcuts import render

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/accounts/login/')
def home(request):
    user = request.user
    
    if user.is_staff:
        return redirect('/manager/home/')
    else:
        return redirect('/borrower/home/')
def home_page(request):
    return render(request, "home.html")