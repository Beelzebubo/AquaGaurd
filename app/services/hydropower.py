"""Hydropower potential estimation from river flow and head height.

Uses the standard hydropower formula:

    P (MW) = η × ρ × g × Q × H / 1e6

Where:
    η = turbine efficiency (default 0.85)
    ρ = water density (1000 kg/m³)
    g = gravity (9.81 m/s²)
    Q = river flow (m³/s)
    H = effective head (m)

Known head heights for major stations (reference):
    - Melamchi:         850 m  (high-head diversion)
    - Upper Tamakoshi:  822 m
    - Kali Gandaki A:   115 m
    - Middle Marsyangdi: 78 m
    - Trishuli 3A:      60 m
    - Kulekhani I:      315 m  (storage)
    - Chisapani:        100 m  (planned run-of-river / storage)
    - Arun III:         260 m
    - Sapta Koshi HM:   40 m
    - Budhi Gandaki:    135 m
"""

# Reference station head heights (metres)
STATION_HEADS: dict[str, float] = {
    "melamchi": 850.0,
    "upper-tamakoshi": 822.0,
    "kali-gandaki-a": 115.0,
    "marsyangdi": 78.0,
    "trishuli": 60.0,
    "kulekhani": 315.0,
    "chisapani": 100.0,
    "arun-iii": 260.0,
    "sapta-koshi": 40.0,
    "budhi-gandaki": 135.0,
}

# Default efficiency for modern Francis / Pelton turbines
DEFAULT_EFFICIENCY = 0.85


def estimate_potential(
    river_flow: float,
    head_height: float | None = None,
    station_id: str | None = None,
    efficiency: float = DEFAULT_EFFICIENCY,
) -> dict:
    """Estimate hydropower potential from river flow.

    Parameters
    ----------
    river_flow : float
        River discharge in m³/s.
    head_height : float | None
        Effective head in metres.  Falls back to known station head if
        *station_id* is provided, otherwise returns a placeholder noting
        head is required.
    station_id : str | None
        Station key from STATION_HEADS.  Ignored if *head_height* is given.
    efficiency : float
        Turbine-generator efficiency (0–1).

    Returns
    -------
    dict with keys:
        power_mw         — estimated electrical output (MW)
        head_height_m    — head used (m)
        efficiency       — efficiency used
        note             — human-readable assessment
    """
    # Resolve head
    if head_height is not None:
        head = head_height
    elif station_id and station_id.lower() in STATION_HEADS:
        head = STATION_HEADS[station_id.lower()]
    else:
        return {
            "power_mw": None,
            "head_height_m": None,
            "efficiency": efficiency,
            "note": "Head height required — provide head_height or a known station_id.",
        }

    # P = η × ρ × g × Q × H  (Watts)
    power_w = efficiency * 1000.0 * 9.81 * river_flow * head
    power_mw = power_w / 1_000_000.0

    # Qualitative assessment
    if power_mw >= 100:
        note = f"Large hydropower potential ({power_mw:.0f} MW)"
    elif power_mw >= 10:
        note = f"Medium hydropower potential ({power_mw:.0f} MW)"
    elif power_mw >= 1:
        note = f"Small hydropower potential ({power_mw:.1f} MW)"
    else:
        note = f"Mini / pico scale ({power_mw*1000:.0f} kW)"

    return {
        "power_mw": round(power_mw, 2),
        "head_height_m": head,
        "efficiency": efficiency,
        "note": note,
    }
