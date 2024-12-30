//adding the script for the weather app
document.getElementById('weatherForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const city = document.getElementById('cityInput').value;
    const resultDiv = document.getElementById('result');

    try {
        const response = await fetch(`/weather/${city}`);
        if (response.ok) {
            const data = await response.json();
            resultDiv.innerHTML = `
                <h2>Weather in ${data.city}</h2>
                <p>Temperature: ${data.temperature}°C</p>
                <p>Condition: ${data.description}</p>
            `;
            saveRecentSearch(city); // Save the city to recent searches
        } else {
            resultDiv.innerHTML = `<p>City not found. Please try again.</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p>Error fetching weather data. Please try later.</p>`;
    }
});

// Save recent searches in local storage
function saveRecentSearch(city) {
    let searches = JSON.parse(localStorage.getItem('recentSearches')) || [];
    if (!searches.includes(city)) {
        searches.push(city); // Add the city if it's not already in the list
        if (searches.length > 5) {
            searches.shift(); // Keep only the last 5 searches
        }
        localStorage.setItem('recentSearches', JSON.stringify(searches));
    }
}

// Show recent searches
document.getElementById('showSearchesButton').addEventListener('click', function() {
    const recentSearchesDiv = document.getElementById('recentSearches');
    const searches = JSON.parse(localStorage.getItem('recentSearches')) || [];
    if (searches.length === 0) {
        recentSearchesDiv.innerHTML = "<p>No recent searches.</p>";
    } else {
        recentSearchesDiv.innerHTML = `
            <h3>Recent Searches:</h3>
            <ul>
                ${searches.map(city => `<li>${city}</li>`).join('')}
            </ul>
        `;
    }
});

