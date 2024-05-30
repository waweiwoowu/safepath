from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UserInfo
from django.core.mail import send_mail
from asgiref.sync import sync_to_async
import random
from .maps import Direction

def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {})
    else:
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            return render(request, "signin.html", {"error": "Username and password are required."})

        try:
            user = UserInfo.objects.get(username=username)
        except UserInfo.DoesNotExist:
            # Username does not exist
            return render(request, "signin.html", {"error": "Invalid username or password."})

        if user.password == password:
            return redirect('/explorer/home/')
        else:
            return redirect('/explorer/signin/')

def signup(request):
    if request.method == "GET":
        return render(request, "signup.html", {})
    else:
        username = request.POST.get("username")
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        verification_code = verification_code_generator()

        user_info = UserInfo(
            username = username,
            fullname = fullname,
            email = email,
            password = password,
            verification_code = verification_code
        )

        user_info.save()

        send_mail(f"Verify", f"hello {username},\nYour verification code is {verification_code}", "f37854979@gmail.com", [email])

        return render(request, "verification_code.html", {"username": username})

def verification_code_generator():
    code = ""
    for _ in range(16):
        num = str(random.randint(0, 9))
        code += num
    return code

def verify(request):
    if request.method == "POST":
        username = request.POST.get("username")
        verification_code = request.POST.get("verification_code")

        try:
            user = UserInfo.objects.get(username=username, verification_code=verification_code)
            user.verification_code = True
            user.save()
            return redirect('signin')
        except:
            return HttpResponse("Failed")

async def home(request):
    if request.method == 'POST':
        start = request.POST.get('start', '')
        destination = request.POST.get('destination', '')

        # Assuming `Direction` class methods are synchronous
        direction = Direction()
        # or Direction(start, destination) if you need to pass arguments
        # direction = Direction(origin=start, destination=destination)

        coordinates = direction.coordinates
        # fatality = await direction.car_accident.fatality
        # injury = await direction.car_accident.injury

        return render(request, 'home.html', {
            'start': start,
            'destination': destination,
            'coordinates': coordinates
        })
    else:
        return render(request, 'home.html', {})


