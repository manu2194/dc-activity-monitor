import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
from send_text import send_sms_via_email

# URL of the events page
EVENTS_URL = "https://dc.citycast.fm/events"

# Function to fetch HTML from the website
def fetch_html():
    """
    Fetch the HTML content of the events page.

    :return: The raw HTML content of the page as a string, or None if an error occurs.
    """
    try:
        response = requests.get(EVENTS_URL)
        response.raise_for_status()  # Raise an error for bad responses (e.g., 404, 500)
        return response.text
    except requests.RequestException as e:
        print(f"❌ Error fetching events: {e}")
        return None
    
def fetch_html_local():
    """
    Fetch HTML content from a local file (for testing purposes).

    :return: The raw HTML content from the "events.html" file.
    """
    with open("events.html", "r") as f:
        return f.read()

# Function to parse event data from HTML
def parse_events(html):
    """
    Parses event data from the provided HTML string.

    :param html: The raw HTML content of the page.
    :return: A list of dictionaries, each representing a day's events.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find the main event container
    event_list = soup.find("div", id="event-list")
    if not event_list:
        print("❌ No event list found on the page.")
        return []

    parsed_events = []
    for day_section in event_list.find_all("div", class_="items-start"):
        # Extract the event date from <h3>
        date_heading = day_section.find("h3")
        date_text = date_heading.text.strip() if date_heading else "Unknown Date"
        timestamp = parse_date_to_iso(date_text)  # Convert to ISO format (YYYY-MM-DD)

        # Locate the list of events for the day
        events_container = day_section.find("div", class_="prose")
        event_list = events_container.find("ul") if events_container else None
        if not event_list:
            continue

        events = []
        for li in event_list.find_all("li"):
            """
            Structure of <li>:
            <li> <text node with emoji> <a>Event Title</a> <text node with time | price | location> </li>
            """
            
            # Extract the entire text inside <li> with custom separator for clarity
            text = li.get_text(strip=True, separator='___')
            anchor = li.find("a")  # Extract anchor (event title)
            
            link = anchor.get("href") if anchor else None  # Extract event link
            emoji = None  # Default emoji placeholder
            title = 'Unknown Event'
            time = 'Unknown Time'
            price = 'Unknown Price'
            location = 'Unknown Location'
            
            # Split text using separator
            parts = text.split('___')
            if len(parts) == 3:
                # Structure: [emoji, title, details]
                emoji, title, details = parts
            else:
                # Structure: [title, details] (no emoji)
                title, details = parts
                emoji = None
                
            # Split details into time, price, and location
            details = details.split('|')[1:]  # Remove first empty part before '|'
            time = details[0].strip() if details else time
            price = details[1].strip() if len(details) > 1 else price
            if not price or price.lower() == 'free':
                price = '$0'
            location = details[2].strip() if len(details) > 2 else location

            events.append({
                "emoji": emoji,      # Emoji (e.g., 🎭, 🎵)
                "title": title,      # Event title
                "link": link,        # Event link (if available)
                "time": time,        # Event time
                "price": price,      # Price (e.g., "Free", "$10")
                "location": location # Location (e.g., "Dupont Circle")
            })

        parsed_events.append({
            "timestamp": timestamp,         # ISO-formatted date (YYYY-MM-DD)
            "friendly_timestamp": date_text, # Original date string (e.g., "FRIDAY, Feb. 7")
            "events": events                 # List of events for the day
        })

    return parsed_events

# Helper function to convert date string to ISO format
def parse_date_to_iso(date_text):
    """
    Convert a date string (e.g., 'FRIDAY, Feb. 7') to ISO format (YYYY-MM-DD).

    :param date_text: Date string in "Day, Month. Date" format.
    :return: Date string in ISO format (YYYY-MM-DD) or None if parsing fails.
    """
    try:
        date_parts = date_text.split(", ")
        if len(date_parts) < 2:
            return None

        month_day = date_parts[1].replace(".", "")  # Remove period from month abbreviation
        event_date = datetime.strptime(month_day, "%b %d")  # Parse "Feb 7"
        current_year = datetime.now().year
        event_date = event_date.replace(year=current_year)  # Add current year

        return event_date.strftime("%Y-%m-%d")  # Return ISO format date
    except ValueError:
        return None

# Main function to get and parse events
def get_events():
    """
    Fetch HTML and parse event data.

    :return: A list of parsed events.
    """
    html = fetch_html_local()  # Change to fetch_html() to use live website
    if html:
        return parse_events(html)
    return []

# Run the scraper
if __name__ == "__main__":
    events = get_events()

    if events:     
        # Save to a JSON file
        with open("events.json", "w") as f:
            json.dump(events, f, indent=4, ensure_ascii=False)
        send_sms_via_email(events)
    else:
        print("❌ No events found.")
