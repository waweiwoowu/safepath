let map, directionsService, directionsRenderer;
// console.log("aaa");
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