import pandas as pd
from core.config import DATA_DIR, OUTPUT_DIR

# Obtain active mission subsystems

core_subsystems = ["power", "thermal", "aocs", "communication", "propulsion", "obc"]

def get_active_subsystems(df):

    subsystems = core_subsystems.copy()

    if "optics_issue" in df.columns:
        subsystems.append("optics")

    if "mobility_issue" in df.columns:
        subsystems.append("mobility")

    return subsystems

# -------------------------------------------------
# 1. Rule definition
# -------------------------------------------------

rules = {
    "power": [
        ("battery_voltage", "min", 3.8, "Voltage degradation"),
        ("battery_current", "max", 3, "Current overload"),
        ("solar_array_power", "min", 110, "Solar array degradation"),
        ("battery_state_of_charge", "min", 35, "Low battery state of charge"),
        # Deep Space
        ("rtg_output", "min", 150, "RTG power degradation"),
        ("battery_state", "min", 40, "Battery state degradation")],

    "thermal": [
        ("battery_temp", "max", 27, "Battery overheating"),
        ("battery_temp", "min", 23, "Battery under-temperature"),
        ("bus_temp", "max", 26, "Bus overheating"),
        ("bus_temp", "min", 18, "Bus under-temperature"),
        ("payload_temp", "max", 22, "Payload overheating"),
        ("payload_temp", "min", 16, "Payload under-temperature"),
         # Lunar Exploration
        ("radiator_temperature", "max", 42, "Radiator overheating"),
        ("heater_power", "max", 60, "Excessive heater power"),
        # Deep Space
        ("processor_temperature", "max", 70, "Processor overheating")],

    "aocs": [
        ("reaction_wheel_speed", "max", 6400, "Reaction wheel saturation"),
        ("gyro_drift", "max", .03, "Gyroscope drift anomaly"),
        # Earth Observation
        ("pointing_error", "max", 1.2, "Pointing error"),
        ("attitude_accuracy", "min", 95, "Attitude accuracy degradation"),
        # Deep Space
        ("trajectory_error", "max", 2, "Trajectory deviation")],

    "communication": [
        ("communication_signal", "min", 75, "Signal degradation"),
        ("data_rate", "min", 40, "Data rate reduction"),
        ("packet_loss", "max", 3, "Packet loss spike"),
        # Earth Observation
        ("ground_station_visibility", "mean", .8, "Ground station visibility lost"),
        ("downlink_rate", "min", 30, "Downlink degradation"),
        # Lunar Exploration
        ("earth_visibility", "min", 1, "Earth visibility lost"),
        ("link_margin", "min", 10, "Low link margin"),
        # Deep Space
        ("antenna_status", "min", 1, "Antenna failure"),
        ("signal_to_noise_ratio", "min", 5, "Low signal-to-noise ratio")],

    "propulsion": [
        ("fuel_level", "min", 50, "Fuel depletion"),
        ("thruster_temp", "max", 40, "Thruster overheating"),
        ("thrust_level", "max", .9, "Extreme thrust output"),
        # Deep Space
        ("delta_v_remaining", "min", 20, "Low delta-v remaining")],

    "obc": [
        ("cpu_load", "max", 60, "CPU overload"),
        ("memory_usage", "max", 70, "Memory saturation"),
        # Deep Space
        ("memory_integrity", "min", 95, "Memory integrity degradation")],

    # Earth Observation only
    "optics": [
        ("camera_temperature", "max", 35, "Camera overheating"),
        ("image_quality", "min", 70, "Image quality degradation"),
        ("imaging_power", "max", 130, "Imaging power overload")],

    # Lunar Exploration only
    "mobility": [
        ("wheel_slip_ratio", "max", .5, "Wheels slipping"),
        ('terrain_slope', 'max', 25, 'Extreme terrain slope'),
        ("surface_speed", "min", 1, "Mobility degradation")]
}


def classify_confidence(rule_detected, ml_detected):
    if ml_detected and rule_detected != ["Unknown anomaly"]:
        return "High"

    elif ml_detected or rule_detected != ["Unknown anomaly"]:
        return "Medium"

    else:
        return "Low"

