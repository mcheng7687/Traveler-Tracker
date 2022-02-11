class City {
    constructor(cityName, temp, localTime, weatherState, weatherIcon) {
        this.cityName = cityName;
        this.temp = temp;
        this.localTime = localTime;
        this.weatherState = weatherState;
        this.weatherIcon = weatherIcon;
      }
}

// Get full city list shown on home page
// Return array of String of city names
function getCityList() {
    const cityNames = [];

    $(".city").each(function () { 
        cityNames.push($(this).text().split("\n")[1].trim());
    });

    return cityNames;
}

// Get all currency codes shown on home page
// Return Set object of currecy codes
function getCurrencyCodes(cityNames) {
    const codes = new Set();

    for (let cityName of cityNames) {
        let noSpacesInCityName = cityName.replace(" ","");
        codes.add($(`#${noSpacesInCityName}`).next().attr("class"));
    }

    return codes;
}

//***************************************************************************//
// Access weather from https://www.weatherapi.com/docs/
// Accepts JSON from external API and return object
async function getWeather(cityName) {

    const cityInfo = await axios.get(`http://api.weatherapi.com/v1/current.json`, 
                                    {params: {"key": WEATHER_API_KEY, 
                                                "q": cityName}});

    const city = new City(cityName, 
                        cityInfo.data.current.feelslike_f, 
                        cityInfo.data.location.localtime,
                        cityInfo.data.current.condition.text,
                        cityInfo.data.current.condition.icon);

    return city;
}

// Update specific city weather conditions and local time in DOM
// "city" arguement is of class City
function updateCityWeather(city) {
    console.log(city);
    $(`#${city.cityName.replace(" ", '')}`).html(`<h6 class="text-center">${city.localTime}</h6>
                                                  <h6 class="text-center">${city.weatherState}</h6>
                                                  <img class="center-block" src=${city.weatherIcon} alt="${city.weatherState}" />
                                                  <h3 class="text-center">${city.temp}\xB0F</h3>
                                                  `);
}

//***************************************************************************//
// Get list of exchange rates from https://www.exchangerate-api.com/docs/standard-requests
// Returns rates as Object with base currency code.
// For example, base = "USD" returns all foreign currency rates equivalent to 1 USD 
async function getExchangeRates(base) {
    const currencyInfo = await axios.get(`https://v6.exchangerate-api.com/v6/${EXCHANGE_API_KEY}/latest/${base}`);

    return currencyInfo.data.conversion_rates;
}

//***************************************************************************//
// Code to run at the start of the home page
// Get foreign exchange rate on every refresh of home page
// Update city weather info every 5 minutes (300000 ms)
const cityNames = getCityList();
const codes = new Set ();
const base = $(".home-currency-code").text();

getExchangeRates(base).then(function(rates) {
    const currency_codes = getCurrencyCodes(cityNames);

    currency_codes.forEach( 
        function (currency_code) {
            $(`.${currency_code}`).children().text(`1 ${base} = ${rates[currency_code]} ${currency_code}`);
        });
    
    for (let cityName of cityNames) {
        getWeather(cityName.trim()).then(updateCityWeather);
    }
});

const rep = setInterval(function () {

    for (let cityName of cityNames) {
        getWeather(cityName.trim()).then(updateCityWeather);
    }

}, 300000);

// End here