from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
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

# def travel(request):
#     if request.method == 'POST':
#         location = request.POST.get('location')
#         area = request.POST.get('area')

#         return render(request, 'travel.html')
#     else:
#         return render(request, 'travel.html')

def travel(request):
    return render(request, 'travel.html')


async def home(request):
    if request.method == 'POST':
        start = request.POST.get('start', '')
        destination = request.POST.get('destination', '')

        # Assuming `Direction` class methods are synchronous
        direction = Direction()
        # or Direction(start, destination) if you need to pass arguments
        # direction = Direction(origin=start, destination=destination)

        # coordinates = direction.coordinates
        # fatality = await direction.traffic_accident.total_fatality
        # injury = await direction.traffic_accident.total_injury
        fatality = direction.traffic_accident.total_fatality
        if fatality == 0:
            fatality = "無死亡"
        injury = direction.traffic_accident.total_injury
        if injury == 0:
            injury = "無受傷"

        # return render(request, 'home.html', {
        #     'start': start,
        #     'destination': destination,
        #     'coordinates': coordinates,
        #     'fatality': fatality,
        #     'injury': injury
        # })
        return JsonResponse({
        'fatality': fatality,
        'injury': injury
    })
    else:
        return render(request, 'home.html', {})

# from django.http import JsonResponse
# import json

# def home(request):
#     if request.method == 'POST' and request.is_ajax():
#         data = json.loads(request.body)
#         start = data.get('start')
#         destination = data.get('destination')

#         # Do whatever processing you need with start and destination here
#         # For example, you can pass them to Direction class and get coordinates

#         coordinates = []  # Assuming you get coordinates somehow
#         return JsonResponse({
#             'start': start,
#             'destination': destination,
#             'coordinates': coordinates
#         })
#     else:
#         return render(request, 'home.html', {})