# -------------------------------------------------
# Event severity classification
# -------------------------------------------------

def classify_event_severity(duration, rule_detected, ml_detected, subsystem):
    """
    Classify the operational severity of an event based on:
    - event duration
    - whether rule-based detection triggered
    - whether ML detection triggered

    Parameters:
        duration (int/float): Number of telemetry samples in the event
        rule_detected (bool): True if rule engine detected the event
        ml_detected (bool): True if Isolation Forest detected the event

    Returns:
        str: Event severity classification
    """
    critical_subsystems = [
        "power",
        "propulsion",
        "aocs",
        'obc'
    ]

    # Both rule and ML agree
    if rule_detected and ml_detected:

        # Persistent confirmed events are critical
        if duration > 200:
            return 'Critical'

        if subsystem in critical_subsystems and duration > 100:
            return "Critical"

        # Short confirmed events are warnings
        else:
            return "Warning"

    # ML only events require investigation
    elif ml_detected:
        return "Investigation"

    # Rule only events are known but not confirmed by ML
    elif rule_detected:
        return "Warning"

    # No detection evidence
    return "Normal"
            
# -------------------------------------------------
# 3. Event engine
# -------------------------------------------------
def extract_events(df):

    subsystems = get_active_subsystems(df)
    events = []

    active = {s: None for s in subsystems}
    anomaly_counter = {s: 0 for s in subsystems}
    normal_counter = {s: 0 for s in subsystems}

    # -------------------------------------------------
    # Rule detection
    # -------------------------------------------------
    def evaluate_rules(df_slice, subsystem):
        """Identify rule-based causes for the event."""

        detected = []

        for col, mode, threshold, label in rules[subsystem]:

            if col not in df_slice.columns:
                continue

            series = df_slice[col]

            if len(series) == 0:
                continue

            if mode == "min" and series.min() < threshold:
                detected.append(label)

            elif mode == "max" and series.max() > threshold:
                detected.append(label)
            
            elif mode == "mean" and series.mean() < threshold:
                detected.append(label)

        return detected if detected else ["Unknown anomaly"]

    # -------------------------------------------------
    # ML detection
    # -------------------------------------------------
    def evaluate_ml(df_slice, subsystem):
        """Check whether Isolation Forest detected anomalies."""

        anomaly_col = f"{subsystem}_anomaly_status"

        if anomaly_col not in df_slice.columns:
            return False

        return (
            df_slice[anomaly_col] == "Anomaly"
        ).any()


    # -------------------------------------------------
    # Event loop
    # -------------------------------------------------
    for i, row in df.iterrows():

        for subsystem in subsystems:

            issue_col = f"{subsystem}_issue"

            if issue_col not in df.columns:
                continue

            # -------------------------
            # Anomaly detected
            # -------------------------
            if row[issue_col]:

                normal_counter[subsystem] = 0

                if active[subsystem] is None:

                    anomaly_counter[subsystem] += 1

                    if anomaly_counter[subsystem] >= 10:

                        active[subsystem] = {
                            "start_time": df.iloc[max(i-2,0)]["time"],
                            "start_index": max(i-2,0)
                        }

            # -------------------------
            # Normal reading
            # -------------------------
            else:

                anomaly_counter[subsystem] = 0

                if active[subsystem] is not None:

                    normal_counter[subsystem] += 1


                    if normal_counter[subsystem] >= 3:

                        start = active[subsystem]

                        df_slice = df.iloc[
                            start["start_index"]:i-2
                        ]

                        rule_detected = evaluate_rules(
                            df_slice,
                            subsystem
                        )

                        ml_detected = evaluate_ml(
                            df_slice,
                            subsystem
                        )

                        rule_flag = rule_detected != ["Unknown anomaly"]

                        if not rule_flag and not ml_detected:
                            active[subsystem] = None
                            normal_counter[subsystem] = 0
                            continue

                        confidence = classify_confidence(
                            rule_detected,
                            ml_detected
                        )

                        events.append({
                            "subsystem": subsystem,
                            "event_type": rule_detected,
                            "rule_detected": rule_detected != ["Unknown anomaly"],
                            "ml_detected": ml_detected,
                            "confidence": confidence,
                            "start_time": start["start_time"],
                            "end_time": row["time"],
                            "duration": row["time"] - start["start_time"],
                            "event_severity": classify_event_severity(
                                duration=row["time"] - start["start_time"],
                                rule_detected=rule_detected != ["Unknown anomaly"],
                                ml_detected=ml_detected,
                                subsystem=subsystem
                            )
                        })

                        active[subsystem] = None
                        normal_counter[subsystem] = 0

    # -------------------------------------------------
    # Close open events
    # -------------------------------------------------
    final_time = df.iloc[-1]["time"]

    for subsystem, start in active.items():

        if start is None:
            continue

        df_slice = df.iloc[start["start_index"]:]

        rule_detected = evaluate_rules(
            df_slice,
            subsystem
        )

        ml_detected = evaluate_ml(
            df_slice,
            subsystem
        )

        rule_flag = rule_detected != ["Unknown anomaly"]

        if not rule_flag and not ml_detected:
            active[subsystem] = None
            normal_counter[subsystem] = 0
            continue

        confidence = classify_confidence(
            rule_detected,
            ml_detected
        )

        events.append({
            "subsystem": subsystem,
            "event_type": rule_detected,
            "rule_detected": rule_detected != ["Unknown anomaly"],
            "ml_detected": ml_detected,
            "confidence": confidence,
            "start_time": start["start_time"],
            "end_time": final_time,
            "duration": final_time - start["start_time"],
            "event_severity": classify_event_severity(
                duration=final_time - start["start_time"],
                rule_detected=rule_detected != ["Unknown anomaly"],
                ml_detected=ml_detected,
                subsystem=subsystem
            ),
        })

    return pd.DataFrame(events)

