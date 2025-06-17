from autogen import ConversableAgent
from config import llm_config
from .promp_engineering.kpi_agent_prompt import kpi_agent_system_message
from embedding.embedding import get_gemini_embedding
from vector_database.chroma import get_chroma_client
import json
import re
from typing import Dict, List, Union
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from vector_database.chroma import get_chroma_client

# Import for data store integration - will be set by app_teams.py
_vector_data_store = None
_current_session_id = None

def set_data_store_context(data_store, session_id):
    """Set the data store and session context for this function"""
    global _vector_data_store, _current_session_id
    _vector_data_store = data_store
    _current_session_id = session_id
    print(f"✅ KPI Agent: Set data store context for session: {session_id}")

# Initialize ChromaDB client
chroma_client = get_chroma_client()

def get_date_filter(query: str) -> dict:
    """
    Extract date or date range from query and return ChromaDB filter
    Enhanced with BANKING TERMINOLOGY support for Q1, Q2, Q3, Q4, etc.
    """
    current_date = datetime.now()
    print(f"Debug - Processing date filter from query: {query}")
    print(f"Debug - Current date: {current_date}")
    
    query_lower = query.lower()
    
    # Handle full year requests
    year_match = re.search(r'year (\d{4})|(\d{4})', query_lower)
    if year_match:
        year = year_match.group(1) or year_match.group(2)
        year = int(year)
        dates = []
        for month in range(1, 13):  # 1 to 12
            date_str = f"{year}-{month:02d}-01"
            dates.append(date_str)
        print(f"🏦 FULL YEAR {year}: {dates}")
        return {"created_date": {"$in": dates}}
    
    # 🏦 BANKING QUARTERS - PRIORITY HANDLING (Q1, Q2, Q3, Q4)
    quarter_pattern = r"q([1-4])\s*(\d{4})"
    quarter_match = re.search(quarter_pattern, query_lower)
    if quarter_match:
        try:
            quarter_num = int(quarter_match.group(1))
            year = int(quarter_match.group(2))
            
            # Define quarter date ranges (calendar year)
            quarter_months = {
                1: [1, 2, 3],     # Q1 = Jan, Feb, Mar
                2: [4, 5, 6],     # Q2 = Apr, May, Jun  
                3: [7, 8, 9],     # Q3 = Jul, Aug, Sep
                4: [10, 11, 12]   # Q4 = Oct, Nov, Dec
            }
            
            months = quarter_months[quarter_num]
            dates = []
            
            for month in months:
                date_str = f"{year}-{month:02d}-01"
                dates.append(date_str)
            
            print(f"🏦 BANKING QUARTER - Q{quarter_num} {year}: {dates}")
            return {"created_date": {"$in": dates}}
            
        except Exception as e:
            print(f"Debug - Error parsing quarter: {str(e)}")
    
    # 🏦 HALF-YEAR PERIODS (H1, H2)
    half_pattern = r"h([12])\s*(\d{4})"
    half_match = re.search(half_pattern, query_lower)
    if half_match:
        try:
            half_num = int(half_match.group(1))
            year = int(half_match.group(2))
            
            if half_num == 1:  # H1 = Q1 + Q2 (Jan-Jun)
                months = [1, 2, 3, 4, 5, 6]
            else:  # H2 = Q3 + Q4 (Jul-Dec)
                months = [7, 8, 9, 10, 11, 12]
            
            dates = []
            for month in months:
                date_str = f"{year}-{month:02d}-01"
                dates.append(date_str)
            
            print(f"🏦 BANKING HALF - H{half_num} {year}: {dates}")
            return {"created_date": {"$in": dates}}
            
        except Exception as e:
            print(f"Debug - Error parsing half year: {str(e)}")
    
    # 🏦 RELATIVE QUARTERS (last quarter, current quarter, previous quarter)
    if "quarter" in query_lower:
        try:
            current_month = current_date.month
            current_year = current_date.year
            
            # Determine current quarter
            if current_month <= 3:
                current_quarter = 1
            elif current_month <= 6:
                current_quarter = 2
            elif current_month <= 9:
                current_quarter = 3
            else:
                current_quarter = 4
            
            target_quarter = None
            target_year = current_year
            
            if any(phrase in query_lower for phrase in ["current quarter", "this quarter"]):
                target_quarter = current_quarter
            elif any(phrase in query_lower for phrase in ["last quarter", "previous quarter"]):
                target_quarter = current_quarter - 1
                if target_quarter < 1:
                    target_quarter = 4
                    target_year = current_year - 1
            
            if target_quarter:
                quarter_months = {
                    1: [1, 2, 3],     # Q1 = Jan, Feb, Mar
                    2: [4, 5, 6],     # Q2 = Apr, May, Jun  
                    3: [7, 8, 9],     # Q3 = Jul, Aug, Sep
                    4: [10, 11, 12]   # Q4 = Oct, Nov, Dec
                }
                
                months = quarter_months[target_quarter]
                dates = []
                
                for month in months:
                    date_str = f"{target_year}-{month:02d}-01"
                    dates.append(date_str)
                
                print(f"🏦 RELATIVE QUARTER - Q{target_quarter} {target_year}: {dates}")
                return {"created_date": {"$in": dates}}
                
        except Exception as e:
            print(f"Debug - Error parsing relative quarter: {str(e)}")
    
    # Handle "as of today", "today", "current", "now", "this month"
    if any(phrase in query_lower for phrase in ["as of today", "today", "current", "now", "this month", "current month"]):
        try:
            # Use current month's first day
            current_month = current_date.replace(day=1)
            date_str = current_month.strftime("%Y-%m-%d")
            print(f"Debug - Current date query, using: {date_str}")
            return {"created_date": date_str}
        except Exception as e:
            print(f"Debug - Error parsing current date: {str(e)}")
    
    # Handle orchestrator's month-YYYY-MM-DD format
    if "month-" in query_lower:
        try:
            month_match = re.search(r"month-(\d{4}-\d{2}-\d{2})", query_lower)
            if month_match:
                date_str = month_match.group(1)
                print(f"Debug - Found month date: {date_str}")
                return {"created_date": date_str}
        except Exception as e:
            print(f"Debug - Error parsing month date: {str(e)}")
    
    # Handle "last X months" and "past X months" - this should be checked FIRST before specific dates
    if any(keyword in query_lower for keyword in ["last", "past"]) and ("months" in query_lower or "month" in query_lower):
        try:
            # Extract number of months
            if any(phrase in query_lower for phrase in ["last month", "past month"]) and "months" not in query_lower:
                num_months = 1
            else:
                # Look for patterns like "last 4 months", "past 6 months", etc.
                month_match = re.search(r"(?:last|past)\s+(\d+)\s+months?", query_lower)
                if month_match:
                    num_months = int(month_match.group(1))
                else:
                    num_months = 1
                
            print(f"Debug - Extracting data for last/past {num_months} months")
            
            # Generate list of dates for the last N months
            dates = []
            current_month = current_date.replace(day=1)
            
            for i in range(num_months):
                month_date = current_month - relativedelta(months=i+1)  # Start from previous month
                dates.append(month_date.strftime("%Y-%m-%d"))
            
            print(f"Debug - Date list for last/past {num_months} months: {dates}")
            
            return {"created_date": {"$in": dates}}
            
        except Exception as e:
            print(f"Debug - Error parsing month range: {str(e)}")
            # Fall through to other parsing methods
    
    # Handle "last X years" and "past X years"
    if any(keyword in query_lower for keyword in ["last", "past"]) and ("years" in query_lower or "year" in query_lower):
        try:
            # Extract number of years
            if any(phrase in query_lower for phrase in ["last year", "past year"]) and "years" not in query_lower:
                num_years = 1
            else:
                # Look for patterns like "last 2 years", "past 3 years", etc.
                year_match = re.search(r"(?:last|past)\s+(\d+)\s+years?", query_lower)
                if year_match:
                    num_years = int(year_match.group(1))
                else:
                    num_years = 1
            
            # Convert years to months
            num_months = num_years * 12
            print(f"Debug - Extracting data for last/past {num_years} year{'s' if num_years > 1 else ''}: {num_months} months")
            
            # Generate list of dates for the last N months (converted from years)
            dates = []
            current_month = current_date.replace(day=1)
            
            for i in range(num_months):
                month_date = current_month - relativedelta(months=i+1)  # Start from previous month
                dates.append(month_date.strftime("%Y-%m-%d"))
            
            print(f"Debug - Date list for last/past {num_years} year{'s' if num_years > 1 else ''}: {len(dates)} months")
            
            return {"created_date": {"$in": dates}}
            
        except Exception as e:
            print(f"Debug - Error parsing year range: {str(e)}")
            # Fall through to other parsing methods
    
    # Handle "previous X months" (alternative to "last X months")
    if "previous" in query_lower and ("months" in query_lower or "month" in query_lower):
        try:
            # Extract number of months
            if "previous month" in query_lower and "months" not in query_lower:
                num_months = 1
            else:
                # Look for patterns like "previous 4 months" or "4 months"
                month_match = re.search(r"(?:previous\s+)?(\d+)\s+months?", query_lower)
                if month_match:
                    num_months = int(month_match.group(1))
                else:
                    num_months = 1
                
            print(f"Debug - Extracting data for previous {num_months} months")
            
            # Generate list of dates for the previous N months
            dates = []
            current_month = current_date.replace(day=1)
            
            for i in range(num_months):
                month_date = current_month - relativedelta(months=i+1)  # Start from previous month
                dates.append(month_date.strftime("%Y-%m-%d"))
            
            print(f"Debug - Date list for previous {num_months} months: {dates}")
            
            return {"created_date": {"$in": dates}}
            
        except Exception as e:
            print(f"Debug - Error parsing previous month range: {str(e)}")
    
    # Handle multiple specific dates like "Months: 2025-02-01, 2025-03-01, 2025-04-01, 2025-05-01"
    if "months:" in query_lower:
        try:
            # Extract dates after "Months:"
            months_match = re.search(r"months:\s*([0-9,\-\s]+)", query_lower)
            if months_match:
                date_string = months_match.group(1)
                # Extract all dates in YYYY-MM-DD format
                dates = re.findall(r"\d{4}-\d{2}-\d{2}", date_string)
                if dates:
                    print(f"Debug - Found multiple specific dates: {dates}")
                    return {"created_date": {"$in": dates}}
        except Exception as e:
            print(f"Debug - Error parsing multiple dates: {str(e)}")
    
    # Handle date ranges with "between"
    if "between" in query_lower and "and" in query_lower:
        try:
            date_pattern = r"between\s+(\d{4}-\d{2}-\d{2})\s+and\s+(\d{4}-\d{2}-\d{2})"
            matches = re.search(date_pattern, query_lower)
            if matches:
                start_date = datetime.strptime(matches.group(1), "%Y-%m-%d")
                end_date = datetime.strptime(matches.group(2), "%Y-%m-%d")
                
                # Generate list of first days of each month in the range
                dates = []
                current = start_date.replace(day=1)
                while current <= end_date:
                    dates.append(current.strftime("%Y-%m-%d"))
                    current = current + relativedelta(months=1)
                
                print(f"Debug - Date list for range: {dates}")
                return {"created_date": {"$in": dates}}
        except Exception as e:
            print(f"Debug - Error parsing date range: {str(e)}")
    
    # Handle orchestrator's start-date end-date format
    if "start-" in query_lower and "end-" in query_lower:
        try:
            # Extract start and end dates
            start_match = re.search(r"start-(\d{4}-\d{2}-\d{2})", query_lower)
            end_match = re.search(r"end-(\d{4}-\d{2}-\d{2})", query_lower)
            
            if start_match and end_match:
                start_date = datetime.strptime(start_match.group(1), "%Y-%m-%d")
                end_date = datetime.strptime(end_match.group(1), "%Y-%m-%d")
                
                # Generate list of first days of each month in the range
                dates = []
                current = start_date.replace(day=1)
                while current <= end_date:
                    dates.append(current.strftime("%Y-%m-%d"))
                    current = current + relativedelta(months=1)
                
                print(f"Debug - Date list for start-end range: {dates}")
                return {"created_date": {"$in": dates}}
        except Exception as e:
            print(f"Debug - Error parsing start-end date range: {str(e)}")
    
    # Try to find a specific date in YYYY-MM-DD format ONLY if no month range was found
    if "month" not in query_lower:  # Only look for specific dates if not asking for months
        date_match = re.search(r"\d{4}-\d{2}-\d{2}", query_lower)
        if date_match:
            date_str = date_match.group(0)
            print(f"Debug - Specific date found: {date_str}")
            return {"created_date": date_str}
        
    print("Debug - No date filter found in query")
    return None

