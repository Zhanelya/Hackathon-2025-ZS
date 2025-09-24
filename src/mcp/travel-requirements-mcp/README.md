# Travel Requirements MCP Server

## Overview
HTTP MCP server providing travel regulatory information and requirements checking.

## Tools
- `get_airport_security_rules` - Get prohibited/restricted items for airport security
- `check_baggage_allowance` - Check airline baggage size, weight, and quantity limits
- `get_visa_requirements` - Get visa/entry requirements for destinations
- `get_documents_checklist` - Get required travel documents checklist

## Phase 1 Mode
All responses use mocked/fixture data. No external HTTP calls are made.

## Usage
```bash
uvx --python 3.13 --from . travel-requirements-mcp
```