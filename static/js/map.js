let map, directionsService, directionsRenderer;
// document.addEventListener('DOMContentLoaded', (event) => {
//     if (typeof google !== 'undefined') {
//         initMap();
//     }
// });
function initMap() {
    // let map, directionsService, directionsRenderer;
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

        // Clear previous results and show the loading message
        $('#display-info').html('');
        $('#display-info-traffic-accident').hide();
        $('#display-info-earthquake').hide();
        $('#display-info-earthquake-list').hide();
        $('#loading-message').html('Calculating risks, please wait...\nDon\'t refresh the screen!!!!!!!!!!!!').show();

        // Calculate and display the route and then send the AJAX request
        calculateAndDisplayRoute(start, destination);
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
            console.log('Collected Coordinates:', coordinates);

            // Ensure coordinates are being correctly converted to a JSON string
            const coordinatesString = JSON.stringify(coordinates);
            console.log('Coordinates JSON String:', coordinatesString);

            // Send coordinates to the server
            $.ajax({
                url: '',  // Ensure this URL points to the correct endpoint
                type: 'POST',
                data: {
                    start: start,
                    destination: destination,
                    coordinates: coordinatesString,
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    console.log('Server response:', response);  // Log server response
                    $('#display-info').html('');
                    $('#display-info-traffic-accident').html('');
                    $('#display-info-earthquake').html('');

                    if (response.traffic_accident_number) {
                        $('#display-info-traffic-accident').show();
                        $('#display-info-traffic-accident').append('<p>事故次數: ' + response.traffic_accident_number + ' 次</p>');
                    }
                    if (response.traffic_accident_fatality) {
                        $('#display-info-traffic-accident').append('<p>死亡人數: ' + response.traffic_accident_fatality + ' 人</p>');
                    }
                    if (response.traffic_accident_injury) {
                        $('#display-info-traffic-accident').append('<p>受傷人數: ' + response.traffic_accident_injury + ' 人</p>');
                    }
                    if (response.earthquake_number) {
                        $('#display-info-earthquake').show();
                        $('#display-info-earthquake').append('<p>地震次數: ' + response.earthquake_number + ' 次</p>');
                        $('#display-info-earthquake').append('<p>平均規模: ' + response.earthquake_average_magnitude + '</p>');
                        $('#display-info-earthquake').append('<p>平均深度: ' + response.earthquake_average_depth + ' 公里</p>');
                        $('#display-info-earthquake-list').show();
                        response.earthquake_data.forEach(data => {
                            $('#display-info-earthquake-list').append(
                                '<div class="earthquake-item">' +
                                '<p>Date: ' + data.date + '</p>' +
                                '<p>Coordinate: (' + data.coordinate[0] + ', ' + data.coordinate[1] + ')</p>' +
                                '<p>Magnitude: ' + data.magnitude + '</p>' +
                                '<p>Depth: ' + data.depth + '< km/p>' +
                                '</div>'
                            );
                        });
                    } else {
                        $('#display-info-earthquake').show();
                        $('#display-info-earthquake').append('<p>無地震紀錄</p>');
                    }

                    $('#loading-message').hide();
                },
                error: function(xhr, status, error) {
                    console.log('AJAX Error:', status, error);
                    console.log('Response:', xhr.responseText);
                    $('#loading-message').hide();
                    $('#display-info').html('<p>An error occurred while processing your request.</p>');
                }
            });
        } else {
            console.log('Directions request failed due to ' + status);
        }
    });
}

initMap();
