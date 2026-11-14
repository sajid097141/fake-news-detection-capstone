
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_FACT_CHECK_API_KEY")

if not API_KEY:
    print("ERROR: API key not found in .env")
    raise SystemExit(1)

url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

params = {
    "key": API_KEY,
    "query": "The Earth is flat",
    "pageSize": 3
}

try:
    response = requests.get(url, params=params, timeout=20)

    print("HTTP Status:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        claims = data.get("claims", [])

        print("API connection successful!")
        print("Claims returned:", len(claims))

        for claim in claims:
            print("\nClaim:", claim.get("text"))
            for review in claim.get("claimReview", []):
                print("Publisher:", review.get("publisher", {}).get("name"))
                print("Rating:", review.get("textualRating"))
                print("Source:", review.get("url"))

    else:
        print("API Error:", response.json())

except requests.RequestException as error:
    print("Connection failed:", error)
