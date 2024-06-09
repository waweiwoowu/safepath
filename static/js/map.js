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

        // Clear previous results and show the loading message
        $('#display-info').html('');
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
