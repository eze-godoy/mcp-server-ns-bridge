"""MCP Server for Netherlands NS Trains."""

import logging
import traceback
from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP

from ns_bridge.config import get_settings
from ns_bridge.models import DiscountType, TravelClass
from ns_bridge.ns_api_client import NSAPIClient, NSAPIError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("ns-bridge")

# Global API client instance
_api_client: NSAPIClient | None = None


def get_api_client() -> NSAPIClient:
    """Get or create the NS API client instance."""
    global _api_client  # noqa: PLW0603
    if _api_client is None:
        settings = get_settings()
        _api_client = NSAPIClient(settings)
    return _api_client


# MCP Tools


@mcp.tool()
async def search_stations(
    query: str | None = None,
    country_codes: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Search for train stations by name or filter by country.

    Use this tool to find station codes needed for trip planning.

    Args:
        query: Search query for station name (minimum 2 characters). Leave empty to list all stations.
        country_codes: Comma-separated country codes to filter (e.g., "nl,de,be"). Common codes: nl (Netherlands), de (Germany), be (Belgium)
        limit: Maximum number of results to return (default: 10, max: 100)

    Returns:
        A dictionary containing:
        - stations: List of matching stations with their codes and locations
        - count: Number of stations returned

    Example:
        search_stations(query="Amsterdam", limit=5)
        search_stations(country_codes="nl", limit=20)
    """
    try:
        client = get_api_client()

        # Parse country codes
        country_list = None
        if country_codes:
            country_list = [c.strip().lower() for c in country_codes.split(",")]

        # Search stations
        stations = await client.search_stations(
            query=query,
            country_codes=country_list,
            limit=min(limit, 100),  # Cap at 100
        )

        # Format response
        return {
            "count": len(stations),
            "stations": [
                {
                    "name": s.name,
                    "code": s.code,
                    "uic_code": s.uic_code,
                    "country": s.country_code,
                    "location": {"lat": s.lat, "lng": s.lng} if s.lat and s.lng else None,
                }
                for s in stations
            ],
        }

    except NSAPIError as e:
        return {"error": str(e), "stations": [], "count": 0}
    except Exception as e:
        logger.exception("Error searching stations")
        return {"error": f"Unexpected error: {e!s}", "stations": [], "count": 0}


@mcp.tool()
async def search_trips(
    origin: str,
    destination: str,
    date_time: str | None = None,
    search_for_arrival: bool = False,
    via_station: str | None = None,
    travel_class: str = "second",
    discount: str = "none",
    num_trips: int = 5,
) -> dict[str, Any]:
    """Search for train trips between two stations with pricing information.

    This is the main tool for route planning. It returns trip options with detailed
    information about connections, travel times, and prices.

    Args:
        origin: Origin station code (e.g., "ut" for Utrecht, "asd" for Amsterdam). Use search_stations to find codes.
        destination: Destination station code (e.g., "rtd" for Rotterdam). Use search_stations to find codes.
        date_time: Departure/arrival date and time in ISO format (e.g., "2025-11-18T14:30:00"). Defaults to current time.
        search_for_arrival: If true, date_time is treated as arrival time. If false (default), it's departure time.
        via_station: Optional intermediate station code to route through
        travel_class: Travel class - either "first" or "second" (default: "second")
        discount: Discount type - "none" (default), "20_percent", or "40_percent"
        num_trips: Number of trip options to return (default: 5)

    Returns:
        A dictionary containing:
        - trips: List of trip options, each with:
            - duration_minutes: Total travel time
            - transfers: Number of transfers required
            - departure_time: Planned departure time
            - arrival_time: Planned arrival time
            - status: Trip status (e.g., "NORMAL", "CANCELLED")
            - legs: List of individual journey segments
            - price: Fare information in cents and formatted
        - origin: Origin station name
        - destination: Destination station name

    Example:
        search_trips(origin="ut", destination="asd", num_trips=3)
        search_trips(origin="rtd", destination="ams", date_time="2025-11-20T09:00:00", travel_class="first")
    """
    try:
        client = get_api_client()

        # Parse travel class
        travel_class_enum = (
            TravelClass.FIRST if travel_class.lower() == "first" else TravelClass.SECOND
        )

        # Parse discount
        discount_map = {
            "none": DiscountType.NO_DISCOUNT,
            "20_percent": DiscountType.DISCOUNT_20_PERCENT,
            "40_percent": DiscountType.DISCOUNT_40_PERCENT,
        }
        discount_enum = discount_map.get(discount.lower(), DiscountType.NO_DISCOUNT)

        # Parse date_time
        dt = None
        if date_time:
            dt = datetime.fromisoformat(date_time)

        # Search trips
        result = await client.search_trips(
            origin_station=origin,
            destination_station=destination,
            date_time=dt,
            search_for_arrival=search_for_arrival,
            via_station=via_station,
            travel_class=travel_class_enum,
            discount=discount_enum,
        )

        # Format response
        formatted_trips = []
        for trip in result.trips[:num_trips]:
            # Get first and last leg for departure/arrival times
            first_leg = trip.legs[0] if trip.legs else None
            last_leg = trip.legs[-1] if trip.legs else None

            trip_data: dict[str, Any] = {
                "duration_minutes": trip.planned_duration_in_minutes,
                "transfers": trip.transfers,
                "status": trip.status,
                "legs": [],
            }

            # Add departure/arrival times (both planned and actual for delay detection)
            if first_leg:
                if first_leg.origin.planned_date_time:
                    trip_data["planned_departure_time"] = (
                        first_leg.origin.planned_date_time.isoformat()
                    )
                if first_leg.origin.actual_date_time:
                    trip_data["actual_departure_time"] = (
                        first_leg.origin.actual_date_time.isoformat()
                    )
                if first_leg.origin.planned_track:
                    trip_data["planned_departure_track"] = first_leg.origin.planned_track
                if first_leg.origin.actual_track:
                    trip_data["actual_departure_track"] = first_leg.origin.actual_track

            if last_leg:
                if last_leg.destination.planned_date_time:
                    trip_data["planned_arrival_time"] = (
                        last_leg.destination.planned_date_time.isoformat()
                    )
                if last_leg.destination.actual_date_time:
                    trip_data["actual_arrival_time"] = (
                        last_leg.destination.actual_date_time.isoformat()
                    )
                if last_leg.destination.planned_track:
                    trip_data["planned_arrival_track"] = last_leg.destination.planned_track
                if last_leg.destination.actual_track:
                    trip_data["actual_arrival_track"] = last_leg.destination.actual_track

            # Add legs
            for leg in trip.legs:
                leg_data: dict[str, Any] = {
                    "transport": leg.name,
                    "direction": leg.direction,
                    "origin": {
                        "name": leg.origin.name,
                    },
                    "destination": {
                        "name": leg.destination.name,
                    },
                    "cancelled": leg.cancelled,
                }

                # Add planned and actual times/tracks for origin
                if leg.origin.planned_date_time:
                    leg_data["origin"]["planned_time"] = leg.origin.planned_date_time.isoformat()
                if leg.origin.actual_date_time:
                    leg_data["origin"]["actual_time"] = leg.origin.actual_date_time.isoformat()
                if leg.origin.planned_track:
                    leg_data["origin"]["planned_track"] = leg.origin.planned_track
                if leg.origin.actual_track:
                    leg_data["origin"]["actual_track"] = leg.origin.actual_track

                # Add planned and actual times/tracks for destination
                if leg.destination.planned_date_time:
                    leg_data["destination"]["planned_time"] = (
                        leg.destination.planned_date_time.isoformat()
                    )
                if leg.destination.actual_date_time:
                    leg_data["destination"]["actual_time"] = (
                        leg.destination.actual_date_time.isoformat()
                    )
                if leg.destination.planned_track:
                    leg_data["destination"]["planned_track"] = leg.destination.planned_track
                if leg.destination.actual_track:
                    leg_data["destination"]["actual_track"] = leg.destination.actual_track

                if leg.product:
                    leg_data["operator"] = leg.product.operator_name
                    leg_data["type"] = leg.product.long_category_name

                trip_data["legs"].append(leg_data)

            # Add pricing if available (use product_fare which matches the requested class/discount)
            fare = trip.product_fare or trip.price
            if fare:
                trip_data["price"] = {
                    "total_cents": fare.price_in_cents,
                    "total_formatted": client.format_price(fare.price_in_cents),
                }

                # Add product type info
                if fare.product:
                    trip_data["price"]["product"] = fare.product
                if fare.travel_class:
                    trip_data["price"]["travel_class"] = fare.travel_class
                if fare.discount_type:
                    trip_data["price"]["discount_type"] = fare.discount_type

                # Add base price and supplement breakdown
                if fare.price_in_cents_excluding_supplement is not None:
                    trip_data["price"]["base_cents"] = fare.price_in_cents_excluding_supplement
                    trip_data["price"]["base_formatted"] = client.format_price(
                        fare.price_in_cents_excluding_supplement
                    )

                if fare.supplement_in_cents:
                    trip_data["price"]["supplement_cents"] = fare.supplement_in_cents
                    trip_data["price"]["supplement_formatted"] = client.format_price(
                        fare.supplement_in_cents
                    )

            formatted_trips.append(trip_data)

        return {
            "origin": origin,
            "destination": destination,
            "trips": formatted_trips,
            "count": len(formatted_trips),
        }

    except NSAPIError as e:
        # Include debug info in error response
        return {
            "error": str(e),
            "debug": {
                "origin": origin,
                "destination": destination,
                "travel_class": travel_class,
                "travel_class_int": 1 if travel_class.lower() == "first" else 2,
                "discount": discount,
                "date_time": date_time,
                "search_for_arrival": search_for_arrival,
                "via_station": via_station,
            },
            "trips": [],
            "count": 0,
        }
    except Exception as e:
        logger.exception("Error searching trips")
        # Get the raw API response if available

        return {
            "error": f"Unexpected error: {e!s}",
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "trips": [],
            "count": 0,
        }


@mcp.tool()
async def get_departures(
    station: str,
    max_journeys: int = 10,
    date_time: str | None = None,
) -> dict[str, Any]:
    """Get upcoming train departures for a specific station.

    Use this to check the departure board at a station, including real-time updates
    about delays, cancellations, and platform changes.

    Args:
        station: Station code (e.g., "ut" for Utrecht Centraal). Use search_stations to find codes.
        max_journeys: Maximum number of departures to return (default: 10, max: 40)
        date_time: Date and time to show departures from in ISO format. Defaults to current time.

    Returns:
        A dictionary containing:
        - station: Station code
        - departures: List of departures with:
            - direction: Destination of the train
            - name: Train identification (e.g., "Intercity 2800")
            - planned_time: Scheduled departure time
            - actual_time: Actual departure time (if different)
            - planned_track: Scheduled platform
            - actual_track: Actual platform (if changed)
            - cancelled: Whether the departure is cancelled
            - delay_minutes: Delay in minutes (if applicable)
        - count: Number of departures returned

    Example:
        get_departures(station="ut", max_journeys=5)
        get_departures(station="asd", date_time="2025-11-20T08:00:00")
    """
    try:
        client = get_api_client()

        # Parse date_time
        dt = None
        if date_time:
            dt = datetime.fromisoformat(date_time)

        # Get departures
        result = await client.get_departures(
            station=station,
            max_journeys=min(max_journeys, 40),  # Cap at 40
            date_time=dt,
        )

        # Format response
        formatted_departures = []
        for departure in result.payload.departures:
            dep_data: dict[str, Any] = {
                "direction": departure.direction,
                "name": departure.name,
                "planned_time": departure.planned_date_time.isoformat(),
                "planned_track": departure.planned_track,
                "cancelled": departure.cancelled,
            }

            # Add actual time if different
            if departure.actual_date_time:
                dep_data["actual_time"] = departure.actual_date_time.isoformat()

                # Calculate delay
                delay = departure.actual_date_time - departure.planned_date_time
                delay_minutes = int(delay.total_seconds() / 60)
                if delay_minutes > 0:
                    dep_data["delay_minutes"] = delay_minutes

            # Add actual track if changed
            if departure.actual_track and departure.actual_track != departure.planned_track:
                dep_data["actual_track"] = departure.actual_track
                dep_data["track_changed"] = True

            # Add product info
            if departure.product:
                dep_data["operator"] = departure.product.operator_name
                dep_data["type"] = departure.product.long_category_name

            formatted_departures.append(dep_data)

        return {
            "station": station,
            "departures": formatted_departures,
            "count": len(formatted_departures),
        }

    except NSAPIError as e:
        return {"error": str(e), "departures": [], "count": 0}
    except Exception as e:
        logger.exception("Error getting departures")
        return {"error": f"Unexpected error: {e!s}", "departures": [], "count": 0}


# MCP Resources


@mcp.resource("station://{code}")
async def get_station_resource(code: str) -> str:
    """Get detailed information about a specific station.

    Args:
        code: Station code (e.g., "ut", "asd", "rtd")

    Returns:
        Formatted station information
    """
    try:
        client = get_api_client()
        stations = await client.search_stations(query=code, limit=1)

        if not stations:
            return f"Station '{code}' not found"

        station = stations[0]
        info = f"# {station.name}\n\n"
        info += f"- **Code**: {station.code}\n"
        info += f"- **UIC Code**: {station.uic_code}\n"
        info += f"- **Country**: {station.country_code}\n"

        if station.lat and station.lng:
            info += f"- **Location**: {station.lat}, {station.lng}\n"

        return info

    except Exception as e:
        return f"Error retrieving station information: {e!s}"


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
