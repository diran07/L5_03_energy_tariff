
"""Track electricity meter readings and calculate tariff bills."""

import json
from datetime import datetime
from pathlib import Path

meters = {}
TARIFF_RATES = [3.5, 5.0, 7.5]
SPIKE_LIMIT = 500
DEFAULT_DATA_FILE = Path("meters.json")


def record_reading(meter_id, units, history=None):
    """Record a non-negative meter reading and return reading history."""
    if not isinstance(units, (int, float)) or isinstance(units, bool):
        raise TypeError("Units must be a number.")
    if units < 0:
        raise ValueError("Units cannot be negative.")
    if not meter_id:
        raise ValueError("Meter ID cannot be empty.")

    if history is None:
        history = []

    history.append((meter_id, units, datetime.now().isoformat()))
    meters[meter_id] = meters.get(meter_id, 0) + units
    return history


def compute_bill(meter_id, tier_rates):
    """Calculate a progressive three-tier electricity bill."""
    if meter_id not in meters:
        raise KeyError(f"Unknown meter: {meter_id}")
    if len(tier_rates) != 3:
        raise ValueError("Exactly three tariff rates are required.")
    if any(
        not isinstance(rate, (int, float))
        or isinstance(rate, bool)
        or rate < 0
        for rate in tier_rates
    ):
        raise ValueError("Tariff rates must be non-negative numbers.")

    units = meters[meter_id]

    if units <= 100:
        return units * tier_rates[0]
    if units <= 300:
        return 100 * tier_rates[0] + (units - 100) * tier_rates[1]

    return (
        100 * tier_rates[0]
        + 200 * tier_rates[1]
        + (units - 300) * tier_rates[2]
    )


def raise_rates(percent):
    """Increase all tariff rates by the given percentage."""
    if not isinstance(percent, (int, float)) or isinstance(percent, bool):
        raise TypeError("Percentage must be a number.")
    if percent < 0:
        raise ValueError("Rate increase cannot be negative.")

    multiplier = 1 + percent / 100
    for index, rate in enumerate(TARIFF_RATES):
        TARIFF_RATES[index] = rate * multiplier


def flag_spikes():
    """Return meter IDs whose accumulated usage exceeds the limit."""
    return [
        meter_id
        for meter_id, units in meters.items()
        if units > SPIKE_LIMIT
    ]


def load_meter_data(file=DEFAULT_DATA_FILE):
    """Load saved meter readings and validate the JSON data."""
    try:
        with open(file, "r", encoding="utf-8") as data_file:
            loaded_data = json.load(data_file)
    except FileNotFoundError:
        meters.clear()
        return
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            f"Could not load meter data: {error}"
        ) from error

    if not isinstance(loaded_data, dict) or not all(
        isinstance(key, str)
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value >= 0
        for key, value in loaded_data.items()
    ):
        raise ValueError(
            "Meter data must contain non-negative numeric totals."
        )

    meters.clear()
    meters.update(loaded_data)


def save_meter_data(file=DEFAULT_DATA_FILE):
    """Save meter totals as JSON."""
    with open(file, "w", encoding="utf-8") as data_file:
        json.dump(meters, data_file, indent=2)


def main():
    """Run the sample electricity billing workflow."""
    load_meter_data()

    history = []
    record_reading("M-01", 120, history)
    record_reading("M-02", 640, history)

    try:
        record_reading("M-03", -50, history)
    except ValueError as error:
        print(f"Invalid reading rejected: {error}")

    record_reading("M-03", 50, history)
    print("Readings recorded:", len(history))

    raise_rates(10)

    print(f"Bill M-01: {compute_bill('M-01', TARIFF_RATES):.2f}")
    print(f"Bill M-03: {compute_bill('M-03', TARIFF_RATES):.2f}")
    print("Spikes:", flag_spikes())

    adjustment = input(
        "Extra units for M-01 (a non-negative number; Enter for 0): "
    ).strip()

    try:
        extra_units = float(adjustment) if adjustment else 0
        record_reading("M-01", extra_units, history)
    except (ValueError, TypeError) as error:
        print(f"Invalid input: {error}")
        return

    save_meter_data()
    load_meter_data()
    print(
        f"Bill M-01 after reload: "
        f"{compute_bill('M-01', TARIFF_RATES):.2f}"
    )


if __name__ == "__main__":
    main()
