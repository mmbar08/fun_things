import requests
import csv
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

SERP_API_KEY = "65e733f469bbe761a38dac071d9daa981894df578ef6d787f7b910e6fca4eeea"

ENTRY_LEVEL_KEYWORDS = [
    "entry level", "no experience", "crew", "team member", "associate",
    "cashier", "host", "front desk", "seasonal", "barista"
]

PART_TIME_KEYWORDS = [
    "part time", "part-time", "pt"
]

FULL_TIME_KEYWORDS = [
    "full time", "full-time", "ft"
]

def get_coordinates(zipcode):
    geolocator = Nominatim(user_agent="job_finder")
    location = geolocator.geocode(zipcode)
    return (location.latitude, location.longitude)

def fetch_jobs(zipcode):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_jobs",
        "q": "part time entry level jobs",
        "location": zipcode,
        "api_key": SERP_API_KEY,
        "num": 50
    }
    response = requests.get(url, params=params)
    return response.json().get("jobs_results", [])

def contains_keyword(text, keywords):
    if not text:
        return False
    text = text.lower()
    return any(keyword in text for keyword in keywords)

def extract_min_age(text):
    if not text:
        return None
    for age in [16, 17, 18]:
        if str(age) in text:
            return age
    return None

def main():
    zipcode = input("Enter your ZIP code: ")
    age = int(input("Enter your age: "))

    print("\nFetching jobs...")

    user_coords = get_coordinates(zipcode)
    jobs = fetch_jobs(zipcode)

    filtered = []

    for job in jobs:
        title = job.get("title", "")
        company = job.get("company_name", "")
        address = job.get("location", "")
        description = job.get("description", "")
        link = job.get("apply_options", [{}])[0].get("link")

        text = (title + " " + description).lower()

        # Must be part-time
        if not contains_keyword(text, PART_TIME_KEYWORDS):
            continue

        # Must NOT be full-time
        if contains_keyword(text, FULL_TIME_KEYWORDS):
            continue

        # Must be entry-level
        if not contains_keyword(text, ENTRY_LEVEL_KEYWORDS):
            continue

        # Age filter
        min_age = extract_min_age(description)
        if min_age and min_age > age:
            continue

        # Coordinates
        coords = job.get("detected_extensions", {}).get("coordinates")
        if coords:
            job_coords = (coords.get("latitude"), coords.get("longitude"))
        else:
            try:
                job_coords = get_coordinates(address)
            except:
                continue

        distance = geodesic(user_coords, job_coords).miles

        if distance <= 3:
            filtered.append([company, title, address, round(distance, 2), min_age, link])

    print("\nPart‑time entry‑level jobs within 3 miles:\n")
    for job in filtered:
        print(f"{job[0]} — {job[1]} ({job[3]} miles)")
        print(f"Age requirement: {job[4]}")
        print(f"Apply: {job[5]}\n")

    with open("jobs_nearby.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Company", "Title", "Address", "Distance (mi)", "Min Age", "Apply Link"])
        writer.writerows(filtered)

    print("Saved results to jobs_nearby.csv")

if __name__ == "__main__":
    main()
