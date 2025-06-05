#!/usr/bin/env python3
"""
REAL EXAMPLE: Vector Data Store Flow
Based on actual logs from the workforce management system
"""

# ===== STEP 1: USER REQUEST =====
user_request = "Hi,volume forecast for business is 'logistics' and substream is 'dlt', team name is 'support'"

# ===== STEP 2: FETCH AGENT EXECUTES =====
# Function: fetch_forecast({"business": "logistics", "substream": "dlt", "team_name": "support"})

# Vector database returns:
vector_db_result = """For the logistics business, dlt substream, and support team:

**Team:** Support
**Business:** Logistics
**Substream:** DLT

**Forecast:**
*   **2025-06-01:** 2845
*   **2025-07-01:** 2843
*   **2025-08-01:** 2519
*   **2025-09-01:** 3499
*   **2025-10-01:** 3597
*   **2025-11-01:** 2780
*   **2025-12-01:** 3295
*   **2026-01-01:** 1921
*   **2026-02-01:** 3005
*   **2026-03-01:** 1144
*   **2026-04-01:** 2535
*   **2026-05-01:** 3758"""

# ===== STEP 3: AUTOMATIC STORAGE IN VECTOR DATA STORE =====
# This happens automatically in fetch_forecasting_agent.py:

stored_entry = {
    "timestamp": "2025-06-05 17:13:51.669788",
    "timestamp_sort": 1733422431.669788,
    "query_type": "forecast",
    "business": "logistics",
    "substream": "dlt", 
    "team": "support",
    "result_data": vector_db_result,  # The actual forecast data
    "metadata": {
        "original_request": user_request,
        "raw_results_count": 3,
        "confidence_scores": [0.85, 0.72, 0.61],
        "query": "work volume forecast for logistics dlt support"
    },
    "entry_id": "forecast_teams_anonymous_20250605_171351_669788"
}

print("📊 STORED ENTRY:")
print(f"🆔 Entry ID: {stored_entry['entry_id']}")
print(f"🏢 Business: {stored_entry['business']}")
print(f"🌊 Substream: {stored_entry['substream']}")
print(f"👥 Team: {stored_entry['team']}")
print(f"📦 Data Preview: {stored_entry['result_data'][:100]}...")

# ===== STEP 4: USER ASKS FOR VISUALIZATION =====
viz_request = "can you plot that ?"

# ===== STEP 5: INTELLIGENT RETRIEVAL =====
# Visualization agent parses intent and queries data store:

query_criteria = {
    "session_id": "teams_anonymous",
    "query_type": "forecast",
    "business": "logistics",
    "substream": "dlt", 
    "team": "support"
}

print("\n🎯 RETRIEVAL QUERY:")
for key, value in query_criteria.items():
    print(f"   {key}: {value}")

# ===== STEP 6: DATA PARSING FOR VISUALIZATION =====
# The stored data gets parsed into visualization format:

parsed_data_points = [
    {"date": "2025-06-01", "value": 2845},
    {"date": "2025-07-01", "value": 2843},
    {"date": "2025-08-01", "value": 2519},
    {"date": "2025-09-01", "value": 3499},
    {"date": "2025-10-01", "value": 3597},
    {"date": "2025-11-01", "value": 2780},
    {"date": "2025-12-01", "value": 3295},
    {"date": "2026-01-01", "value": 1921},
    {"date": "2026-02-01", "value": 3005},
    {"date": "2026-03-01", "value": 1144},
    {"date": "2026-04-01", "value": 2535},
    {"date": "2026-05-01", "value": 3758}
]

print(f"\n📊 PARSED DATA POINTS: {len(parsed_data_points)} points")
for i, point in enumerate(parsed_data_points[:3], 1):
    print(f"   [{i}] {point['date']} = {point['value']:,}")
print(f"   ... and {len(parsed_data_points) - 3} more points")

# ===== STEP 7: VISUALIZATION JSON CREATION =====
visualization_data = {
    "business": "logistics",
    "substream": "dlt", 
    "team": "support",
    "forecast_data": parsed_data_points
}

print(f"\n🎨 VISUALIZATION DATA CREATED:")
print(f"📦 JSON size: {len(str(visualization_data))} characters")
print(f"📋 Business: {visualization_data['business']}")
print(f"📋 Data points: {len(visualization_data['forecast_data'])}")

# ===== STEP 8: CHART GENERATION =====
# The data gets passed to create_visualization function:

chart_spec = {
    'data': [{
        'x': [point['date'] for point in parsed_data_points],
        'y': [point['value'] for point in parsed_data_points],
        'type': 'scatter',
        'mode': 'lines+markers',
        'name': 'Logistics DLT Support Forecast',
        'line': {'color': '#2E86C1', 'width': 3},
        'marker': {'size': 8, 'color': '#2E86C1'}
    }],
    'layout': {
        'title': {'text': 'Logistics DLT Support Team - Volume Forecast', 'x': 0.5},
        'xaxis': {'title': 'Date'},
        'yaxis': {'title': 'Volume'},
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white'
    }
}

print(f"\n📈 CHART GENERATED:")
print(f"🎯 Title: {chart_spec['layout']['title']['text']}")
print(f"📊 Data points: {len(chart_spec['data'][0]['x'])}")
print(f"📈 Chart type: {chart_spec['data'][0]['type']}")

# ===== REAL LOG OUTPUT =====
print(f"\n📋 ACTUAL LOG MESSAGES:")
log_messages = [
    "📊 Stored forecast search result for logistics-dlt-support in session teams_anonymous",
    "✅ Stored forecast data in vector data store: forecast_teams_anonymous_20250605_171351_669788",
    "✅ AUDIT - Match found: logistics-dlt-support @ 17:21:12",
    "🎯 Total data points extracted: 12",
    "✅ VIZ SUCCESS - Created chart with 1 traces",
    "✅ Successfully sent chart image to Teams!"
]

for msg in log_messages:
    print(f"   {msg}")

print(f"\n🎯 SUMMARY:")
print("✅ User asks for forecast → Data automatically stored in vector data store")
print("✅ User asks for plot → Data intelligently retrieved and parsed")  
print("✅ Chart created from stored data → Sent to Teams as image")
print("✅ Complete flow: Request → Store → Retrieve → Visualize") 