"""Tests for data models."""

from datetime import UTC, datetime

from ns_bridge.models import (
    DiscountType,
    Location,
    Price,
    Product,
    Station,
    StationNames,
    Stop,
    TravelClass,
)


def test_station_creation() -> None:
    """Test creating a Station model."""
    station = Station(
        namen=StationNames(lang="Utrecht Centraal", middel="Utrecht C.", kort="Ut"),
        code="ut",
        UICCode="8400621",
        lat=52.089199,
        lng=5.110168,
        land="nl",
    )

    assert station.name == "Utrecht Centraal"
    assert station.code == "ut"
    assert station.uic_code == "8400621"
    assert station.lat == 52.089199
    assert station.lng == 5.110168
    assert station.country_code == "nl"


def test_station_minimal() -> None:
    """Test creating a Station with minimal fields."""
    station = Station(namen=StationNames(lang="Amsterdam"))

    assert station.name == "Amsterdam"
    assert station.code is None
    assert station.uic_code is None


def test_location_with_alias() -> None:
    """Test Location model with aliased fields."""
    location = Location(
        name="Den Haag",
        lat=52.0808,
        lng=4.3248,
        countryCode="nl",
        uicCode="8400258",
    )

    assert location.name == "Den Haag"
    assert location.country_code == "nl"
    assert location.uic_code == "8400258"


def test_stop_with_times() -> None:
    """Test Stop model with planned and actual times."""
    now = datetime.now(UTC)
    later = datetime.now(UTC)

    stop = Stop(
        name="Rotterdam Centraal",
        plannedDateTime=now,
        actualDateTime=later,
        plannedTrack="5b",
        actualTrack="5a",
    )

    assert stop.name == "Rotterdam Centraal"
    assert stop.planned_date_time == now
    assert stop.actual_date_time == later
    assert stop.planned_track == "5b"
    assert stop.actual_track == "5a"


def test_product() -> None:
    """Test Product model."""
    product = Product(
        number="2800",
        categoryCode="IC",
        shortCategoryName="IC",
        longCategoryName="Intercity",
        operatorCode="NS",
        operatorName="NS",
        type="TRAIN",
    )

    assert product.number == "2800"
    assert product.category_code == "IC"
    assert product.operator_name == "NS"


def test_price() -> None:
    """Test Price model."""
    price = Price(
        priceInCents=1250,
        priceInCentsExcludingSupplement=1000,
        supplementInCents=250,
        travelClass=TravelClass.SECOND,
        discountType=DiscountType.NO_DISCOUNT,
    )

    assert price.price_in_cents == 1250
    assert price.price_in_cents_excluding_supplement == 1000
    assert price.supplement_in_cents == 250
    assert price.travel_class == TravelClass.SECOND
    assert price.discount_type == DiscountType.NO_DISCOUNT


def test_travel_class_enum() -> None:
    """Test TravelClass enum values."""
    assert TravelClass.FIRST.value == "FIRST_CLASS"
    assert TravelClass.SECOND.value == "SECOND_CLASS"


def test_discount_type_enum() -> None:
    """Test DiscountType enum values."""
    assert DiscountType.NO_DISCOUNT.value == "NO_DISCOUNT"
    assert DiscountType.DISCOUNT_20_PERCENT.value == "DISCOUNT_20_PERCENT"
    assert DiscountType.DISCOUNT_40_PERCENT.value == "DISCOUNT_40_PERCENT"
