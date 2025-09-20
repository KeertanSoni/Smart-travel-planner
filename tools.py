import os
import requests
from datetime import datetime, timedelta

# We are keeping this dummy function as it doesn't need an API key
def find_activities(destination: str, category: str) -> str:
    """
    This is a dummy function to find activities.
    It returns a hardcoded string with fake activity suggestions.
    """
    print(f"--> Finding activities in {destination} under the category '{category}'...")
    if category.lower() == "beaches":
        return "Found activities: Baga Beach, Calangute Beach, Anjuna Beach."
    elif category.lower() == "food":
        return "Found local food spots: Fisherman's Wharf, Britto's, Martin's Corner."
    else:
        return "No activities found for that category."

def search_flights(origin: str, destination: str, date: str) -> str:
    """
    This function searches for real flights using the Kiwi.com API on RapidAPI.
    It can now handle both specific dates (YYYY-MM-DD) and general month names (e.g., "December").
    """
    print(f"--> Searching for REAL flights from {origin} to {destination} on {date}...")
    
    # --- START of the new, smarter date handling logic --- # COMMENT: This new block will fix the error.
    try:
        # First, we try to read the date as if it's already in the correct format.
        parsed_date = datetime.strptime(date, '%Y-%m-%d')
        date_from = parsed_date.strftime('%Y-%m-%d')
    except ValueError:
        # If the above fails, it's likely a month name like "December".
        print(f"--> '{date}' is not a specific date. Assuming the first of the month.")
        try:
            now = datetime.now()
            # Convert the month name to its number (e.g., "December" -> 12)
            month_number = datetime.strptime(date, '%B').month
            
            # If the month has already passed this year, assume next year.
            target_year = now.year
            if month_number < now.month:
                target_year += 1
            
            # Create a full date string for the first day of that month.
            date_from = f"{target_year}-{month_number:02d}-01"
            print(f"--> Automatically set start date to: {date_from}")
        except ValueError:
            # If we can't understand the date at all, return an error.
            return "Could not understand the date. Please use a format like 'YYYY-MM-DD' or a month name."
    # --- END of the new, smarter date handling logic --- #

    # The rest of the function now uses our processed 'date_from'
    date_to = (datetime.strptime(date_from, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    
    url = "https://kiwi.com-cheap-flights.p.rapidapi.com/round-trip"
    
    querystring = {
        "from": origin,
        "to": destination,
        "dateFrom": date_from,
        "dateTo": date_to,
        "adults": "2",
        "currency": "INR"
    }
    
    headers = {
        "X-RapidAPI-Key": os.getenv("FLIGHT_API_KEY"),
        "X-RapidAPI-Host": "kiwi.com-cheap-flights.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        if data.get("data"):
            first_flight = data["data"][0]
            price = first_flight.get("price")
            airline_codes = first_flight.get("airlines", [])
            
            return f"Found a flight with airline(s) {', '.join(airline_codes)} for ₹{price}."
        else:
            return "No flights found for the specified route and date."
            
    except requests.exceptions.RequestException as e:
        return f"An error occurred while calling the flight API: {e}"
    
def search_hotels(destination: str, num_nights: int) -> str:
    """
    This function searches for real hotels using the Hotels.com API on RapidAPI.
    It first finds the destination ID and then searches for hotels.
    """
    print(f"--> Searching for REAL hotels in {destination} for {num_nights} nights...")
    
    # --- Part 1: Get the Destination ID from the location name ---
    region_search_url = "https://hotels-com-provider.p.rapidapi.com/v2/regions"
    region_querystring = {"query": destination, "domain": "IN", "locale": "en_GB"}
    
    headers = {
        "X-RapidAPI-Key": os.getenv("HOTEL_API_KEY"),
        "X-RapidAPI-Host": "hotels-com-provider.p.rapidapi.com"
    }
    
    try:
        region_response = requests.get(region_search_url, headers=headers, params=region_querystring)
        region_response.raise_for_status()
        region_data = region_response.json()
        
        # Extract the destination ID (gaiaId)
        destination_id = None
        for item in region_data.get('data', []):
            if item.get('__typename') == 'Region':
                destination_id = item.get('gaiaId')
                break
        
        if not destination_id:
            return f"Could not find a destination ID for {destination}."

        # --- Part 2: Search for hotels using the Destination ID ---
        checkin_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d') # Search 30 days from now
        checkout_date = (datetime.now() + timedelta(days=30 + num_nights)).strftime('%Y-%m-%d')

        hotel_search_url = "https://hotels-com-provider.p.rapidapi.com/v2/hotels/search"
        hotel_querystring = {
            "region_id": destination_id,
            "locale": "en_GB",
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "domain": "IN",
            "adults_number": "2",
            "sort_order": "RECOMMENDED"
        }
        
        hotel_response = requests.get(hotel_search_url, headers=headers, params=hotel_querystring)
        hotel_response.raise_for_status()
        hotel_data = hotel_response.json()
        
        if hotel_data.get('listResults', {}).get('hotels'):
            first_hotel = hotel_data['listResults']['hotels'][0]
            hotel_name = first_hotel.get('name')
            price_info = first_hotel.get('price', {}).get('lead', {})
            price = price_info.get('formatted')
            
            return f"Found hotel: '{hotel_name}' with a price of {price}."
        else:
            return "No hotels found for the specified destination and dates."

    except requests.exceptions.RequestException as e:
        return f"An error occurred while calling the hotel API: {e}"