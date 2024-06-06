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
    $("form").submit(function(event){
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
            },
            error: function(){
                alert("fail");
            }
        });
    });
});