# Booking MCP Server

## Overview
HTTP MCP server providing travel booking search and reservation capabilities.

## Tools
- `search_flights` - Search for flight options
- `search_hotels` - Search for hotel accommodations
- `search_activities` - Search for activities and attractions
- `hold_booking` - Place a booking on hold (requires confirmation)
- `confirm_booking` - Confirm a held booking

## Phase 1 Mode
All responses use sandbox/mock providers with 'DEMO ONLY' flags. No real bookings are made.

## Usage
```bash
uvx --python 3.13 --from . booking-mcp
```