def merge_events(events_df, max_gap=30):
    """
    Merge nearby events from the same subsystem.

    Parameters:
        events_df: dataframe containing extracted events
        max_gap: maximum number of telemetry samples between events
                 before treating them as one event
    """

    if events_df.empty:
        return events_df

    merged_events = []

    # Sort events first
    events_df = events_df.sort_values(
        ["subsystem", "start_time"]
    ).reset_index(drop=True)

    current = events_df.iloc[0].copy()

    for i in range(1, len(events_df)):

        next_event = events_df.iloc[i]

        same_subsystem = (current["subsystem"] == next_event["subsystem"])

        # Compare event type
        same_type = (str(current["event_type"]) == str(next_event["event_type"]))

        # Time gap between events
        gap = (next_event["start_time"] - current["end_time"])

        if same_subsystem and gap <= max_gap:

            # Extend current event
            current["end_time"] = next_event["end_time"]

            current["duration"] = (current["end_time"] - current["start_time"])

            # Keep highest severity
            severity_rank = {
                "Normal": 0,
                "Investigation": 1,
                "Warning": 2,
                "Critical": 3}

            if severity_rank[next_event["event_severity"]] > severity_rank[current["event_severity"]]:
                current["event_severity"] = next_event["event_severity"]

            # If either detected by ML/rules, keep it
            current["rule_detected"] = (current["rule_detected"] or next_event["rule_detected"])

            current["ml_detected"] = (current["ml_detected"] or next_event["ml_detected"])

        else:
            merged_events.append(current)
            current = next_event.copy()

    # append final event
    merged_events.append(current)

    return pd.DataFrame(merged_events)

# Run code
if __name__ == '__main__':
    df = pd.read_csv(DATA_DIR / 'telemetry_data_with_health_status.csv')
    events_df = extract_events(df)
    events_df = merge_events(events_df)
    events_df.to_csv(OUTPUT_DIR / 'mission_events.csv', index=False)
    print("Event extraction complete. Results saved to mission_events.csv")
