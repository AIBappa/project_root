// ProximityInput.js
import React, { useState } from 'react';

const ProximityInput = ({ onProximityChange }) => {
    const [proximity, setProximity] = useState(5); // Default to 5 km

    const handleChange = (event) => {
        const newProximity = event.target.value;
        setProximity(newProximity);
        onProximityChange(newProximity);
    };

    return (
        <div>
            <label htmlFor="proximity">Proximity (km):</label>
            <input
                id="proximity"
                type="number"
                value={proximity}
                onChange={handleChange}
                min="1"
                step="0.1"
            />
        </div>
    );
};

export default ProximityInput;
