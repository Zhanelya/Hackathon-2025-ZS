"""Main MCP server for travel requirements."""

import asyncio
import logging
from typing import Any, Sequence
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
# Local imports
try:
    from .requirements_service import TravelRequirementsService
except ImportError:
    # Handle case when running as script
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from requirements_service import TravelRequirementsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("travel-requirements-mcp")

# Initialize service
requirements_service = TravelRequirementsService()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="get_airport_security_rules",
            description="Get airport security rules and prohibited/restricted items",
            inputSchema={
                "type": "object",
                "properties": {
                    "airport_code": {
                        "type": "string",
                        "description": "IATA airport code (e.g., LAX, JFK)"
                    },
                    "country_code": {
                        "type": "string",
                        "description": "ISO 2-letter country code (e.g., US, GB)"
                    },
                    "airline": {
                        "type": "string",
                        "description": "Optional airline code"
                    },
                    "cabin_class": {
                        "type": "string",
                        "description": "Optional cabin class (economy, business, first)"
                    }
                },
                "required": ["airport_code", "country_code"]
            }
        ),
        types.Tool(
            name="check_baggage_allowance",
            description="Check airline baggage size, weight, and quantity limits",
            inputSchema={
                "type": "object",
                "properties": {
                    "airline": {
                        "type": "string",
                        "description": "Airline code (e.g., UA, BA, LH)"
                    },
                    "cabin_class": {
                        "type": "string",
                        "description": "Cabin class (economy, premium_economy, business, first)"
                    },
                    "route": {
                        "type": "string",
                        "description": "Route (origin-destination, e.g., LAX-LHR)"
                    },
                    "fare_brand": {
                        "type": "string",
                        "description": "Optional fare brand/type"
                    }
                },
                "required": ["airline", "cabin_class", "route"]
            }
        ),
        types.Tool(
            name="get_visa_requirements",
            description="Get visa and entry requirements for destination",
            inputSchema={
                "type": "object",
                "properties": {
                    "nationality": {
                        "type": "string",
                        "description": "Traveler nationality (ISO 2-letter code, e.g., US, DE)"
                    },
                    "destination_country": {
                        "type": "string",
                        "description": "Destination country (ISO 2-letter code, e.g., JP, FR)"
                    },
                    "transit_countries": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of transit countries"
                    },
                    "stay_length_days": {
                        "type": "integer",
                        "description": "Length of stay in days",
                        "default": 7
                    },
                    "purpose": {
                        "type": "string",
                        "description": "Purpose of travel (tourism, business, etc.)",
                        "default": "tourism"
                    }
                },
                "required": ["nationality", "destination_country"]
            }
        ),
        types.Tool(
            name="get_documents_checklist",
            description="Get required and recommended travel documents checklist",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination_country": {
                        "type": "string",
                        "description": "Destination country (ISO 2-letter code)"
                    },
                    "nationality": {
                        "type": "string",
                        "description": "Traveler nationality (ISO 2-letter code)"
                    },
                    "minors_traveling": {
                        "type": "boolean",
                        "description": "Whether minors are traveling",
                        "default": False
                    },
                    "driving": {
                        "type": "boolean", 
                        "description": "Whether planning to drive",
                        "default": False
                    },
                    "insurance": {
                        "type": "boolean",
                        "description": "Whether travel insurance is desired",
                        "default": True
                    }
                },
                "required": ["destination_country", "nationality"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Handle tool calls."""
    if not arguments:
        arguments = {}
    
    try:
        if name == "get_airport_security_rules":
            result = await requirements_service.get_airport_security_rules(
                airport_code=arguments["airport_code"],
                country_code=arguments["country_code"],
                airline=arguments.get("airline"),
                cabin_class=arguments.get("cabin_class")
            )
        
        elif name == "check_baggage_allowance":
            result = await requirements_service.check_baggage_allowance(
                airline=arguments["airline"],
                cabin_class=arguments["cabin_class"],
                route=arguments["route"],
                fare_brand=arguments.get("fare_brand")
            )
        
        elif name == "get_visa_requirements":
            result = await requirements_service.get_visa_requirements(
                nationality=arguments["nationality"],
                destination_country=arguments["destination_country"],
                transit_countries=arguments.get("transit_countries", []),
                stay_length_days=arguments.get("stay_length_days", 7),
                purpose=arguments.get("purpose", "tourism")
            )
        
        elif name == "get_documents_checklist":
            result = await requirements_service.get_documents_checklist(
                destination_country=arguments["destination_country"],
                nationality=arguments["nationality"],
                minors_traveling=arguments.get("minors_traveling", False),
                driving=arguments.get("driving", False),
                insurance=arguments.get("insurance", True)
            )
        
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        # Format result as JSON string
        import json
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point for the server."""
    # Use stdin/stdout for communication
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="travel-requirements-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())