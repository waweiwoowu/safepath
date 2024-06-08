from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import UserInfo
from django.core.mail import send_mail
from asgiref.sync import sync_to_async
import random
from .maps import Direction, DirectionAPI
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth

def index(request):
    if 'username' in request.session:
        user = request.session['username']
        return render(request, "index.html", {'user':user})

    return render(request, "index.html", {'user':"您尚未登入"})


def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {})
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect('/explorer//')
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
            request.session['username'] = username
            return redirect('/explorer//')
        else:
            return redirect('/explorer/signin/')

def logout(request):
    if 'username' in request.session:
        del request.session['username']
        return render(request, "index.html", {"user":"您已登出!!"})
    return render(request, "index.html", {"user":"您尚未登入!!"})

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

@csrf_exempt
def travel(request):
    attractions = []
    food_places = []
    if request.method == 'POST':
        city = request.POST.get('city')
        area = request.POST.get('area')
        print("--> " + city + " <--")
        # print(area)
        # return HttpResponse(str(city))
        # if city == "臺北市" and area == "文山區":
        attractions = [
            {
                'title': '台北小巨蛋',
                'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ8WoAAe2RE9lmNkIsPButFnegYyjwmTWZFbw&s',
                'address': '地址A',
                'phone': '電話A',
            },
            {
                'title': '木柵動物園',
                'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ8WoAAe2RE9lmNkIsPButFnegYyjwmTWZFbw&s',
                'address': '地址B',
                'phone': '電話B',
            }
        ]
        food_places = [
            {
                'title': '梅子鰻蒲燒屋日本料理',
                'image': 'https://media.istockphoto.com/id/483120255/zh/照片/asian-oranage-chicken-with-green-onions.jpg?s=612x612&w=0&k=20&c=MujdLI69HjK4hSVFmpfQXHynGDHT2XOBOPSigQKcnyo=',
                'rating': '5星',
                'address': '地址B',
                'phone': '電話B',
                'openhour': '星期一 11:30-23:00',
                'price':'800-1000'
            },
            {
                'title': '紫艷中餐廳',
                'image': 'https://media.istockphoto.com/id/483120255/zh/照片/asian-oranage-chicken-with-green-onions.jpg?s=612x612&w=0&k=20&c=MujdLI69HjK4hSVFmpfQXHynGDHT2XOBOPSigQKcnyo=',
                'rating': '4星',
                'address': '地址B',
                'phone': '電話B',
                'openhour': '星期一 11:30-23:00',
                'price':'400-500'
            }
        ]

        return JsonResponse({"attractions": attractions, "food_places": food_places}, safe=False)
    else:

        return render(request, 'travel.html')

def travel_map(request):
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')
    waypoints = request.GET.get('waypoints', '')

    context = {
        'start': start,
        'end': end,
        'waypoints': waypoints.split('|') if waypoints else []
    }

    return render(request, 'travel_map.html', context)

import json

def home(request):
    if request.method == 'POST':
        start = request.POST.get('start', '')
        destination = request.POST.get('destination', '')
        coordinates = request.POST.get('coordinates', '')

        try:
            if not coordinates:
                raise ValueError('No coordinates provided')
            coordinates = json.loads(coordinates)
            print('Parsed coordinates:', coordinates)
        except (json.JSONDecodeError, ValueError) as e:
            print('Error:', str(e))
            return JsonResponse({'error': 'Invalid coordinates format or no coordinates provided'}, status=400)

        direction = Direction(coordinates)
        # direction = DirectionAPI()
        # direction = DirectionAPI(origin=start, destination=destination) # This will spend googlemaps api quotas

        # coordinates = direction.coordinates

        fatality = direction.traffic_accident.total_fatality
        if fatality == 0:
            fatality = "無死亡"
        injury = direction.traffic_accident.total_injury
        if injury == 0:
            injury = "無受傷"

        magnitude = direction.earthquake.magnitude
        if magnitude is None:
            magnitude = "無地震"
        else:
            magnitude = direction.earthquake.magnitude[0]

        # return render(request, 'home.html', {
        #     'start': start,
        #     'destination': destination,
        #     'coordinates': coordinates,
        #     'fatality': fatality,
        #     'injury': injury
        # })
        return JsonResponse({
        'fatality': fatality,
        'injury': injury,
        'magnitude': magnitude
    })
    else:
        return render(request, 'home.html', {})


# def home(request):
#     if request.method == 'POST':
#         start = request.POST.get('start', '')
#         destination = request.POST.get('destination', '')
#         coordinates = request.POST.get('coordinates', '')

#         print('Received start:', start)
#         print('Received destination:', destination)
#         print('Received coordinates:', coordinates)

#         try:
#             coordinates = json.loads(coordinates)
#             print('Parsed coordinates:', coordinates)
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid coordinates format'}, status=400)

#         # direction = DirectionAPI()
#         # direction = DirectionAPI(origin=start, destination=destination) # This will spend googlemaps api quotas
#         direction = Direction(coordinates)

#         # coordinates = direction.coordinates
#         # fatality = await direction.traffic_accident.total_fatality
#         # injury = await direction.traffic_accident.total_injury
#         fatality = direction.traffic_accident.total_fatality
#         if fatality == 0:
#             fatality = "無死亡"
#         injury = direction.traffic_accident.total_injury
#         if injury == 0:
#             injury = "無受傷"

#         magnitude = direction.earthquake.magnitude
#         if magnitude is None:
#             magnitude = "無地震"
#         else:
#             magnitude = direction.earthquake.magnitude[0]

#         # return render(request, 'home.html', {
#         #     'start': start,
#         #     'destination': destination,
#         #     'coordinates': coordinates,
#         #     'fatality': fatality,
#         #     'injury': injury
#         # })
#         return JsonResponse({
#         'fatality': fatality,
#         'injury': injury,
#         'magnitude': magnitude
#         # 'magnitude': coordinates
#     })
#     else:
#         return render(request, 'home.html', {})

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



