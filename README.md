# Duke Calendar MCP Server

## Project Overview

The Duke Calendar MCP (Multi-purpose Communication Protocol) Server is a FastAPI application that provides LLM-powered natural language querying for Duke University's calendar events. This project bridges the complex, messy data from Duke's Bedework calendar API with a user-friendly natural language interface, enabling users to find relevant events through simple queries like "what's happening in the arts today?" or "are there any engineering lectures this week?"

## Challenges and Strategy

### Calendar API Challenges

The Duke Calendar API presented several significant challenges:

1. **Data Volume & Quality Issues**: 
   - Thousands of groups/sponsors (many orphaned)
   - Hundreds of categories (ad-hoc additions with minimal governance)
   - Inconsistent data entry (especially with locations and descriptions)
   - Long, unwieldy canonical IDs that consume LLM tokens

2. **Complex Hierarchies**:
   - No clear organizational structure for navigating events
   - Difficult to map user queries to specific categories or groups
   - Traditional filtering approaches break down with this level of complexity

3. **Time-bound Data**:
   - Calendar data is inherently time-sensitive
   - Need to translate natural language time expressions (e.g., "next weekend") to API parameters

### Our Solution Strategy

We adopted a two-stage approach that leverages both efficient data management and LLM capabilities:

1. **Simplified Data Model**:
   - Implemented a caching layer that refreshes data periodically (every hour)
   - Created a local_id system to replace lengthy canonical IDs
   - Defined a streamlined event representation with essential fields
   - Removed inconsistent fields (e.g., location) from LLM decision-making

2. **LLM-Optimized Query Process**:
   - Step 1: Convert natural language time queries to ISO date ranges
   - Step 2: Fetch simplified event data for that date range
   - Step 3: Let the LLM analyze and select relevant events
   - Step 4: Retrieve full details only for selected events
   - Step 5: Present results in a user-friendly format

3. **Token Efficiency**:
   - Using local_ids instead of canonical IDs
   - Batching multiple event IDs into a single API call
   - Truncating lengthy descriptions
   - Excluding irrelevant or inconsistent fields

4. **Handling Large Result Sets**:
   - Implementing categorization and summarization strategies
   - Grouping events by day or category when appropriate
   - Highlighting most relevant events rather than showing all

## System Architecture

The system consists of three main components:

### 1. MCP Server (FastAPI Backend)

The MCP server handles data retrieval, caching, and API endpoints:

- **Cache Management**: Refreshes event data from Duke Calendar API periodically
- **ID Mapping**: Maintains mappings between local_ids and canonical IDs
- **API Endpoints**:
  - `/simplified-events`: Returns compact event data for a date range
  - `/events-by-local-ids`: Returns full event details for selected events

### 2. OpenWebUI Tool

A custom tool for OpenWebUI that enables LLMs to:

- Parse natural language time expressions
- Retrieve simplified events
- Analyze and select relevant events
- Fetch detailed information
- Format responses appropriately

### 3. LLM Integration (e.g., GPT-4o-mini)

The LLM:
- Interprets user queries
- Makes decisions about which events are relevant
- Formats the response appropriately
- Handles large result sets with summarization strategies

## Code Structure

- `app/`: FastAPI application
  - `main.py`: Application entry point
  - `config.py`: Configuration settings
  - `models.py`: Data models (EventData, SimplifiedEvent, etc.)
  - `mcp.py`: CalendarMCP class for data management
  - `routers/`: API route definitions
    - `calendar.py`: Calendar endpoint handlers

- `duke_calendar_tool.py`: OpenWebUI tool implementation

## API Endpoints

### GET /api/v1/calendar/simplified-events

Returns simplified events for a date range.

**Parameters:**
- `start_date`: ISO format date (YYYY-MM-DD)
- `end_date`: ISO format date (YYYY-MM-DD)

**Response:**
```json
{
  "events": [
    {
      "local_id": 1,
      "title": "Event Title",
      "groups": "Sponsor Group",
      "categories": ["Category1", "Category2"],
      "description": "Truncated description...",
      "start_time": "2025-03-30T15:00:00Z"
    },
    ...
  ],
  "count": 5,
  "date_range": {"start": "2025-03-30", "end": "2025-03-30"}
}
```

### POST /api/v1/calendar/events-by-local-ids

Returns full event details for specified local IDs.

**Request Body:**
```json
{
  "local_ids": [1, 5, 9]
}
```

**Response:**
```json
{
  "events": [
    {
      "id": "CAL-8a008ae5-8f05e4c1-018f-078609f6-00000dbcdemobedework@mysite.edu_20250330T150000Z",
      "local_id": 1,
      "start_timestamp": "2025-03-30T15:00:00Z",
      "end_timestamp": "2025-03-30T16:00:00Z",
      "summary": "Event Title",
      "description": "Full description...",
      "status": "CONFIRMED",
      "sponsor": "Sponsor Group",
      "co_sponsors": ["Co-sponsor 1", "Co-sponsor 2"],
      "location": {
        "address": "Location Name",
        "link": "https://maps.duke.edu/?focus=290"
      },
      "contact": {
        "name": "Contact Name",
        "email": "contact@duke.edu",
        "phone": "123-456-7890"
      },
      "categories": ["Category1", "Category2"],
      "link": "https://calendar.duke.edu/show?fq=id:CAL-8a008ae5...",
      "event_url": "https://example.com/event"
    },
    ...
  ],
  "count": 3
}
```

## Usage Examples

### Natural Language Queries

The system can handle queries like:

- "What arts events are happening this weekend?"
- "Are there any engineering lectures tomorrow?"
- "Show me all biomedical seminars next week"
- "What's happening in the chapel today?"

### Response Handling

For small result sets (1-5 events), the LLM provides detailed information about each event.

For larger result sets, the LLM:
1. Categorizes and summarizes events
2. Highlights most relevant events
3. Groups by day or category
4. Offers filtering suggestions

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/duke-calendar-mcp.git
   cd duke-calendar-mcp
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   DUKE_CALENDAR_API_URL=https://calendar.duke.edu/events/index.json
   DEBUG=False
   REFERENCE_CACHE_TTL=3600
   ```

4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Register the OpenWebUI tool in your OpenWebUI instance

## Future Improvements

1. **Natural Language Understanding**:
   - Add sentiment analysis to better understand user preferences
   - Implement contextual understanding to improve follow-up queries

2. **Data Quality**:
   - Develop heuristics to standardize location information
   - Implement named entity recognition to improve category mapping

3. **User Experience**:
   - Create user profiles to personalize event recommendations
   - Add relevance feedback mechanisms to improve future queries

4. **Performance Optimizations**:
   - Implement more sophisticated caching strategies
   - Add predictive pre-fetching for common queries

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.# mcp_calendar

