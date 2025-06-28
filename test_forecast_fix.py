#!/usr/bin/env python3
"""
Test script to fix forecast agent by seeding vector database with sample data
"""

import sys
sys.path.append('.')

# Import config first to set environment variables
import config

from vector_database.chroma import get_chroma_client
from embedding.embedding import get_gemini_embedding

def seed_forecast_data():
    """Seed the vector database with sample forecast data"""
    print("🔥 SEEDING FORECAST DATA...")
    
    # Get ChromaDB client and collection
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="forecast_data")
    
    # Sample forecast data matching the conversation logs
    forecast_data = [
        {
            "id": "forecast_logistics_dlt_support_2025",
            "document": """📊 Logistics DLT Support Team - Volume Forecast 2025-2026

Business: logistics
Substream: dlt  
Team: support

Monthly Volume Forecast:
• June 2025: 2,845 cases
• July 2025: 2,843 cases
• August 2025: 2,519 cases
• September 2025: 3,499 cases
• October 2025: 3,597 cases
• November 2025: 2,780 cases
• December 2025: 3,295 cases
• January 2026: 1,921 cases
• February 2026: 3,005 cases
• March 2026: 1,144 cases
• April 2026: 2,535 cases
• May 2026: 3,758 cases

Average Monthly Volume: 2,728 cases
Peak Month: May 2026 (3,758 cases)
Low Month: March 2026 (1,144 cases)

Forecast Confidence: 85%
Data Source: Workforce Planning System
Generated: 2025-06-25""",
            "metadata": {
                "business": "logistics",
                "substream": "dlt",
                "team": "support",
                "data_type": "volume_forecast",
                "time_period": "2025-2026",
                "forecast_type": "monthly"
            }
        },
        {
            "id": "forecast_logistics_dlt_marketing_2025",
            "document": """📊 Logistics DLT Marketing Team - Volume Forecast 2025-2026

Business: logistics
Substream: dlt
Team: marketing

Monthly Volume Forecast:
• June 2025: 1,245 cases
• July 2025: 1,543 cases
• August 2025: 1,819 cases
• September 2025: 2,199 cases
• October 2025: 2,297 cases
• November 2025: 1,980 cases
• December 2025: 2,095 cases
• January 2026: 1,621 cases
• February 2026: 1,805 cases
• March 2026: 1,344 cases
• April 2026: 1,735 cases
• May 2026: 2,158 cases

Average Monthly Volume: 1,820 cases
Peak Month: October 2025 (2,297 cases)
Low Month: March 2026 (1,344 cases)

Forecast Confidence: 78%
Data Source: Workforce Planning System
Generated: 2025-06-25""",
            "metadata": {
                "business": "logistics",
                "substream": "dlt",
                "team": "marketing",
                "data_type": "volume_forecast",
                "time_period": "2025-2026",
                "forecast_type": "monthly"
            }
        },
        {
            "id": "forecast_retail_pos_support_2025",
            "document": """📊 Retail POS Support Team - Volume Forecast 2025-2026

Business: retail
Substream: pos
Team: support

Monthly Volume Forecast:
• June 2025: 4,145 cases
• July 2025: 4,243 cases
• August 2025: 3,919 cases
• September 2025: 4,899 cases
• October 2025: 5,197 cases
• November 2025: 4,580 cases
• December 2025: 5,995 cases
• January 2026: 3,821 cases
• February 2026: 4,305 cases
• March 2026: 3,644 cases
• April 2026: 4,235 cases
• May 2026: 5,458 cases

Average Monthly Volume: 4,537 cases
Peak Month: December 2025 (5,995 cases)
Low Month: March 2026 (3,644 cases)

Forecast Confidence: 92%
Data Source: Workforce Planning System
Generated: 2025-06-25""",
            "metadata": {
                "business": "retail",
                "substream": "pos",
                "team": "support",
                "data_type": "volume_forecast",
                "time_period": "2025-2026",
                "forecast_type": "monthly"
            }
        }
    ]
    
    # Add data to vector database
    for data in forecast_data:
        print(f"🔥 Adding forecast data: {data['id']}")
        
        # Get embedding for the document
        embedding = get_gemini_embedding(data["document"])
        
        if embedding:
            collection.add(
                documents=[data["document"]],
                metadatas=[data["metadata"]],
                embeddings=[embedding],
                ids=[data["id"]]
            )
            print(f"✅ Added: {data['id']}")
        else:
            print(f"❌ Failed to get embedding for: {data['id']}")
    
    print("✅ FORECAST DATA SEEDING COMPLETE!")
    
    # Test the collection
    print("\n🔍 TESTING COLLECTION...")
    count = collection.count()
    print(f"📊 Total documents in forecast_data collection: {count}")
    
    # Test query
    test_query = "work volume forecast for logistics dlt support"
    test_embedding = get_gemini_embedding(test_query)
    if test_embedding:
        results = collection.query(
            query_embeddings=[test_embedding],
            n_results=1,
            include=["documents", "metadatas", "distances"]
        )
        
        if results and results.get('documents') and results['documents'][0]:
            distance = results['distances'][0][0]
            confidence = 1 - distance
            print(f"✅ Test query successful!")
            print(f"📊 Query: '{test_query}'")
            print(f"📊 Confidence: {confidence:.1%}")
            print(f"📄 Document snippet: {results['documents'][0][0][:200]}...")
        else:
            print(f"❌ Test query failed - no results")
    else:
        print(f"❌ Test query failed - no embedding")

def test_forecast_agent():
    """Test the forecast agent with the seeded data"""
    print("\n🔥 TESTING FORECAST AGENT...")
    
    from agents.fetch_forecasting_agent import fetch_forecast
    
    # Test the function call
    test_request = "Get forecast for business logistics, substream dlt, team support"
    print(f"📝 Testing request: {test_request}")
    
    result = fetch_forecast(test_request)
    print(f"📊 Result type: {type(result)}")
    print(f"📄 Result content: {result}")

if __name__ == "__main__":
    print("🚀 FORECAST FIX TEST")
    print("="*50)
    
    try:
        # Seed the database
        seed_forecast_data()
        
        # Test the agent
        test_forecast_agent()
        
        print("\n✅ FORECAST FIX TEST COMPLETE!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc() 