import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from core.config import DATA_DIR

#----------------------------------------------------------------------------
# Define all available telemetry variables for each subsystem
#----------------------------------------------------------------------------
subsystem_features = {
    'power': [
        'battery_voltage', 'battery_current', 'solar_array_power',
        "battery_state_of_charge", "solar_generation",
        # Deep Space
        'rtg_output'],

    'thermal': [
        'battery_temp', 'bus_temp', 'payload_temp',
        # Lunar Exploration
        "radiator_temperature", "heater_power",
        # Deep Space
        'processor_temperature'],

    'aocs': [
        'reaction_wheel_speed', 'gyro_drift',
        # Earth Observation
        'pointing_error', 'attitude_accuracy'],

    'communication': [
        'communication_signal', 'data_rate', 'packet_loss',
        # Earth Observation
        'downlink_rate', 'ground_station_visibility',
        # Lunar Exploration
        'earth_visibility', 'link_margin',
        # Deep Space
        'antenna_status', 'signal_to_noise_ratio'],

    'propulsion': [
        'fuel_level', 'thruster_temp', 'thrust_level',
        # Deep Space
        'trajectory_error', 'delta_v_remaining'],

    'obc': [
        'cpu_load', 'memory_usage',
        # Deep Space
        'memory_integrity'],

    # Earth Observation only
    'optics': [
        'camera_temperature', 'image_quality', 'imaging_power'],
    
    # Lunar Exploration only
    'mobility': [
        'wheel_slip_ratio', 'terrain_slope' 'surface_speed']
}

#----------------------------------------------------------------------------
# Fit an Isolation Forest model for each subsystem on nominal telemetry
#----------------------------------------------------------------------------
contamination_rate = .03

def train_models(df):
    models = {}

    for subsystem, features in subsystem_features.items():

         # Only use telemetry that exists for this mission
        available_features = [
            feature
            for feature in features
            if feature in df.columns
        ]

        # Skip unavailable subsystems
        if len(available_features) == 0:
            continue

        X = df[available_features]
        model = IsolationForest(contamination=contamination_rate, random_state=42)
        model.fit(X)
        models[subsystem] = {"model": model, "features": available_features}

    return models


#----------------------------------------------------------------------------
# Apply Isolation Forest model for each subsystem on mission telemetry
#----------------------------------------------------------------------------
def apply_anomaly_models(df, models):
    
    for subsystem, model_data in models.items():
        model = model_data['model']
        features = model_data['features']
 
        X = df[features]
        predictions = model.predict(X)
        df[f'{subsystem}_anomaly_score'] = model.decision_function(X)
        df[f'{subsystem}_anomaly_prediction'] = predictions
        df[f"{subsystem}_anomaly_status"] = np.where(predictions == -1, "Anomaly", "Normal")

    return df

if __name__ == '__main__':
    nominal_mission_telemetry = pd.read_csv(DATA_DIR / 'nominal_mission_telemetry.csv')
    mission_telemetry = pd.read_csv(DATA_DIR / 'mission_telemetry.csv')

    models = train_models(nominal_mission_telemetry)
    mission_telemetry = apply_anomaly_models(mission_telemetry, models)

    mission_telemetry.to_csv(DATA_DIR / "telemetry_data_with_anomaly_status.csv", index=False)
    print("Anomaly detection completed. Results saved to telemetry_data_with_anomaly_status.csv")
