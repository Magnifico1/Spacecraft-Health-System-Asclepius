mission_profile = {

    "name": "Deep Space Mission",

    "description": """
    Autonomous spacecraft operating far from Earth where communication
    delays require high spacecraft autonomy.
    """,

    "mission_objectives": [
        "maintain autonomous spacecraft operation",
        "preserve power resources",
        "maintain long-range communication",
        "protect scientific instruments"
    ],

    "additional_telemetry_variables": [
        "rtg_output",
        "battery_state",
        "processor_temperature",
        "memory_integrity",
        "antenna_status",
        "signal_to_noise_ratio",
        "trajectory_error",
        "delta_v_remaining"
    ],

    "priorities": [
        "spacecraft survival",
        "power conservation",
        "computer reliability",
        "communication availability"
    ],

    "critical_subsystems": [
        "power",
        "obc",
        "communication",
        "propulsion"
    ],

    "available_actions": [
        "activate redundant systems",
        "reduce power consumption",
        "perform onboard diagnostics",
        "delay non-critical operations"
    ]
}