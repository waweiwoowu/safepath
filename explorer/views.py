from django.contrib import auth
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from explorer.database import AttractionSQLController, RestaurantSQLController
from explorer.maps import Direction, DirectionAPI, Hotspot, Foodspot
from explorer.models import UserInfo
import json
import random


def index(request):
    if 'username' in request.session:
        user = request.session['username']
        return render(request, "index.html", {'user':user})

    return render(request, "index.html", {'user':"您尚未登入"})

def home(request):
    return redirect('/explorer/map')

def map(request):
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
            "image": f"/static/images/hotspots/{foodspots.image[i]}",
            "rating": foodspots.rating[i],
            "address": foodspots.address[i],
            "phone": foodspots.phone[i],
            "openhour": foodspots._opening_hours[i],
            "price": foodspots.avg_price[i]
        } for i in range(len(foodspots.data))]

        return JsonResponse({"attractions": attractions, "food_places": food_places}, safe=False)
    else:
        cities = []  # Assuming you have a list of cities to pass to the template
        return render(request, 'travel.html', {'cities': cities})

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