def parse_query_string(query_str: str) -> Dict:
    """Parse the query string to extract time period, department and KPI name"""
    result = {
        "kpi_name": None,
        "department": None,
        "date_range": None,
        "start_date": None,
        "end_date": None
    }
    
    # Extract any dates first
    date_filter = get_date_filter(query_str)
    if date_filter:
        if "$and" in date_filter:
            result["start_date"] = date_filter["$and"][0]["created_date"]["$gte"]
            result["end_date"] = date_filter["$and"][1]["created_date"]["$lte"]
        else:
            # Single date
            result["start_date"] = date_filter["created_date"]
            result["end_date"] = date_filter["created_date"]
    
    print(f"Debug - Parsed dates: start={result['start_date']}, end={result['end_date']}")
    return result

def validate_kpi_data(metadata: dict) -> tuple[bool, str]:
    """
    Only validates the date format of KPI data.
    Returns (is_valid, error_message).
    """
    # Only check if date exists and is valid
    try:
        if not metadata.get("created_date"):
            return False, "Missing date"
        datetime.strptime(metadata["created_date"], "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, f"Invalid date format: {metadata['created_date']}"

def validate_query_params(params: dict) -> tuple[bool, str]:
    """
    Only validates date parameters if provided.
    Returns (is_valid, error_message).
    """
    # Only validate dates if they are provided
    if params["start_date"]:
        try:
            datetime.strptime(params["start_date"], "%Y-%m-%d")
        except ValueError:
            return False, f"Invalid start date format: {params['start_date']}"
            
    if params["end_date"]:
        try:
            datetime.strptime(params["end_date"], "%Y-%m-%d")
        except ValueError:
            return False, f"Invalid end date format: {params['end_date']}"
            
    return True, ""

def fetch_kpi(query_str: str) -> Dict:
    """
    Fetches KPI data using semantic search with date filtering.
    Now handles simple queries like "home-loan attrition rate last month" directly.
    """
    try:
        print(f"\n🔥 RAW KPI INPUT - Processing KPI request:")
        print(f"📝 Query Type: {type(query_str)}")
        print(f"📦 Query Size: {len(str(query_str))} characters")
        print(f"🔥 RAW COMPLETE QUERY:")
        print(f"{'='*50}")
        print(str(query_str))
        print(f"{'='*50}")
        
        # Check if this is a natural language query like "home-loan attrition rate last month"
        query_lower = query_str.lower()
        print(f"🔥 RAW QUERY LOWER: {query_lower}")
        
        # Handle natural language queries directly with dynamic number extraction
        if any(phrase in query_lower for phrase in ["as of today", "today", "current", "now", "this month", "current month"]):
            current_date = datetime.now()
            current_month = current_date.replace(day=1)
            date_filter = {"created_date": current_month.strftime("%Y-%m-%d")}
            print(f"🔥 RAW DATE FILTER (current/today): {date_filter}")
        elif any(phrase in query_lower for phrase in ["last month", "previous month"]):
            current_date = datetime.now()
            last_month = current_date.replace(day=1) - relativedelta(months=1)
            date_filter = {"created_date": last_month.strftime("%Y-%m-%d")}
            print(f"🔥 RAW DATE FILTER (last month): {date_filter}")
        elif any(phrase in query_lower for phrase in ["past", "last", "previous"]) and ("month" in query_lower or "year" in query_lower):
            # Dynamic extraction of number and time unit
            try:
                # Extract number of months/years using regex
                if "year" in query_lower:
                    # Handle years - convert to months
                    year_match = re.search(r"(?:past|last|previous)\s+(\d+)\s*years?", query_lower)
                    if year_match:
                        num_years = int(year_match.group(1))
                        num_months = num_years * 12
                        time_unit = f"{num_years} year{'s' if num_years > 1 else ''}"
                    else:
                        # Handle "past year" or "last year" without number
                        num_months = 12
                        time_unit = "1 year"
                elif "month" in query_lower:
                    # Handle months
                    month_match = re.search(r"(?:past|last|previous)\s+(\d+)\s*months?", query_lower)
                    if month_match:
                        num_months = int(month_match.group(1))
                        time_unit = f"{num_months} month{'s' if num_months > 1 else ''}"
                    else:
                        # Default to 1 month if no number specified
                        num_months = 1
                        time_unit = "1 month"
                else:
                    num_months = 1
                    time_unit = "1 month"
                
                print(f"🔥 RAW TIME EXTRACTION: {time_unit} ({num_months} months)")
                
                # Generate list of dates for the extracted time period
                current_date = datetime.now()
                dates = []
                current_month = current_date.replace(day=1)
                
                for i in range(num_months):
                    month_date = current_month - relativedelta(months=i+1)
                    dates.append(month_date.strftime("%Y-%m-%d"))
                
                date_filter = {"created_date": {"$in": dates}}
                print(f"🔥 RAW DATE FILTER (dynamic): {date_filter}")
                
            except Exception as e:
                print(f"🔥 RAW DATE PARSING ERROR: {e}")
                # Fallback to existing logic
                date_filter = get_date_filter(query_str)
        else:
            # Use existing date parsing logic
            date_filter = get_date_filter(query_str)
            
        print(f"🔥 RAW FINAL DATE FILTER: {date_filter}")
            
        if not date_filter:
            return {
                "error": """Please specify a time period for the KPI data. You can use:
- A specific date (YYYY-MM-DD)
- A date range ("between YYYY-MM-DD and YYYY-MM-DD")
- Relative periods ("last X months", "last month")"""
            }
        
        # Get collection
        client = get_chroma_client()
        collections = client.list_collections()
        
        if 'kpi_data' not in [c.name for c in collections]:
            return {
                "error": "KPI data collection not found. Please ensure the data has been loaded."
            }
            
        collection = client.get_collection(name="kpi_data")
        collection_count = collection.count()
        print(f"🔥 RAW DATABASE - Using KPI collection with {collection_count} records")
        
        # Query with semantic search
        query_embedding = get_gemini_embedding(query_str)
        print(f"🔥 RAW EMBEDDING LENGTH: {len(query_embedding) if query_embedding else 'None'}")
        
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": 50,  # Increased to get more results across the date range
            "include": ["metadatas", "distances", "documents"],
            "where": date_filter  # Use the date filter directly
        }
        
        print(f"🔥 RAW QUERY PARAMS:")
        for key, value in query_params.items():
            if key == "query_embeddings":
                print(f"   🔑 [{key}]: [embedding_vector_length_{len(value[0]) if value and value[0] else 0}]")
            else:
                print(f"   🔑 [{key}]: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
        
        print("🔥 RAW DATABASE - Querying vector database...")
        results = collection.query(**query_params)
        
        # 🔥 RAW VECTOR DATABASE RESULTS DUMP
        print(f"🔥 RAW KPI VECTOR DB RESULTS - COMPLETE DUMP:")
        print(f"📝 Results Type: {type(results)}")
        print(f"🔑 Results Keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
        
        if results and isinstance(results, dict):
            for key, value in results.items():
                print(f"🔥 RAW KPI VECTOR [{key}]:")
                if isinstance(value, list) and value:
                    print(f"   📊 Length: {len(value)}")
                    if value[0]:  # Check if first element exists and is not empty
                        print(f"   📊 First element length: {len(value[0])}")
                        for i, item in enumerate(value[0][:3]):  # Show first 3 items from first list
                            print(f"   📋 Item [{i}]: {str(item)[:300]}{'...' if len(str(item)) > 300 else ''}")
                else:
                    print(f"   📝 Value: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
        
        if not results or not results['metadatas'][0]:
            return {
                "error": f"No data found for the specified time period"
            }
            
        print(f"🔥 RAW RESULTS COUNT: Found {len(results['metadatas'][0])} total results")
        
        # Format results with minimal validation - just get top 5
        formatted_results = []
        for i, (metadata, distance, document) in enumerate(zip(results['metadatas'][0], results['distances'][0], results['documents'][0])):
            print(f"🔥 RAW KPI RESULT [{i+1}]:")
            print(f"   📊 Distance: {distance:.3f}")
            print(f"   📊 Confidence: {(1-distance)*100:.1f}%")
            print(f"   🏷️ Metadata: {metadata}")
            print(f"   📄 Document: {str(document)[:200]}{'...' if len(str(document)) > 200 else ''}")
            
            # Only basic field validation
            if not all(key in metadata for key in ["kpi_name", "department", "kpi_value", "created_date"]):
                print(f"🔥 RAW SKIP - Missing fields: {metadata}")
                continue
                
            print(f"🔥 RAW MATCH - {metadata['kpi_name']} - {metadata['department']}")
                
            # Basic value validation
            try:
                value = float(metadata["kpi_value"])
                print(f"🔥 RAW VALUE: {value}")
            except (ValueError, TypeError):
                print(f"🔥 RAW SKIP - Invalid value: {metadata['kpi_value']}")
                continue
                
            # Basic date validation
            is_valid, error = validate_kpi_data(metadata)
            if not is_valid:
                print(f"🔥 RAW SKIP - Date validation: {error}")
                continue
                
            formatted_result = {
                "kpi": metadata["kpi_name"],
                "department": metadata["department"],
                "value": value,
                "date": metadata["created_date"],
                "confidence": round((1 - distance) * 100, 2)
            }
            formatted_results.append(formatted_result)
            print(f"🔥 RAW ADDED: {formatted_result}")
            
            # Limit to top 5 results
            if len(formatted_results) >= 5:
                break
        
        if not formatted_results:
            return {
                "error": "No matching KPI data found for your query."
            }
        
        # Sort by confidence (highest first)
        formatted_results.sort(key=lambda x: x["confidence"], reverse=True)
        print(f"🔥 RAW SORTED RESULTS: {len(formatted_results)} results")
        
        # 🤖 INTELLIGENT CONVERSATIONAL PROCESSING AGENT
        print("🔥 RAW KPI PROCESSING - Creating intelligent agent...")
        
        # Create intelligent processing agent for KPI results
        processing_agent = ConversableAgent(
            name="KPI-Processing-Agent",
            llm_config=llm_config,
            system_message=f"""You are an intelligent KPI results filter and processor. Your job is to:

1. **FILTER RELEVANTLY**: Analyze the user's query and only select KPIs that actually match what they're asking for
2. **PRIORITIZE BY INTENT**: Focus on what the user specifically requested, not just highest confidence scores
3. **CREATE CONVERSATIONAL RESPONSE**: Format the filtered results in a business-intelligent way

**USER'S ORIGINAL QUERY**: "{query_str}"

**YOUR FILTERING LOGIC**:
- If user asks for "attrition rate", prioritize attrition-related KPIs
- If user asks for "home loan", prioritize home loan department KPIs  
- If user asks for "last month", focus on the most recent data
- If user asks for a specific metric, filter out unrelated metrics
- Only return 3-5 most relevant KPIs, not all results

**BUSINESS CONTEXT**: 
- You're analyzing performance metrics for banking/fintech operations
- High attrition rates (>12%) indicate potential issues
- Default rates >5% require attention
- Early repayment >50% may suggest competitive pressures

**OUTPUT FORMAT**: Create a natural, conversational response that:
- **ONLY INCLUDES RELEVANT KPIs** that match the user's query
- Explains business significance of the selected KPIs
- Suggests potential actions or concerns
- Uses the exact numbers provided in the results
- Groups related metrics logically

**CRITICAL FILTERING RULES**:
1. **MATCH USER INTENT**: If they ask for "attrition", don't include default rates unless highly relevant
2. **LIMIT RESULTS**: Return only 3-5 most relevant KPIs, not all available
3. **NO DUMMY DATA**: Use ONLY the provided KPI results below
4. **EXPLAIN SELECTIONS**: Briefly mention why these KPIs are relevant to the user's query

**AVAILABLE KPI RESULTS TO FILTER FROM**:""",
            human_input_mode="NEVER"
        )
        
        # Prepare context for processing agent
        results_context = f"""USER QUERY: {query_str}

KPI SEARCH RESULTS ({len(formatted_results)} matches):

"""
        
        for result in formatted_results:
            results_context += f"""• **{result['kpi']}** ({result['department']})
  Value: {result['value']}
  Date: {result['date']}
  Confidence: {result['confidence']}%

"""
        
        results_context += """
TASK: Filter and present only the KPIs that match the user's specific query. Create a conversational business analysis focusing on the most relevant metrics. Include business context and actionable insights."""
        
        # 🔥 RAW AGENT CONTEXT DUMP
        print(f"🔥 RAW KPI AGENT CONTEXT:")
        print(f"{'='*50}")
        print(results_context)
        print(f"{'='*50}")
        
        # Get intelligent processing
        try:
            response = processing_agent.generate_reply(
                messages=[{"role": "user", "content": results_context}]
            )
            
            # 🔥 RAW AGENT RESPONSE DUMP
            print(f"🔥 RAW KPI AGENT RESPONSE:")
            print(f"📝 Response Type: {type(response)}")
            print(f"📄 Response Content:")
            print(f"{'='*50}")
            print(str(response))
            print(f"{'='*50}")
            
            if isinstance(response, dict) and 'content' in response:
                processed_content = response['content']
            elif isinstance(response, str):
                processed_content = response
            else:
                processed_content = str(response)
            
            print(f"🔥 RAW KPI PROCESSED CONTENT:")
            print(f"📄 Final Content: {processed_content[:400]}{'...' if len(processed_content) > 400 else ''}")
            
            # 📊 STORE IN VECTOR DATA STORE FOR VISUALIZATION ACCESS
            if _vector_data_store and _current_session_id:
                try:
                    # Store the processed KPI result in the data store
                    entry_id = _vector_data_store.store_search_result(
                        session_id=_current_session_id,
                        query_type="kpi",
                        business="mixed",  # KPIs can span multiple departments
                        substream="performance_metrics",
                        team="all_departments",
                        result_data={
                            "kpi_results": formatted_results,
                            "processed_response": processed_content,
                            "query": query_str,
                            "top_kpi": formatted_results[0] if formatted_results else None
                        },
                        metadata={
                            "total_results": len(formatted_results),
                            "top_confidence": formatted_results[0]['confidence'] if formatted_results else 0,
                            "departments": list(set([r['department'] for r in formatted_results])),
                            "query_type": "kpi_analysis"
                        }
                    )
                    print(f"✅ Stored KPI data in vector data store: {entry_id}")
                except Exception as store_error:
                    print(f"⚠️ Failed to store KPI data in vector data store: {store_error}")
            else:
                print("⚠️ Vector data store not available for KPI results - skipping storage")
            
            # Return the processed content
            return {"results": processed_content}
            
        except Exception as e:
            print(f"🔥 RAW KPI PROCESSING ERROR: {str(e)}")
            # Fallback if agent processing fails
            response = f"""📊 **KPI Analysis Results** (Query: "{query_str}")

Found {len(formatted_results)} matching KPIs:

"""
            for result in formatted_results:
                response += f"• **{result['kpi']}** ({result['department']}): {result['value']} ({result['date']})\n"
            
            # Still try to store in vector data store even with fallback
            if _vector_data_store and _current_session_id:
                try:
                    entry_id = _vector_data_store.store_search_result(
                        session_id=_current_session_id,
                        query_type="kpi",
                        business="mixed",
                        substream="performance_metrics", 
                        team="all_departments",
                        result_data={
                            "kpi_results": formatted_results,
                            "processed_response": response,
                            "query": query_str
                        },
                        metadata={
                            "total_results": len(formatted_results),
                            "fallback_processing": True
                        }
                    )
                    print(f"✅ Stored KPI data (fallback) in vector data store: {entry_id}")
                except Exception as store_error:
                    print(f"⚠️ Failed to store KPI fallback data: {store_error}")
                    
            return {"results": response}
        
    except Exception as e:
        print(f"🔥 RAW KPI ERROR: {e}")
        import traceback
        print(traceback.format_exc())
        return {
            "error": f"Error fetching data: {str(e)}"
        }

def create_agent():
    kpi_agent = ConversableAgent(
        name="KPI-Data-Agent",
        llm_config=llm_config,
        system_message=kpi_agent_system_message,
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        human_input_mode="NEVER",
    )
    
    # Register the fetch_kpi function properly with AutoGen
    kpi_agent.register_for_execution()(fetch_kpi)
    kpi_agent.register_for_llm(description="Fetch KPI data based on user query with date filtering")(fetch_kpi)
    
    return kpi_agent 