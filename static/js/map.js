// let map, directionsService, directionsRenderer;     // 自定義的全域變數用於 地圖 服務 渲染

// //此版本 前端 console 可印出座標
// function initMap() {
//     // 初始化 google maps API: 設定中心 縮放尺度
//     map = new google.maps.Map(document.getElementById('map'), {
//         center: { lat: 23.83876, lng: 120.9876 },
//         zoom: 8
//     });

//     // 實體化 google API (DirectionsService)
//     directionsService = new google.maps.DirectionsService();
//     // 實體化 google API (DirectionsRenderer)
//     directionsRenderer = new google.maps.DirectionsRenderer();
//     // DirectionsRenderer 與地圖綁定
//     directionsRenderer.setMap(map);

//     // JavaScript 等待第一個 form submit 觸發執行 calculateAndDisplayRoute()
//     document.querySelector('form').addEventListener('submit', function(event) {
//         event.preventDefault();
//         calculateAndDisplayRoute();
//     });
// }

// // 計算起點終點
// function calculateAndDisplayRoute() {
//     // 取得輸入的值 起點 終點
//     const start = document.getElementById('start').value;
//     const destination = document.getElementById('destination').value;

//     // google maps API (DirectionsService) 計算路線
//     directionsService.route({
//         origin: start,
//         destination: destination,
//         travelMode: google.maps.TravelMode.DRIVING
//     }, function(response, status) {
//         if (status === google.maps.DirectionsStatus.OK) {
//             directionsRenderer.setDirections(response);

//             // 取得所有必經路線的座標點
//             const route = response.routes[0];
//             const coordinates = [];
//             route.legs.forEach(leg => {
//                 leg.steps.forEach(step => {
//                     step.path.forEach(latlng => {
//                         coordinates.push({
//                             lat: latlng.lat(),
//                             lng: latlng.lng()
//                         });
//                     });
//                 });
//             });
//             console.log(coordinates);  // 肥包子 20240603 增加，這裡會輸出所有的座標點

//         } else {
//             // 錯誤訊息
//             console.log('Directions request failed due to ' + status);
//         }
//     });
// }
// // 避免地圖初始化失敗 (Bug 處理中 目前為替代作法: 補呼叫一次初始化)
// initMap();


/*
//下方為原版 JavaScript 保存在 maps_origin.js 內
console.log("aaa");
function initMap() {
    // console.log("initMap1");
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 23.83876, lng: 120.9876 },
        zoom: 8
    });
    // console.log("initMap2");
    directionsService = new google.maps.DirectionsService();
    // console.log("initMap3");
    directionsRenderer = new google.maps.DirectionsRenderer();
    // console.log("initMap4");
    directionsRenderer.setMap(map);
    // console.log("initMap5");
    document.querySelector('form').addEventListener('submit', function(event) {
        event.preventDefault();
        calculateAndDisplayRoute();
    });
}


// console.log("bbb");
function calculateAndDisplayRoute() {
    // console.log("calculateAndDisplayRoute1");
    const start = document.getElementById('start').value;
    const destination = document.getElementById('destination').value;

    directionsService.route({
        origin: start,
        destination: destination,
        travelMode: google.maps.TravelMode.DRIVING
    }, function(response, status) {
        // console.log("calculateAndDisplayRoute2");
        if (status === google.maps.DirectionsStatus.OK) {
            // console.log("calculateAndDisplayRoute3");
            directionsRenderer.setDirections(response);
            // console.log("calculateAndDisplayRoute4");
        } else {
            // console.log("calculateAndDisplayRoute5");
            console.log('Directions request failed due to ' + status);
            // console.log("calculateAndDisplayRoute6");
        }
    });
}
initMap();
*/

let map, directionsService, directionsRenderer;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 23.83876, lng: 120.9876 },
        zoom: 8
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);

    $('#route-form').on('submit', function(event) {
        event.preventDefault();
        const start = $('#start').val();
        const destination = $('#destination').val();

        // Perform AJAX form submission
        $.ajax({
            url: '',
            type: 'POST',
            data: {
                start: start,
                destination: destination,
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                $('#display-info').html('');

                if (start) {
                    $('#display-info').append('<p>Start: ' + start + '</p>');
                }
                if (destination) {
                    $('#display-info').append('<p>Destination: ' + destination + '</p>');
                }
                if (response.fatality) {
                    $('#display-info').append('<p>Fatality: ' + response.fatality + '</p>');
                }
                if (response.injury) {
                    $('#display-info').append('<p>Injury: ' + response.injury + '</p>');
                }
                if (response.magnitude) {
                    $('#display-info').append('<p>Magnitude: ' + response.magnitude + '</p>');
                }
                // Calculate and display the route
                calculateAndDisplayRoute(start, destination);
            }
        });
    });
}

function calculateAndDisplayRoute(start, destination) {
    directionsService.route({
        origin: start,
        destination: destination,
        travelMode: google.maps.TravelMode.DRIVING
    }, function(response, status) {
        if (status === google.maps.DirectionsStatus.OK) {
            directionsRenderer.setDirections(response);
            const route = response.routes[0];
            const coordinates = [];
            route.legs.forEach(leg => {
                leg.steps.forEach(step => {
                    step.path.forEach(latlng => {
                        coordinates.push({
                            lat: latlng.lat(),
                            lng: latlng.lng()
                        });
                    });
                });
            });
            console.log(coordinates);
        } else {
            console.log('Directions request failed due to ' + status);
        }
    });
}

initMap();