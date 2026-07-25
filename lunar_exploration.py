mission_profile = {

    "name": "Lunar Exploration Mission",

    "description": """
    Spacecraft operating around or on the lunar surface.
    Operations are affected by extreme thermal conditions,
    limited communication opportunities, and constrained power.
    """,

    "mission_objectives": [
        "maintain spacecraft survival",
        "support lunar surface operations",
        "maintain communication with Earth",
        "protect scientific payloads"
    ],

    "additional_telemetry_variables": [
        "radiator_temperature",
        "heater_power",
        "earth_visibility",
        "link_margin",
        "wheel_slip_ratio",
        'terrain_slope'
        "surface_speed"
    ],

    "priorities": [
        "thermal survival",
        "power availability",
        "communication availability",
        "mobility operations"
    ],

    "critical_subsystems": [
        "thermal",
        "power",
        "communication",
        "aocs"
    ],

    "available_actions": [
        "enter survival mode",
        "reduce non-essential loads",
        "prioritise communication windows",
        "preserve battery capacity"
    ]
}