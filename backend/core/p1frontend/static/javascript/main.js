// The code is divided into following sections
// Global declarations
// init() function - main function 
// Constituent functions declared in the main init()


// Global declarations
let map; // Declare map globally
let nearbyContactsGeoJSONLayer; // Declare nearbyContactsGeoJSONLayer globally

document.addEventListener('DOMContentLoaded', init);

function init() {
    // Set base map view
    map = L.map('map').setView([21.15, 79.08], 4);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Event listener for map clicks
    map.on('click', (e) => {
        const { lat, lng } = e.latlng;
        const proximity = document.getElementById('proximity').value;

        fetchContacts(lat, lng, proximity);
    });
}

async function fetchContacts(lat, lng, proximity) {
    const url = `/api/v1/contacts/?lat=${lat}&lng=${lng}&proximity=${proximity}`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const geojson = await response.json();
        addContactsToMap(geojson);
    } catch (error) {
        console.error('Error fetching contacts:', error);
    }
}

function addContactsToMap(geojson) {
    if (nearbyContactsGeoJSONLayer) {
        map.removeLayer(nearbyContactsGeoJSONLayer);
    }
    nearbyContactsGeoJSONLayer = L.geoJSON(geojson, {
        pointToLayer: function(feature, latlng) { return L.circleMarker(latlng, pointstyle); },
        onEachFeature: (feature, layer) => {
            let contactName = feature.properties.name;
            let contactEmail = feature.properties.email;
            layer.bindPopup(`Contact: ${contactName}<br>Email: ${contactEmail}`);
        }
    }).addTo(map);
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
