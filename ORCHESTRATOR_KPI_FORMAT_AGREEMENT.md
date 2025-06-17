# Orchestrator-KPI Agent Format Agreement

## Supported Query Formats

### 1. Single Month Query
**Format:** `kpi-{kpi_name} department-{department} month-{YYYY-MM-DD}`
**Example:** `kpi-attrition-rate department-home-loan month-2025-05-01`
**Usage:** When user asks for a specific month

### 2. Date Range Query  
**Format:** `kpi-{kpi_name} department-{department} start-{YYYY-MM-DD} end-{YYYY-MM-DD}`
**Example:** `kpi-attrition-rate department-home-loan start-2025-02-01 end-2025-05-31`
**Usage:** When user asks for a date range or "last X months"

### 3. Range with Additional Info
**Format:** `kpi-{kpi_name} department-{department} range-{X}-months start-{YYYY-MM-DD} end-{YYYY-MM-DD}`
**Example:** `kpi-attrition-rate department-home-loan range-4-months start-2025-02-01 end-2025-05-31`
**Usage:** When user asks for "last X months" with additional context

## Natural Language Handling

### Supported User Inputs:
- "last month" → Generate single month query
- "last X months" → Generate date range query  
- "previous month" → Generate single month query
- "previous X months" → Generate date range query
- Specific date → Generate single month query
- Date range → Generate date range query

## Orchestrator Responsibilities:
1. Parse user's natural language request
2. Convert to agreed format structure
3. Calculate appropriate dates based on current date
4. Send properly formatted query to KPI agent

## KPI Agent Responsibilities:
1. Parse the structured query format
2. Extract dates using defined patterns:
   - `month-(\d{4}-\d{2}-\d{2})` for single dates
   - `start-(\d{4}-\d{2}-\d{2})` and `end-(\d{4}-\d{2}-\d{2})` for ranges
   - `last|previous \d+ months?` for natural language
3. Query ChromaDB with appropriate filters
4. Return formatted results

## Error Handling:
- If date parsing fails, return structured error message
- If no data found, return "No data found for specified period"  
- If query format is invalid, request proper format

## Date Calculation Rules:
- "last month" = previous calendar month (e.g., if current is June 2025, return May 2025)
- "last X months" = previous X calendar months from current date
- Always use first day of month (YYYY-MM-01) for consistency
- Date ranges are inclusive of start and end months

## Testing Formats:
All these should work correctly:
- `kpi-attrition-rate department-home-loan month-2025-05-01`
- `kpi-attrition-rate department-home-loan start-2025-02-01 end-2025-05-31`  
- `home-loan attrition rate last month`
- `home-loan attrition rate previous 4 months`
- `kpi-attrition-rate department-home-loan range-4-months start-2025-02-01 end-2025-05-31` 