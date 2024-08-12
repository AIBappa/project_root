let map; // Declare map globally
let nearbyCitiesGeoJSONLayer; // Declare nearbyCitiesGeoJSONLayer globally

document.addEventListener('DOMContentLoaded', init);

// Initialize the map and fetch GeoJSON data
function init() {
    // Set base map view
    map = L.map('map').setView([21.15, 79.08], 4);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Fetch places data after map initialization
    fetchGetRequest('/api/v1/places', addAllPlacesToMap);

    // Move element selections here to ensure they exist
    const placeImageElement = document.getElementById('placeimage');
    const menuTitleElement = document.getElementById('menu_title');
    const menuTextElement = document.getElementById('menu_text');

    if (!placeImageElement || !menuTitleElement || !menuTextElement) {
        console.error('One or more DOM elements are not found.');
        return;
    }

    // Define popup and click handler for each feature
    const onEachFeatureHandler = (feature, layer) => {
        let placeName = feature.properties.place_name;
        layer.bindPopup(`Place name is <br/><center><b> ${placeName} </b></center>`);
        console.log(feature);

        let noImageAvailable = './media/place_images/no_image.jpg';

        layer.on('click', (e) => {
            let featureImage = feature.properties.image ? feature.properties.image : noImageAvailable;
            let featureDescription = feature.properties.description;

            menuTitleElement.innerHTML = `Cultural place name : ${placeName}`;
            placeImageElement.setAttribute('src', featureImage);
            menuTextElement.innerHTML = featureDescription;
            
            // Add nearby cities logic
            let featureId = feature.properties.pk;
            addNearbyCitiesLogic(featureId);
        });
    };

    // Add places to the map from the fetched JSON data
    function addAllPlacesToMap(json) {
        if (map) {
            L.geoJSON(json, {
                pointToLayer: function(feature, latlng) { return L.circleMarker(latlng, pointstyle); },
                onEachFeature: (feature, layer) => { onEachFeatureHandler(feature, layer); },
            }).addTo(map);
        } else {
            console.error('Map is not initialized.');
        }
    }

    // Add Nearby cities logic
    const addNearbyCities = (geojson) => {
        if (nearbyCitiesGeoJSONLayer) { 
            map.removeLayer(nearbyCitiesGeoJSONLayer); 
        }
        nearbyCitiesGeoJSONLayer = L.geoJSON(geojson, {
            interactive: true,
            onEachFeature: (feature, layer) => {
                let cityName = feature.properties.name;
                let proximity = feature.properties.proximity;
                layer.bindPopup(`City name: ${cityName}, <br/> Proximity: ${proximity}`);
            }
        }).addTo(map);
    };

    const addNearbyCitiesLogic = (id) => {
        let url = `/api/v1/cities/?placeid=${id}`;
        console.log('id', id);
        console.log('url', url);
        fetchGetRequest(url, addNearbyCities);
    };

    // Remove the nearbyCitiesGeoJSONLayer if clicking outside city area
    map.on('click', (e) => {
        if (nearbyCitiesGeoJSONLayer && !e.originalEvent.target.closest('.leaflet-popup')) {
            map.removeLayer(nearbyCitiesGeoJSONLayer);
        }
    });
}

// Fetch JSON data from the server and pass it to the callback function
async function fetchGetRequest(url, func) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const json = await response.json();
        func(json); // Call the callback function with the fetched JSON data
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Define the style for the points
const pointstyle = {
    stroke: true,
    radius: 8,
    color: 'black',
    weight: 2,
    opacity: 1,
    fillColor: 'orange',
    fillOpacity: 1,
};
