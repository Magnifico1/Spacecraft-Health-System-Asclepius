import pandas as pd
import numpy as np
from core.config import DATA_DIR

def anomaly_flag(df, subsystem):
    """
    Safely retrieve ML anomaly status.
    Returns False if subsystem is not active in this mission.
    """
    column = f"{subsystem}_anomaly_status"

    if column in df.columns:
        anomaly = df[column] == "Anomaly"

        # Convert isolated ML detections into sustained ML issues
        return (anomaly.rolling(window=10, min_periods=1).sum()>= 3)

    return False


def health_status(df):
    """
    Evaluate the health status of the spacecraft based on telemetry data.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing telemetry data.
    
    Returns:
    pd.DataFrame: DataFrame with additional columns indicating subsystem health status.
    """

    # Define conditions for health status of each subsystem
    # Power subsystem
    df['power_rule_count'] = (
        (df['battery_voltage'] < 3.8).astype(int) +
        (df['battery_current'] > 3).astype(int) + 
        (df['solar_array_power'] < 110).astype(int) +
        (df["battery_state_of_charge"] < 50).astype(int))
    
    df['power_rule_issue'] = df['power_rule_count']>0

    df["power_ml_issue"] = anomaly_flag(df, "power")

    # Thermal subsystem
    df['thermal_rule_count'] = (
        (df['battery_temp'] < 23).astype(int) +
        (df['battery_temp'] > 27).astype(int) + 
        (df['bus_temp'] < 18).astype(int) + 
        (df['bus_temp'] > 26).astype(int) + 
        (df['payload_temp'] < 16).astype(int) +
        (df['payload_temp'] > 22).astype(int))

    df['thermal_rule_issue'] = df['thermal_rule_count']>0

    df["thermal_ml_issue"] = anomaly_flag(df, "thermal")

    # Attitude and Orbit Control System (AOCS)
    df['aocs_rule_count'] = (
        (df['reaction_wheel_speed'] > 6400).astype(int) + 
        (df['gyro_drift'] > 0.03).astype(int))

    df['aocs_rule_issue'] = df['aocs_rule_count']>0

    df["aocs_ml_issue"] = anomaly_flag(df, "aocs")

    # Communication subsystem
    df['communication_rule_count'] = (
        (df['communication_signal'] < 75).astype(int) +
        (df['data_rate'] < 40).astype(int) +
        (df['packet_loss'] > 3).astype(int))

    df['communication_rule_issue'] = df['communication_rule_count']>0

    df["communication_ml_issue"] = anomaly_flag(df, "communication")

    # Propulsion subsystem
    df['propulsion_rule_count'] = (
        (df['fuel_level'] < 50).astype(int) +
        (df['thruster_temp'] > 40).astype(int) +
        (df['thrust_level'] > 0.9).astype(int))

    df['propulsion_rule_issue'] = df['propulsion_rule_count']>0

    df["propulsion_ml_issue"] = anomaly_flag(df, "propulsion")

    # On-board Computer (OBC) subsystem
    df['obc_rule_count'] = (
        (df['cpu_load'] > 60).astype(int) +
        (df['memory_usage'] > 70).astype(int))

    df['obc_rule_issue'] = df['obc_rule_count']>0

    df["obc_ml_issue"] = anomaly_flag(df, "obc")

    
    #-----------------------------------------------------------
    # Earth Observation mission-specific telemetry
    #-----------------------------------------------------------

    # Optics subsystem
    if all(col in df.columns for col in [
        "camera_temperature",
        "image_quality",
        "imaging_power"]):

        df["optics_rule_count"] = (
            (df["camera_temperature"] > 35).astype(int) +
            (df["image_quality"] < 70).astype(int) +
            (df["imaging_power"] > 130).astype(int))
    
        df['optics_rule_issue'] = df['optics_rule_count']>0

        df["optics_ml_issue"] = anomaly_flag(df, "optics")

    # AOCS
    if all(col in df.columns for col in [
        "pointing_error",
        "attitude_accuracy"]):

        df["aocs_rule_count"] = (
            df["aocs_rule_count"].astype(int) +
            (df["pointing_error"] > 2.5).astype(int) +
            (df["attitude_accuracy"] < 95).astype(int))
    
    # Communication subsystem
    if all(col in df.columns for col in [
        "downlink_rate",
        "ground_station_visibility"]):

        df["communication_rule_count"] = (
            df["communication_rule_count"].astype(int) +
            (df["downlink_rate"] < 30).astype(int) +
            (df["ground_station_visibility"] == 0).astype(int))
    
    #-----------------------------------------------------------------
    # Lunar Exploration mission-specific telemetry
    #-----------------------------------------------------------------

    # Thermal subsystem
    if all(col in df.columns for col in [
        "radiator_temperature",
        "heater_power"]):

        df["thermal_rule_count"] = (
            df["thermal_rule_count"].astype(int) +
            (df["radiator_temperature"] > 42).astype(int).astype(int) +
            (df["heater_power"] > 60).astype(int).astype(int))

    # Communication subsystem
    if all(col in df.columns for col in [
            "earth_visibility",
            "link_margin"]):

        df["communication_rule_count"] = (
            df["communication_rule_count"].astype(int) +
            (df["earth_visibility"] == 0).astype(int) +
            (df["link_margin"] < 10).astype(int))
    
    # Mobility subsystem
    if all(col in df.columns for col in [
        "wheel_slip_ratio",
        'terrain_slope',
        "surface_speed"]):

        df["mobility_rule_count"] = (
            (df["wheel_slip_ratio"] > 0.5).astype(int) +
            (df['terrain_slope'] > 25).astype(int) +
            (df["surface_speed"] < 1).astype(int))
        
        df['mobility_rule_issue'] = df['mobility_rule_count']>0

        df["mobility_ml_issue"] = anomaly_flag(df, "mobility")


    #-----------------------------------------------------------------
    # Deep Space mission-specific telemetry
    #-----------------------------------------------------------------

    # Power subsystem
    if all(col in df.columns for col in [
        "rtg_output",
        "battery_state"]):

        df["power_rule_count"] = (
            df["power_rule_count"].astype(int) +
            (df["rtg_output"] < 150).astype(int) +
            (df["battery_state"] < 40).astype(int))

    # Thermal subsystem
    if "processor_temperature" in df.columns:

        df["thermal_rule_count"] = (
            df["thermal_rule_count"].astype(int) +
            (df["processor_temperature"] > 70).astype(int))

    # Communication subsystem
    if all(col in df.columns for col in [
        "antenna_status",
        "signal_to_noise_ratio"]):

        df["communication_rule_count"] = (
            df["communication_rule_count"].astype(int) +
            (df["antenna_status"] == 0).astype(int) +
            (df["signal_to_noise_ratio"] < 5).astype(int))


    # Propulsion subsystem
    if all(col in df.columns for col in [
        "trajectory_error",
        "delta_v_remaining"]):

        df["propulsion_rule_count"] = (
            df["propulsion_rule_count"].astype(int) +
            (df["trajectory_error"] > 2).astype(int) +
            (df["delta_v_remaining"] < 20).astype(int))

    # OBC
    if "memory_integrity" in df.columns:

        df["obc_rule_count"] = (
            df["obc_rule_count"].astype(int) +
            (df["memory_integrity"] < 95).astype(int))

    # Compute subsystem issue flags 
    df["power_issue"] = (df["power_rule_issue"] | df["power_ml_issue"])
    df["thermal_issue"] = (df["thermal_rule_issue"] | df["thermal_ml_issue"])
    df["aocs_issue"] = (df["aocs_rule_issue"] | df["aocs_ml_issue"])
    df["communication_issue"] = (df["communication_rule_issue"] | df["communication_ml_issue"])
    df["propulsion_issue"] = (df["propulsion_rule_issue"] | df["propulsion_ml_issue"])
    df["obc_issue"] = (df["obc_rule_issue"] | df["obc_ml_issue"])

    if 'optics_rule_issue' in df.columns:
        df["optics_issue"] = (df["optics_rule_count"] > 0)

    if "mobility_rule_issue" in df.columns:
        df["mobility_issue"] = (df["mobility_rule_issue"] > 0)
    

    #------------------------------------------------------------------
    # Subsystem health classification
    #------------------------------------------------------------------

    def subsystem_status(rule_count):

        return np.where(
            rule_count > 0,
            "Degraded",
            "Normal")

    df["power_status"] = subsystem_status(df["power_rule_count"])
    df["thermal_status"] = subsystem_status(df["thermal_rule_count"])
    df["aocs_status"] = subsystem_status(df["aocs_rule_count"])
    df["communication_status"] = subsystem_status(df["communication_rule_count"])
    df["propulsion_status"] = subsystem_status(df["propulsion_rule_count"])
    df["obc_status"] = subsystem_status(df["obc_rule_count"])

    if "optics_rule_count" in df.columns:
        df["optics_status"] = subsystem_status(df["optics_rule_count"])

    if "mobility_rule_count" in df.columns:
        df["mobility_status"] = subsystem_status(df["mobility_rule_count"])


    #------------------------------------------------------------------
    # Aggregate system health
    #------------------------------------------------------------------

    def classify_system_health(row):

        # Critical subsystems
        critical_rule_count = sum([
            row["power_rule_count"],
            row["communication_rule_count"],
            row["propulsion_rule_count"],
            row.get("optics_rule_count", 0),
            row.get("mobility_rule_count", 0)
        ])

        # Other subsystems
        non_critical_rule_count = sum([
            row["thermal_rule_count"],
            row["aocs_rule_count"],
            row["obc_rule_count"]
        ])


        # ML anomaly count
        ml_count = sum([
            row["power_ml_issue"],
            row["thermal_ml_issue"],
            row["aocs_ml_issue"],
            row["communication_ml_issue"],
            row["propulsion_ml_issue"],
            row["obc_ml_issue"],
            row.get("optics_ml_issue", False),
            row.get("mobility_ml_issue", False)
        ])


        # -----------------------------
        # Overall spacecraft health
        # -----------------------------

        if critical_rule_count >= 3:
            return "Critical"

        elif non_critical_rule_count >= 5:
            return "Critical"

        elif critical_rule_count > 0:
            return "Warning"

        elif non_critical_rule_count > 0:
            return "Warning"

        elif ml_count >= 3:
            return "Warning"

        else:
            return "Normal"

        # Apply function to every telemetry row
    df["spacecraft_status"] = df.apply(classify_system_health, axis=1)

    return df



if __name__ == '__main__':
    df = pd.read_csv(DATA_DIR / 'telemetry_data_with_anomaly_status.csv')
    print(df.columns)
    df = health_status(df)
    df.to_csv(DATA_DIR / 'telemetry_data_with_health_status.csv', index=False)
    print("Health status evaluation completed. Results saved to telemetry_data_with_health_status.csv")