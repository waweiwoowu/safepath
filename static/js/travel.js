$(document).ready(function() {
    var selectedLocations = [];

    // Fetch and populate the city dropdown
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
            alert("Failed to load city data.");
        }
    });

    // Populate the area dropdown based on the selected city
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

    // Form submission to get recommended locations
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
                    var disabled = isLocationSelected(attraction.title) ? 'disabled' : '';
                    attractionsHtml += '<div class="grid-item">';
                    attractionsHtml += '<img src="' + attraction.image + '" alt="' + attraction.title + '" style="width:100%">';
                    attractionsHtml += '<div class="data"><h3>' + attraction.title + '</h3>';
                    attractionsHtml += '<p>' + attraction.address + '</p></div>';
                    // David add address parameter
                    attractionsHtml += '<button class="select" onclick="addToRoute(\'hotspot\', \'' + attraction.title + '\', \'' + attraction.address + '\')" ' + disabled + '>select</button>';
                    attractionsHtml += '</div>';
                });

                $.each(response.food_places, function(index, food_place) {
                    var disabled = isLocationSelected(food_place.title) ? 'disabled' : '';
                    foodPlacesHtml += '<div class="grid-item">';
                    foodPlacesHtml += '<img src="' + food_place.image + '" alt="' + food_place.title + '" style="width:100%">';
                    foodPlacesHtml += '<div class="data"><h3>' + food_place.title + '</h3>';
                    foodPlacesHtml += '<p>Rating: ' + food_place.rating + '</p>';
                    foodPlacesHtml += '<p>Address: ' + food_place.address + '</p>';
                    foodPlacesHtml += '<p>Phone: ' + food_place.phone + '</p>';
                    // foodPlacesHtml += '<p>Open Hours: ' + food_place.openhour + '</p>';
                    foodPlacesHtml += '<p>Average Price: ' + food_place.price + '</p></div>';
                    // David add address parameter
                    foodPlacesHtml += '<button class="select" onclick="addToRoute(\'foodspot\', \'' + food_place.title + '\', \'' + food_place.address + '\')" ' + disabled + '>select</button>';
                    foodPlacesHtml += '</div>';
                });

                $('#hotspotContainer').html(attractionsHtml);
                $('#foodspotContainer').html(foodPlacesHtml);
            },
            error: function() {
                alert("Failed to get recommendations.");
            }
        });
    });

    window.addToRoute = function(type, title, addr) { // David add attr attribute
        if (selectedLocations.length >= 5) {
            alert("You can only select up to 5 locations.");
            return;
        }

        selectedLocations.push({ type: type, title: title, addr: addr }); // David add attr attribute
        updateSelectedLocations();
        updateDisabledButtons();
    };

    window.removeFromRoute = function(index) {
        selectedLocations.splice(index, 1);
        updateSelectedLocations();
        updateDisabledButtons();
    };

    function updateSelectedLocations() {
        var selectedHtml = '';
        $.each(selectedLocations, function(index, item) {
            selectedHtml += '<div class="grid-item selected-item">';
            selectedHtml += '<span>' + item.title + '</span>';
            selectedHtml += '<span style="display: nonex">' + item.addr + '</span>'; // David add attr attribute
            selectedHtml += '<button class="cancel" onclick="removeFromRoute(' + index + ')">cancel</button>';
            selectedHtml += '</div>';
        });
        $('#selectedContainer').html(selectedHtml);
    }

    function updateDisabledButtons() {
        $('.select').each(function() {
            var title = $(this).siblings('.data').find('h3').text();
            if (isLocationSelected(title)) {
                $(this).attr('disabled', 'disabled');
            } else {
                $(this).removeAttr('disabled');
            }
        });
    }

    function isLocationSelected(title) {
        return selectedLocations.some(function(location) {
            return location.title === title;
        });
    }

    // 規劃路線按鈕
    $('#planRouteButton').click(function() {
        var startPoint = $('#Start_Point').val();
        var destination = $('#Destination').val();

        // alert("startPoint: \n" + startPoint + "\n" + "destination: " + destination)
        // var selectedTitles = selectedLocations.map(function(item) { return item.title; });
        var selectedAddress = selectedLocations.map(function(item) { return item.addr; });
        // alert("selectedTitles: \n" + selectedTitles)
        var waypoints = selectedAddress.join('|');
        // alert("waypoints: \n" + waypoints)
        // alert("start: " + encodeURIComponent(startPoint))
        var url = '/explorer/travel_map/?start=' + encodeURIComponent(startPoint) + '&end=' + encodeURIComponent(destination) + '&waypoints=' + encodeURIComponent(waypoints) + '&optimize_waypoints=True';
        // alert("url: \n" + url)
        // window.location.href = url; // 直接跳轉
        window.open(url, '_blank'); // 在新分頁中打開 URL
    });
});
