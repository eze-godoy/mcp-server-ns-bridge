"""NS API Client for interacting with Netherlands Railways APIs."""

import logging
from datetime import datetime
from typing import Any

import httpx

from ns_bridge.config import Settings
from ns_bridge.models import (
    DeparturesResponse,
    DiscountType,
    Station,
    TravelClass,
    TripSearchResponse,
)

logger = logging.getLogger(__name__)

# Constants
MIN_QUERY_LENGTH = 2


class NSAPIError(Exception):
    """Base exception for NS API errors."""


class NSAPIClient:
    """Client for interacting with the NS (Nederlandse Spoorwegen) API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the NS API client.

        Args:
            settings: Application settings containing API credentials
        """
        self.settings = settings
        self.base_url = settings.ns_api_base_url
        self.client = httpx.AsyncClient(
            headers={
                "Ocp-Apim-Subscription-Key": settings.ns_api_key,
            },
            timeout=30.0,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "NSAPIClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the NS API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as a dictionary

        Raises:
            NSAPIError: If the API request fails
        """
        url = f"{self.base_url}{endpoint}"

        # Debug logging
        logger.info(f"NS API Request: {method} {url}")
        logger.info(f"Parameters: {params}")

        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
            )
            logger.info(f"Response status: {response.status_code}")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_msg = f"NS API request failed: {e.response.status_code} - {e.response.text}"
            logger.exception(error_msg)
            raise NSAPIError(error_msg) from e

        except httpx.RequestError as e:
            error_msg = f"NS API request error: {e!s}"
            logger.exception(error_msg)
            raise NSAPIError(error_msg) from e

    # Stations API

    async def search_stations(
        self,
        query: str | None = None,
        country_codes: list[str] | None = None,
        limit: int = 10,
    ) -> list[Station]:
        """Search for stations by name or filter by country.

        Args:
            query: Search query (minimum 2 characters)
            country_codes: List of country codes to filter (e.g., ["nl", "de", "be"])
            limit: Maximum number of results to return

        Returns:
            List of matching stations
        """
        params: dict[str, Any] = {"limit": limit}

        if query:
            if len(query) < MIN_QUERY_LENGTH:
                msg = f"Query must be at least {MIN_QUERY_LENGTH} characters long"
                raise ValueError(msg)
            params["q"] = query

        if country_codes:
            params["countryCodes"] = ",".join(country_codes)

        data = await self._make_request("GET", "/nsapp-stations/v2", params=params)

        # Parse the response into Station models
        stations = []
        for station_data in data.get("payload", []):
            try:
                stations.append(Station(**station_data))
            except Exception as e:
                logger.warning(f"Failed to parse station data: {e}")
                continue

        return stations

    # Trips API

    async def search_trips(
        self,
        origin_station: str | None = None,
        destination_station: str | None = None,
        origin_uic: str | None = None,
        destination_uic: str | None = None,
        date_time: datetime | None = None,
        search_for_arrival: bool = False,
        via_station: str | None = None,
        travel_class: TravelClass = TravelClass.SECOND,
        discount: DiscountType = DiscountType.NO_DISCOUNT,
    ) -> TripSearchResponse:
        """Search for trips between two stations.

        Args:
            origin_station: NS station code for origin (e.g., "ut" for Utrecht)
            destination_station: NS station code for destination
            origin_uic: UIC code for origin station (alternative to origin_station)
            destination_uic: UIC code for destination station
            date_time: Desired departure/arrival time (defaults to now)
            search_for_arrival: If True, search for arrival time instead of departure
            via_station: Optional via station code
            travel_class: Travel class (1st or 2nd)
            discount: Discount type for pricing

        Returns:
            Trip search results with pricing information
        """
        # Validate input
        if not (origin_station or origin_uic):
            msg = "Either origin_station or origin_uic must be provided"
            raise ValueError(msg)

        if not (destination_station or destination_uic):
            msg = "Either destination_station or destination_uic must be provided"
            raise ValueError(msg)

        params: dict[str, Any] = {
            "travelClass": (
                1 if travel_class == TravelClass.FIRST else 2
            ),  # API wants integer: 1 or 2
        }

        # Only add discount if it's not NO_DISCOUNT (API has this as default)
        if discount != DiscountType.NO_DISCOUNT:
            params["discount"] = discount.value

        # Origin
        if origin_station:
            params["fromStation"] = origin_station
        elif origin_uic:
            params["originUicCode"] = origin_uic

        # Destination
        if destination_station:
            params["toStation"] = destination_station
        elif destination_uic:
            params["destinationUicCode"] = destination_uic

        # Optional parameters
        if date_time:
            params["dateTime"] = date_time.isoformat()

        if search_for_arrival:
            params["searchForArrival"] = "true"

        if via_station:
            params["viaStation"] = via_station

        data = await self._make_request("GET", "/reisinformatie-api/api/v3/trips", params=params)

        return TripSearchResponse(**data)

    # Departures API

    async def get_departures(
        self,
        station: str | None = None,
        uic_code: str | None = None,
        max_journeys: int = 10,
        date_time: datetime | None = None,
    ) -> DeparturesResponse:
        """Get departures for a specific station.

        Args:
            station: NS station code (e.g., "ut" for Utrecht Centraal)
            uic_code: UIC code for the station (alternative to station)
            max_journeys: Maximum number of departures to return
            date_time: Departure time to show departures from (defaults to now)

        Returns:
            List of departures from the station
        """
        if not (station or uic_code):
            msg = "Either station or uic_code must be provided"
            raise ValueError(msg)

        params: dict[str, Any] = {"maxJourneys": max_journeys}

        if station:
            params["station"] = station
        elif uic_code:
            params["uicCode"] = uic_code

        if date_time:
            params["dateTime"] = date_time.isoformat()

        data = await self._make_request(
            "GET", "/reisinformatie-api/api/v2/departures", params=params
        )

        return DeparturesResponse(**data)

    # Pricing helper

    def format_price(self, price_in_cents: int) -> str:
        """Format price in cents to Euro string.

        Args:
            price_in_cents: Price in cents

        Returns:
            Formatted price string (e.g., "€12.50")
        """
        euros = price_in_cents / 100
        return f"€{euros:.2f}"
