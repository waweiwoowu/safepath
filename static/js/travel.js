$(document).ready(function(){
    // Load city data into the first dropdown
    $.ajax({
        url: 'https://raw.githubusercontent.com/donma/TaiwanAddressCityAreaRoadChineseEnglishJSON/master/CityCountyData.json',
        type: "get",
        dataType: "json",
        success: function (data) {
            console.log(data);
            $.each(data, function(key, value){
                console.log(key, value);
                $('#city').append('<option value="'+key+'">'+data[key].CityName+'</option>');
            });
        },
        error: function (data) {
            alert("fail");
        }
    });

    // Load area data based on the selected city
    $("#city").change(function(){
        var cityValue = $("#city").val();  // Get selected city value
        $("#area").empty(); // Clear previous values
        $("#area").css("display", "inline"); // Show area dropdown
        $("#area").append('<option value="">選擇鄉鎮</option>'); // Add default option

        $.ajax({
            url: 'https://raw.githubusercontent.com/donma/TaiwanAddressCityAreaRoadChineseEnglishJSON/master/CityCountyData.json',
            type: "get",
            dataType: "json",
            success: function(data){
                var eachVal = data[cityValue].AreaList; // Get areas for selected city
                $.each(eachVal, function(key, value){
                    $('#area').append('<option value="'+key+'">'+eachVal[key].AreaName+'</option>');
                });
            },
            error: function(){
                alert("fail");
            }
        });
    });

    // Handle form submission
    $("#recommendfrom").submit(function(event){
        event.preventDefault(); // Prevent the form from submitting the traditional way
        var cityValue = $("#city").val();  // Get selected city value
        var areaValue = $("#area").val();  // Get selected area value

        $.ajax({
            url: 'https://raw.githubusercontent.com/donma/TaiwanAddressCityAreaRoadChineseEnglishJSON/master/CityCountyData.json',
            type: "get",
            dataType: "json",
            success: function(data){
                var cityName = data[cityValue].CityName;
                var areaName = data[cityValue].AreaList[areaValue].AreaName;
                $('#result').text(cityName + " - " + areaName);
                $('#result')
            },
            error: function(){
                alert("fail");
            }
        });
    });


    // Handle form submission
    $("#recommendfrom").submit(function(event){
        event.preventDefault(); // Prevent the form from submitting the traditional way
        var cityValue = $("#city").val();  // Get selected city value
        var areaValue = $("#area").val();  // Get selected area value
        var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();  // Get CSRF token
        console.log(csrftoken)
        $.ajax({
            url: '{% url "travel" %}',
            type: "POST",
            data: {
                'city': cityValue,
                'area': areaValue,
                'csrfmiddlewaretoken': csrftoken
            },
            dataType: 'json',
            success: function(response){
                var attractionsHtml='';
                var foodPlacesHtml='';

                $.each(response.attractions, function(index, attraction){
                    attractionsHtml += '<div class="result">';
                    attractionsHtml += '<input type="checkbox" id="hotSpot_' + index + '" name="hotSpot_' + index + '">';
                    attractionsHtml += '<label for="hotSpot_' + index + '">' + attraction.title + '</label><br>';
                    attractionsHtml += '<h3>'+ attraction.title + '</h3>';
                    attractionsHtml += '<img src="' + attraction.image +'" alt="' + attraction.title + '">';
                    attractionsHtml += '<p>地址:' + attraction.address + '</p>'
                    attractionsHtml += '<p>電話:'+ attraction.phone + '</p>'
                    attractionsHtml += '</div>';
                });
                $.each(response.food_places, function(index, food_place){
                    foodPlacesHtml += '<div class="result">';
                    foodPlacesHtml += '<input type="checkbox" id="food_' + index + '" name="food_' + index + '">';
                    foodPlacesHtml += '<label for="food_' + index + '">' + food_place.title + '</label><br>';
                    foodPlacesHtml += '<h3>'+ food_place.title + '<h3>';
                    foodPlacesHtml += '<img src="' + food_place.image + '" alt="' + food_place.title + '">';
                    foodPlacesHtml += '<p>評價: ' + food_place.rating + '</p>';
                    foodPlacesHtml += '<p>地址: ' + food_place.address + '</p>';
                    foodPlacesHtml += '<p>電話: ' + food_place.phone + '</p>';
                    foodPlacesHtml += '<p>營業時間: ' + food_place.openhour + '</p>';
                    foodPlacesHtml += '<p>平均消費: ' + food_place.price + '</p>';
                    foodPlacesHtml += '</div>';
                })

                $('.Recommend_spot .columnatrraction').html('<h3>景點資訊</h3>'+ attractionsHtml);
                $('.Recommend_food .columfood').html('<h3>美食資訊</h3>'+ foodPlacesHtml);

            },
            error: function(){
                alert("fail");

            },
    });
});
});