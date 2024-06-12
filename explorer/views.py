from django.contrib import auth
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from explorer.database import AttractionSQLController, RestaurantSQLController
from explorer.maps import Direction, DirectionAPI, Hotspot, Foodspot, _get_google_maps_api_key
from explorer.models import UserInfo
import json
import random
from django.db import IntegrityError


def index(request):
    if 'username' in request.session:
        user = request.session['username']
        return render(request, "index.html", {'user':user})

    return render(request, "index.html", {'user':"您尚未登入"})

def home(request):
    return redirect('/explorer/index')

def map(request):
    if request.method == 'POST':
        start = request.POST.get('start', '')
        destination = request.POST.get('destination', '')
        coordinates = request.POST.get('coordinates', '')

        try:
            if not coordinates:
                raise ValueError('No coordinates provided')
            coordinates = json.loads(coordinates)
            # print('Parsed coordinates:', coordinates)
        except (json.JSONDecodeError, ValueError) as e:
            print('Error:', str(e))
            return JsonResponse({'error': 'Invalid coordinates format or no coordinates provided'}, status=400)

        direction = Direction(coordinates)

        traffic_accident_number = direction.traffic_accident.number
        traffic_accident_fatality = direction.traffic_accident.total_fatality
        traffic_accident_injury = direction.traffic_accident.total_injury

        if direction.earthquake.data:
            earthquake_number = direction.earthquake.number
            earthquake_average_magnitude = f"{direction.earthquake.average_magnitude:.2f}"
            earthquake_average_depth = f"{direction.earthquake.average_depth:.1f}"
        else:
            earthquake_number = 0
            earthquake_average_magnitude = None
            earthquake_average_depth = None
        earthquake_data = [{
            "date": direction.earthquake.date[i],
            "coordinate": direction.earthquake.coordinate[i],
            "magnitude": direction.earthquake.magnitude[i],
            "depth": direction.earthquake.depth[i],
            "date": direction.earthquake.date[i],
            "date": direction.earthquake.date[i],
        } for i in range(earthquake_number)]

        return JsonResponse({
            "traffic_accident_number": traffic_accident_number,
            "traffic_accident_fatality": traffic_accident_fatality,
            "traffic_accident_injury": traffic_accident_injury,
            "earthquake_number": earthquake_number,
            "earthquake_average_magnitude": earthquake_average_magnitude,
            "earthquake_average_depth": earthquake_average_depth,
            "earthquake_data": earthquake_data
    })
    else:
        return render(request, 'map.html', {})

@csrf_exempt
def travel(request):
    if request.method == 'POST':
        area_1 = request.POST.get('city')
        area_2 = request.POST.get('area')

        hotspots = Hotspot(area_1=area_1, area_2=area_2)
        foodspots = Foodspot(area_1=area_1, area_2=area_2)

        attractions = [{
            "title": hotspots.name[i],
            "image": f"/static/images/hotspots/{hotspots.image[i]}",
            "address": hotspots.address[i]
        } for i in range(len(hotspots.data))]

        food_places = [{
            "title": foodspots.name[i],
            "image": f"/static/images/foodspots/{foodspots.image[i]}",
            "rating": foodspots.rating[i],
            "address": foodspots.address[i],
            "phone": foodspots.phone[i],
            "openhour": foodspots._opening_hours[i],
            "price": foodspots.avg_price[i]
        } for i in range(len(foodspots.data))]

        return JsonResponse({"attractions": attractions, "food_places": food_places}, safe=False)
    else:
        cities = []  # Assuming you have a list of cities to pass to the template
        start = request.GET.get('start')
        destination = request.GET.get('destination')
        if start and destination:
            return render(request, 'travel.html', {'cities': cities, 'start': start, 'destination': destination})
        else:
            return render(request, 'travel.html', {'cities': cities})


def travel_map(request):
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')
    waypoints = request.GET.get('waypoints', '')
    api_key = _get_google_maps_api_key()

    context = {
        'start': start,
        'end': end,
        'waypoints': waypoints.split('|') if waypoints else [],
        'api_key': api_key
    }

    return render(request, 'travel_map.html', context)

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

        if not username or not fullname or not email or not password:
            return render(request, "signup.html", {"error": "All fields are required."})

        if UserInfo.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already taken."})
        if UserInfo.objects.filter(email=email).exists():
            return render(request, "signup.html", {"error": "Email already registered."})

        verification_code = verification_code_generator()

        try:
            # 創建新用戶
            user_info = UserInfo(
                username=username,
                fullname=fullname,
                email=email,
                password=password,
                verification_code=verification_code
            )
            user_info.save()

        except IntegrityError:
            return render(request, "signup.html", {"error": "Error creating user. Please try again."})

        # 發送驗證電子郵件
        try:
            send_mail(
                "Verify",
                f"Hello {username},\nYour verification code is {verification_code}",
                "f37854979@gmail.com",
                [email]
            )
        except Exception as e:
            user_info.delete()
            return render(request, "signup.html", {"error": "Error sending verification email. Please try again."})

        return render(request, "verification_code.html", {"username": username})
# def signup(request):
#     if request.method == "GET":
#         return render(request, "signup.html", {})
#     else:
#         username = request.POST.get("username")
#         fullname = request.POST.get("fullname")
#         email = request.POST.get("email")
#         password = request.POST.get("password")
#         verification_code = verification_code_generator()

#         user_info = UserInfo(
#             username = username,
#             fullname = fullname,
#             email = email,
#             password = password,
#             verification_code = verification_code
#         )

#         user_info.save()

#         send_mail(f"Verify", f"hello {username},\nYour verification code is {verification_code}", "f37854979@gmail.com", [email])

#         return render(request, "verification_code.html", {"username": username})

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
