from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)

# Allow all origins, all headers, and credentials
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

SUBURB_LIST_URL = "https://www.microburbs.com.au/report_generator/api/suburb/suburbs"
SUBURB_AMENITY_URL = "https://www.microburbs.com.au/report_generator/api/suburb/amenity"
SUBURB_DEMO_URL = "https://www.microburbs.com.au/report_generator/api/suburb/demographics"
HEADERS = {
    "Authorization": "Bearer test",
    "Content-Type": "application/json"
}

@app.route('/')
def home():
    return "<h1>Welcome to Microburbs Suburb Dashboard API!</h1>"

@app.route('/api/suburbs', methods=['GET'])
def get_suburbs():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    try:
        params = {"page": page, "limit": limit}
        response = requests.get(SUBURB_LIST_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/suburbDetail', methods=['GET'])
def get_suburb_detail():
    suburb = request.args.get('suburb')
    if not suburb:
        return jsonify({"error": "Suburb query parameter is required"}), 400

    try:
        amenity_resp = requests.get(SUBURB_AMENITY_URL, headers=HEADERS, params={"suburb": suburb}, timeout=10)
        amenity_resp.raise_for_status()
        amenities_data = amenity_resp.json()

        demo_resp = requests.get(SUBURB_DEMO_URL, headers=HEADERS, params={"suburb": suburb}, timeout=10)
        demo_resp.raise_for_status()
        demo_data = demo_resp.json()

        # Count amenities by category
        category_counts = {}
        for item in amenities_data.get("results", []):
            cat = item.get("category", "Unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        merged = {
            "suburb": suburb,
            "amenities": {
                "category_counts": category_counts,
                "summary": f"Total {len(amenities_data.get('results', []))} amenities across {len(category_counts)} categories."
            },
            "demographics": demo_data
        }

        return jsonify(merged)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
