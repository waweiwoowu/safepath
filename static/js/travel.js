$(document).ready(function() {
    $.ajax({
        url: '/static/json/travel.json',
        type: "get",
        dataType: "json",
        success: function (data) {
            $('#city').empty().append('<option value="">選擇城市</option>');
            $.each(data, function(key, value) {
                $('#city').append('<option value="'+value.CityName+'">'+value.CityName+'</option>');
            });
            window.cityData = data;
        },
        error: function (data) {
            alert("fail");
        }
    });

    $("#city").change(function() {
        var cityValue = $("#city").val();
        $("#area").empty().css("display", "inline").append('<option value="">選擇鄉鎮</option>');
        $.each(window.cityData, function(key, value) {
            if (value.CityName === cityValue) {
                $.each(value.AreaList, function(index, area) {
                    $('#area').append('<option value="'+area.AreaName+'">'+area.AreaName+'</option>');
                });
            }
        });
    });

    $("#recommendform").submit(function(event) {
        event.preventDefault();
        var cityValue = $("#city").val();
        var areaValue = $("#area").val();
        var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();

        $.ajax({
            url: '{% url "travel" %}',
            type: "POST",
            data: {
                'city': cityValue,
                'area': areaValue,
                'csrfmiddlewaretoken': csrftoken
            },
            dataType: 'json',
            success: function(response) {
                var attractionsHtml = '';
                var foodPlacesHtml = '';

                $.each(response.attractions, function(index, attraction) {
                    attractionsHtml += '<div class="grid-item">';
                    attractionsHtml += '<img src="' + attraction.image + '" alt="' + attraction.title + '" style="width:100%">';
                    attractionsHtml += '<div class="data"><h3>' + attraction.title + '</h3>';
                    attractionsHtml += '<p>' + attraction.address + '</p></div>';
                    attractionsHtml += '<button class="select" onclick="addToRoute(\'hotspot\', \'' + attraction.title + '\')">select</button>';
                    attractionsHtml += '</div>';
                });

                $.each(response.food_places, function(index, food_place) {
                    foodPlacesHtml += '<div class="grid-item">';
                    foodPlacesHtml += '<img src="' + food_place.image + '" alt="' + food_place.title + '" style="width:100%">';
                    foodPlacesHtml += '<div class="data"><h3>' + food_place.title + '</h3>';
                    foodPlacesHtml += '<p>Rating: ' + food_place.rating + '</p>';
                    foodPlacesHtml += '<p>Address: ' + food_place.address + '</p>';
                    foodPlacesHtml += '<p>Phone: ' + food_place.phone + '</p>';
                    foodPlacesHtml += '<p>Open Hours: ' + food_place.openhour + '</p>';
                    foodPlacesHtml += '<p>Average Price: ' + food_place.price + '</p></div>';
                    foodPlacesHtml += '<button class="select" onclick="addToRoute(\'foodspot\', \'' + food_place.title + '\')">select</button>';
                    foodPlacesHtml += '</div>';
                });

                $('#hotspotContainer').html(attractionsHtml);
                $('#foodspotContainer').html(foodPlacesHtml);
            },
            error: function() {
                alert("fail");
            }
        });
    });

    window.addToRoute = function(type, title) {
        var selectedItems = [];
        var startPoint = $('#Start_Point').val();
        var destination = $('#Destination').val();

        if (type === 'hotspot') {
            $('.hotSpot:checked').each(function() {
                selectedItems.push($(this).data('title'));
            });
        } else if (type === 'foodspot') {
            $('.foodPlace:checked').each(function() {
                selectedItems.push($(this).data('title'));
            });
        }

        selectedItems.push(title);

        var routeHtml = '<p>' + startPoint + ' --- ';
        $.each(selectedItems, function(index, item) {
            routeHtml += item + ' --- ';
        });

        $('#routeContainer').html(routeHtml + destination + '</p>');
    };

    $('#planRouteButton').click(function() {
        var selectedItems = [];
        var startPoint = $('#Start_Point').val();
        var destination = $('#Destination').val();
        // var startPoint = "台北車站"
        // var destination = "中正紀念堂"
        alert(" =========== aaa =========== ")
        $('.hotSpot:checked').each(function() {
            alert("bbb")
            selectedItems.push($(this).data('title'));
        });

        $('.foodPlace:checked').each(function() {
            alert(" =========== ccc =========== ")
            selectedItems.push($(this).data('title'));
        });
        alert(" =========== ddd =========== ")
        var waypoints = selectedItems.join('|');
        var url = '/explorer/travel_map/?start=' + encodeURIComponent(startPoint) + '&end=' + encodeURIComponent(destination) + '&waypoints=' + encodeURIComponent(waypoints);
        window.location.href = url;
    });
});
