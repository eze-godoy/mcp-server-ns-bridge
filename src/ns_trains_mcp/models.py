"""Data models for NS API responses and requests."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TravelClass(str, Enum):
    """Train travel class."""

    FIRST = "FIRST_CLASS"
    SECOND = "SECOND_CLASS"


class DiscountType(str, Enum):
    """Discount types for ticket pricing."""

    NO_DISCOUNT = "NO_DISCOUNT"
    DISCOUNT_20_PERCENT = "DISCOUNT_20_PERCENT"
    DISCOUNT_40_PERCENT = "DISCOUNT_40_PERCENT"


class ProductType(str, Enum):
    """NS train product types."""

    TRAIN = "TRAIN"
    BUS = "BUS"
    TRAM = "TRAM"
    METRO = "METRO"


# Station Models


class StationNames(BaseModel):
    """Station name variants."""

    model_config = ConfigDict(populate_by_name=True)

    lang: str  # Full name
    middel: str | None = None  # Medium name
    kort: str | None = None  # Short name


class Station(BaseModel):
    """NS Station information."""

    model_config = ConfigDict(populate_by_name=True)

    namen: StationNames  # Names object from NS API
    code: str | None = None
    uic_code: str | None = Field(None, alias="UICCode")
    lat: float | None = None
    lng: float | None = None
    land: str | None = None  # Country code (called 'land' in Dutch API)

    @property
    def name(self) -> str:
        """Get the full station name."""
        return self.namen.lang

    @property
    def country_code(self) -> str | None:
        """Get the country code."""
        return self.land


# Trip Models


class Location(BaseModel):
    """Location information (can be station or coordinates)."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    lat: float | None = None
    lng: float | None = None
    country_code: str | None = Field(None, alias="countryCode")
    uic_code: str | None = Field(None, alias="uicCode")


class Stop(BaseModel):
    """Stop information on a journey leg."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    # Origin/destination use plannedDateTime/actualDateTime (not departure/arrival specific)
    planned_date_time: datetime | None = Field(None, alias="plannedDateTime")
    actual_date_time: datetime | None = Field(None, alias="actualDateTime")
    planned_track: str | None = Field(None, alias="plannedTrack")
    actual_track: str | None = Field(None, alias="actualTrack")

    # Additional fields from API
    lng: float | None = None
    lat: float | None = None
    country_code: str | None = Field(None, alias="countryCode")
    uic_code: str | None = Field(None, alias="uicCode")
    station_code: str | None = Field(None, alias="stationCode")


class Product(BaseModel):
    """Transport product information."""

    model_config = ConfigDict(populate_by_name=True)

    number: str | None = None
    category_code: str | None = Field(None, alias="categoryCode")
    short_category_name: str | None = Field(None, alias="shortCategoryName")
    long_category_name: str | None = Field(None, alias="longCategoryName")
    operator_code: str | None = Field(None, alias="operatorCode")
    operator_name: str | None = Field(None, alias="operatorName")
    type: str | None = None


class Duration(BaseModel):
    """Duration information with display value."""

    model_config = ConfigDict(populate_by_name=True)

    value: str  # e.g., "26 min."


class Leg(BaseModel):
    """Journey leg (one continuous ride)."""

    model_config = ConfigDict(populate_by_name=True)

    idx: str
    name: str
    direction: str | None = None
    cancelled: bool = False
    origin: Stop
    destination: Stop
    product: Product | None = None
    stops: list[Stop] = Field(default_factory=list)
    duration: Duration | str | None = None  # Can be object or string


class Price(BaseModel):
    """Pricing information."""

    model_config = ConfigDict(populate_by_name=True)

    price_in_cents: int = Field(alias="priceInCents")
    price_in_cents_excluding_supplement: int | None = Field(
        None, alias="priceInCentsExcludingSupplement"
    )
    supplement_in_cents: int | None = Field(None, alias="supplementInCents")
    buyable_ticket_price_in_cents: int | None = Field(None, alias="buyableTicketPriceInCents")
    product: str | None = None  # e.g., "OVCHIPKAART_ENKELE_REIS", "OVCHIPKAART_RETOUR"
    travel_class: str | None = Field(
        None, alias="travelClass"
    )  # e.g., "FIRST_CLASS", "SECOND_CLASS"
    discount_type: str | None = Field(
        None, alias="discountType"
    )  # e.g., "NO_DISCOUNT", "DISCOUNT_20_PERCENT"


class Trip(BaseModel):
    """Complete trip information from origin to destination."""

    model_config = ConfigDict(populate_by_name=True)

    idx: int
    uid: str
    planned_duration_in_minutes: int = Field(alias="plannedDurationInMinutes")
    actual_duration_in_minutes: int | None = Field(None, alias="actualDurationInMinutes")
    transfers: int
    status: str
    legs: list[Leg]
    fare_route: dict[str, Any] | None = Field(None, alias="fareRoute")
    product_fare: Price | None = Field(
        None, alias="productFare"
    )  # Price for selected class/discount
    fares: list[Price] | None = None  # All available fare options
    price: Price | None = None  # Legacy field, same as product_fare


class TripSearchResponse(BaseModel):
    """Response from trips search endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    source: str
    trips: list[Trip]


# Departure Models


class RouteStation(BaseModel):
    """Simple route station information in departures."""

    model_config = ConfigDict(populate_by_name=True)

    uic_code: str = Field(alias="uicCode")
    medium_name: str = Field(alias="mediumName")


class Departure(BaseModel):
    """Departure information for a station."""

    model_config = ConfigDict(populate_by_name=True)

    direction: str
    name: str
    planned_date_time: datetime = Field(alias="plannedDateTime")
    actual_date_time: datetime | None = Field(None, alias="actualDateTime")
    planned_track: str | None = Field(None, alias="plannedTrack")
    actual_track: str | None = Field(None, alias="actualTrack")
    product: Product
    cancelled: bool = False
    route_stations: list[RouteStation] = Field(default_factory=list, alias="routeStations")


class DeparturesPayload(BaseModel):
    """Payload wrapper for departures response."""

    model_config = ConfigDict(populate_by_name=True)

    source: str
    departures: list[Departure]


class DeparturesResponse(BaseModel):
    """Response from departures endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    payload: DeparturesPayload
