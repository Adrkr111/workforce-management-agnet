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

# Initialize ChromaDB client
chroma_client = get_chroma_client()

def get_date_filter(query: str) -> dict:
    """
    Extract date or date range from query and return ChromaDB filter
    """
    current_date = datetime.now()
    print(f"Debug - Processing date filter from query: {query}")
    print(f"Debug - Current date: {current_date}")
    
    query_lower = query.lower()
    
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
            print(f"Debug - Extracting data for last/past {num_years} year{'s' if num_years > 1 else ''} ({num_months} months)")
            
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
        print("\nDebug - KPI Agent - Starting KPI data fetch")
        print(f"Debug - Query string: {query_str}")
        
        # Check if this is a natural language query like "home-loan attrition rate last month"
        query_lower = query_str.lower()
        
        # Handle natural language queries directly with dynamic number extraction
        if any(phrase in query_lower for phrase in ["last month", "previous month"]):
            current_date = datetime.now()
            last_month = current_date.replace(day=1) - relativedelta(months=1)
            date_filter = {"created_date": last_month.strftime("%Y-%m-%d")}
            print(f"Debug - Natural language: last month = {last_month.strftime('%Y-%m-%d')}")
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
                
                print(f"Debug - Extracting data for {time_unit} ({num_months} months)")
                
                # Generate list of dates for the extracted time period
                current_date = datetime.now()
                dates = []
                current_month = current_date.replace(day=1)
                
                for i in range(num_months):
                    month_date = current_month - relativedelta(months=i+1)
                    dates.append(month_date.strftime("%Y-%m-%d"))
                
                date_filter = {"created_date": {"$in": dates}}
                print(f"Debug - Natural language: {time_unit} = {dates}")
                
            except Exception as e:
                print(f"Debug - Error in dynamic date parsing: {e}")
                # Fallback to existing logic
                date_filter = get_date_filter(query_str)
        else:
            # Use existing date parsing logic
            date_filter = get_date_filter(query_str)
            
        if not date_filter:
            return {
                "error": """Please specify a time period for the KPI data. You can use:
- A specific date (YYYY-MM-DD)
- A date range ("between YYYY-MM-DD and YYYY-MM-DD")
- Relative periods ("last X months", "last month")"""
            }
            
        print(f"Debug - Date filter: {date_filter}")
        
        # Get collection
        client = get_chroma_client()
        collections = client.list_collections()
        
        if 'kpi_data' not in [c.name for c in collections]:
            return {
                "error": "KPI data collection not found. Please ensure the data has been loaded."
            }
            
        collection = client.get_collection(name="kpi_data")
        collection_count = collection.count()
        print(f"Debug - Using KPI data collection with {collection_count} records")
        
        # Query with semantic search
        query_embedding = get_gemini_embedding(query_str)
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": 50,  # Increased to get more results across the date range
            "include": ["metadatas", "distances", "documents"],
            "where": date_filter  # Use the date filter directly
        }
        
        print(f"Debug - Query parameters: {query_params}")
        results = collection.query(**query_params)
        
        if not results or not results['metadatas'][0]:
            return {
                "error": f"No data found for the specified time period"
            }
            
        print(f"Debug - Found {len(results['metadatas'][0])} total results")
        
        # Format results with minimal validation - just get top 5
        formatted_results = []
        for metadata, distance, document in zip(results['metadatas'][0], results['distances'][0], results['documents'][0]):
            # Only basic field validation
            if not all(key in metadata for key in ["kpi_name", "department", "kpi_value", "created_date"]):
                print(f"Debug - Skipping record due to missing fields: {metadata}")
                continue
                
            print(f"Debug - Found matching record: {metadata['kpi_name']} - {metadata['department']}")
                
            # Basic value validation
            try:
                value = float(metadata["kpi_value"])
            except (ValueError, TypeError):
                print(f"Debug - Skipping record due to invalid value format: {metadata['kpi_value']}")
                continue
                
            # Basic date validation
            is_valid, error = validate_kpi_data(metadata)
            if not is_valid:
                print(f"Debug - Skipping record due to date validation: {error}")
                continue
                
            formatted_results.append({
                "kpi": metadata["kpi_name"],
                "department": metadata["department"],
                "value": value,
                "date": metadata["created_date"],
                "confidence": round((1 - distance) * 100, 2)
            })
            print(f"Debug - Added valid record: {formatted_results[-1]}")
            
            # Limit to top 5 results
            if len(formatted_results) >= 5:
                break
        
        if not formatted_results:
            return {
                "error": "No matching KPI data found for your query."
            }
        
        # Sort by confidence (highest first)
        formatted_results.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Generate clean human-readable response
        response = f"📊 **Top {len(formatted_results)} KPI Results**\n\n"

        for i, result in enumerate(formatted_results, 1):
            response += f"**{i}. {result['kpi']}**\n"
            response += f"   • Department: {result['department']}\n"
            response += f"   • Value: {result['value']:.2f}%\n"
            response += f"   • Date: {result['date']}\n"
            response += f"   • Match Confidence: {result['confidence']:.1f}%\n\n"
            
        response += f"📈 **Summary**: Found {len(formatted_results)} relevant KPIs from {collection_count} total records\n"
        response += f"🎯 **Best Match**: {formatted_results[0]['kpi']} ({formatted_results[0]['confidence']:.1f}% confidence)"
            
        print(f"Debug - Retrieved {len(formatted_results)} top results")
        return {"results": response}
        
    except Exception as e:
        print(f"Error in fetch_kpi: {e}")
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
        function_map={
            "fetch_kpi": fetch_kpi
        }
    )
    return kpi_agent 