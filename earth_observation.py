mission_profile = {

    "description": """
    Low Earth orbit spacecraft performing Earth imaging missions.
    Primary objectives are Earth observation, payload operation,
    and reliable data delivery to ground stations.
    """,

    "mission_objectives": [
        "maintain imaging payload availability",
        "collect scientific observation data",
        "maintain reliable ground communication",
        "preserve orbital operations"
    ],

    "additional_telemetry_variables": [
        "camera_temperature",
        "image_quality",
        "imaging_power",
        "downlink_rate",
        "ground_station_visibility",
        "pointing_error",
        "attitude_accuracy"
    ],    

    "priorities": [
        "payload availability",
        "communication reliability",
        "power generation",
        "attitude stability"
    ],

    "critical_subsystems": [
        "communication",
        "power",
        "aocs"
    ],

    "available_actions": [
        "reduce payload activity",
        "switch communication modes",
        "enter safe power mode",
        "reduce spacecraft load"
    ]
}