import requests
from django.conf import settings

api_key = settings.GOOGLE_API_KEY
google_maps_url = "https://addressvalidation.googleapis.com/v1:validateAddress"


def validate_address(address):

    payload = {
        "address": {"regionCode": "GB", "addressLines": [address]},
        "enableUspsCass": False,
    }

    response = requests.post(f"{google_maps_url}?key={api_key}", json=payload)
    result = response.json()

    if "error" in result:
        return {"error": "Invalid request to Google API", "details": result.get("error")}

    verdict = result.get("result", {}).get("verdict", {})
    address_data = result.get("result", {}).get("address", {})
    geocode = result.get("result", {}).get("geocode", {})

    address_complete = verdict.get("addressComplete", False)
    has_unconfirmed = verdict.get("hasUnconfirmedComponents", False)
    missing_components = address_data.get("missingComponentTypes", [])
    granularity = verdict.get("validationGranularity", "OTHER")

    if not address_complete or has_unconfirmed:
        return {"error": "Address is incomplete or unconfirmed"}
    
    if "postal_code" in missing_components or "premise" in missing_components:
        return {"error": "Address is missing postal code or premise"}
    
    if granularity == "OTHER":
        return {"error": "Address is too vague or not recognized"}

    return {
        "formattedAddress": address_data.get("formattedAddress"),
        "latitude": geocode.get("location", {}).get("latitude"),
        "longitude": geocode.get("location", {}).get("longitude"),
        "placeId": geocode.get("placeId"),
        "valid": True
        }