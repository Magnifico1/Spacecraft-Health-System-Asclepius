import pandas as pd
import numpy as np
from core.config import DATA_DIR
from core.config import mission


# Generate nominal core telemetry

def generate_nominal_core_telemetry(num_points=5000):
    np.random.seed(42) 

    time = np.arange(num_points)

    # Power subsystem
    battery_voltage = 4.1 - .00005*time + np.random.normal(0, .02, num_points)
    battery_current = 1.5 + np.random.normal(0, .05, num_points)
    solar_array_power = 120 + np.random.normal(0, 5, num_points)
    battery_state_of_charge = (90 + np.random.normal(0, 2, num_points))

    # Thermal subsystem
    battery_temp = 25 + np.random.normal(0, .4, num_points)
    bus_temp = 22 + np.random.normal(0, .3, num_points)
    payload_temp = 19 + np.random.normal(0, .5, num_points)

    # Attitude and Orbital Control subsystem
    reaction_wheel_speed = 6000 + np.random.normal(0, 40, num_points)
    gyro_drift = np.random.normal(0, .01, num_points)

    # Communication subsystem
    communication_signal = 80 + np.random.normal(0, 2, num_points)
    data_rate = 50 + np.random.normal(0, 3, num_points) #in Mbps
    packet_loss = np.abs(np.random.normal(.5, .2, num_points)) #in percent

    # Propulsion subsystem
    fuel_level = 100 - .001*time + np.random.normal(0, .1, num_points) #in percent
    thruster_temp = 30 + np.random.normal(0, .5, num_points)
    thrust_level = np.random.choice([0, 0.2, 0.5, 1.0],
                                    size=num_points,
                                    p=[0.5, 0.2, 0.25, 0.05]
                                    )

    # On-board Computer subsystem
    cpu_load = 40 + np.random.normal(0, 10, num_points)
    memory_usage = 60 + np.random.normal(0, 5, num_points) 

    # Combine telemetry data into dataframe
    telemetry = pd.DataFrame({
        'time': time,
        'battery_voltage': battery_voltage,
        'battery_current': battery_current,
        'battery_state_of_charge': battery_state_of_charge,
        'solar_array_power': solar_array_power,
        'battery_temp': battery_temp,
        'bus_temp': bus_temp,
        'payload_temp': payload_temp,
        'reaction_wheel_speed': reaction_wheel_speed,
        'gyro_drift': gyro_drift,
        'communication_signal': communication_signal,
        'data_rate': data_rate,
        'packet_loss': packet_loss,
        'fuel_level': fuel_level,
        'thruster_temp': thruster_temp,
        'thrust_level': thrust_level,
        'cpu_load': cpu_load,
        'memory_usage': memory_usage
    })

    return telemetry


# Generate nominal telemetry including both core and mission-specific variables

def generate_specific_telemetry(df, mission):
    """
    Add mission-specific telemetry variables on top of
    the generic spacecraft telemetry.

    Parameters:
        df: dataframe containing core spacecraft telemetry
        mission: earth_observation, lunar, or deep_space

    Returns:
        dataframe with additional mission telemetry
    """

    df = df.copy()
    n = len(df)

    # Earth Observation Mission

    if mission == "earth_observation":

        # Optics
        df["camera_temperature"] = (20 + np.random.normal(0, 0.5, n))
        df["image_quality"] = (95 + np.random.normal(0, 2, n))
        df["imaging_power"] = (100 + np.random.normal(0, 5, n))

        # Communication
        df["downlink_rate"] = (50 + np.random.normal(0, 3, n))
        df["ground_station_visibility"] = np.random.choice([0, 1], size=n, p=[.08, .92])

        # AOCS
        df["pointing_error"] = (0.05 + np.random.normal(0, 0.01, n))
        df["attitude_accuracy"] = (99 + np.random.normal(0, 0.5, n))

    # Lunar Mission

    elif mission == "lunar_exploration":

        # Thermal
        df["radiator_temperature"] = (30 + np.random.normal(0, 1, n))
        df["heater_power"] = (40 + np.random.normal(0, 3, n))

        # Communication
        df["earth_visibility"] = np.random.choice([0, 1], size=n, p=[0.4, 0.6])
        df["link_margin"] = (20 + np.random.normal(0, 2, n))

        # Mobility
        df['wheel_slip_ratio'] = np.random.normal(0.1, 0.03, n)
        df['terrain_slope'] = np.random.normal(0, 5, n)
        df["surface_speed"] = (2.5 + np.random.normal(0,0.2,n))

    # Deep Space Mission

    elif mission == "deep_space":

        # Power
        df["rtg_output"] = (np.linspace(300, 280, n) + np.random.normal(0, 2, n))

        # Communication
        df["antenna_status"] = np.ones(n)
        df["signal_to_noise_ratio"] = (50 + np.random.normal(0, 3, n))

        # AOCS
        df["trajectory_error"] = (0.1 + np.random.normal(0, 0.02, n))

        # Propulsion
        df["delta_v_remaining"] = (np.linspace(100, 70, n) + np.random.normal(0, 0.5, n))
    
        # OBC 
        df["processor_temperature"] = (35 + np.random.normal(0, 1, n))
        df["memory_integrity"] = (100 + np.random.normal(0, 0.5, n))

    else:
        raise ValueError(f"Unknown mission profile: {mission}")

    return df


# Fault injection

def get_fault_windows(mission):

    if mission == "earth_observation":

        return {
            "power": (.15, .25),
            "thermal": (.55, .60),
            "aocs": (.65, .75),
            "communication": (.05, .18),
            "propulsion": (.70, .73),
            "obc": (.85, .93)
        }

    elif mission == "lunar_exploration":

        return {
            "power": (.30, .40),
            "thermal": (.15, .20),
            "aocs": (.55, .65),
            "communication": (.4, .45),
            "propulsion": (.75, .88),
            "obc": (.90, .95)
        }

    elif mission == "deep_space":

        return {
            "power": (.65, .75),
            "thermal": (.40, .50),
            "aocs": (.20, .30),
            "communication": (.70, .80),
            "propulsion": (.10, .15),
            "obc": (.50, .55)
        }

    else:
        raise ValueError("Unknown mission")

def apply_ramp(df, column, start, end, start_value, end_value):
    length = end - start
    ramp = np.linspace(start_value, end_value, length)
    df.loc[start:end-1, column] += ramp

    # Major events

def inject_faults(df): 

    n = len(df)
    df = df.copy()
    events = []

    windows = get_fault_windows(mission)

    def get_window_indices(window):
        start = int(n * window[0])
        start = max(0, start)  
        end = int(n * window[1])
        end = min(n, end)
        return start, end

    # Power subsystem
    start, end = get_window_indices(windows['power'])

    apply_ramp(df, 'battery_voltage', start, end, 0, -1)
    apply_ramp(df, 'battery_current', start, end, 0, 2)
    apply_ramp(df, 'solar_array_power', start, end, 0, -30)
    apply_ramp(df, 'battery_state_of_charge', start, end, 0, -40)

    # Thermal subsystem

    start, end = get_window_indices(windows['thermal'])

    apply_ramp(df, 'battery_temp', start, end, 0, 10)
    apply_ramp(df, 'bus_temp', start, end, 0, 10)
    apply_ramp(df, 'payload_temp', start, end, 0, 10)
   
    # Attitude and Orbital Control subsystem

    start, end = get_window_indices(windows['aocs'])

    apply_ramp(df, 'reaction_wheel_speed', start, end, 0, 800)
    apply_ramp(df, 'gyro_drift', start, end, 0, .05)

    # Communication subsystem

    start, end = get_window_indices(windows['communication'])

    apply_ramp(df, 'communication_signal', start, end, 0, -10)
    apply_ramp(df, 'data_rate', start, end, 0, -20)
    apply_ramp(df, 'packet_loss', start, end, 0, 5)

    # Propulsion subsystem

    start, end = get_window_indices(windows['propulsion'])

    apply_ramp(df, 'fuel_level', start, end, 0, -18)
    apply_ramp(df, 'thruster_temp', start, end, 0, 20)
    apply_ramp(df, 'thrust_level', start, end, 0, 0.5)

    # On-board Computer subsystem
    start, end = get_window_indices(windows['obc'])

    apply_ramp(df, 'cpu_load', start, end, 0, 70)
    apply_ramp(df, 'memory_usage', start, end, 0, 40)


    # Minor events

    # Power subsystem
    start = 800
    end = 950
    apply_ramp(df, 'battery_voltage', start, end, 0, -0.4)

    start = 1400
    end = 1450
    apply_ramp(df, 'battery_current', start, end, 0, 0.15)

    # Thermal subsystem
    start = 1200
    end = 1450
    apply_ramp(df,'bus_temp',start,end,0,5)

    # AOCS
    start = 1600
    end = 1700
    apply_ramp(df,'gyro_drift',start,end,    0,0.025)

    # Commumnication
    start = 200
    end = 350
    apply_ramp(df,'communication_signal',start,end,0,-4)

    # Propulsion
    start = 2700
    end = 2800
    apply_ramp(df, 'thrust_level', start, end, 0, 0.25)

    # OBC
    start = 3900
    end = 4050
    apply_ramp(df, 'cpu_load', start, end, 0, 30)


    # Mission-specific fault injection

    if mission == "earth_observation": 
        inject_eo_faults(df)

    elif mission == "lunar_exploration": 
        inject_lunar_faults(df)

    elif mission == "deep_space": 
        inject_deep_space_faults(df)
        
    return df


def inject_eo_faults(df):

    n = len(df)

    # Power
    # Camera overheating
    start = int(n * 0.25)
    end = int(start+350)
    apply_ramp(df,"camera_temperature",start,end,0,15)

    # Image quality degradation
    start = int(n * 0.45)
    end = int(start+150)
    apply_ramp(df,"image_quality",start,end,0,-40)

    start = int(n * 0.80)
    end = int(start + 100)
    apply_ramp(df,"image_quality",start,end,0,-10)

    # Imaging power increase
    start = int(n * 0.65)
    end = int(start+150)
    apply_ramp(df,"imaging_power",start,end,0,40)

    # AOCS
    # Pointing drifts
    start = int(n * 0.35)
    end = int(start+15)
    apply_ramp(df,"pointing_error",start,end,0,1.5)

    # Attitude fault
    start = int(n * 0.55)
    end = int(start+150)
    apply_ramp(df,"attitude_accuracy",start,end,0,-10)

    # Communication
    # Reduced downlink capability
    start = int(n * 0.75)
    end = int(start+150)
    apply_ramp(df,"downlink_rate",start,end,0,-25)

    # Ground station outage
    start = int(n * 0.85)
    end = int(start+20)
    df.loc[start:end,"ground_station_visibility"] = 0


def inject_lunar_faults(df):

    n = len(df)

    # Power
    # battery degradation
    start = int(n * 0.72)
    end = int(start + 75)
    df.loc[start:end, "battery_state_of_charge"] = 66

    # Radiator degradation
    start = int(n * 0.60)
    end = int(start + 100)
    apply_ramp(df,"radiator_temperature",start,end,0,10)

    # Heater overuse
    start = int(n * 0.55)
    end = int(start+170)
    apply_ramp(df,"heater_power",start,end,0,30)

    # Communication
    # Communication window degradation
    start = int(n * 0.70)
    end = int(start+50)
    df.loc[start:end-1, "earth_visibility"] = 0
    apply_ramp(df,"link_margin",start,end,0,-15)

    start = int(n * 0.85)
    end = int(start + 60)
    apply_ramp(df,"link_margin",start,end,0,-7)

    # Propulsion
    start = int(n * 0.65)
    end = int(start + 100)
    df.loc[start:end,"thrust_level"] = 1

    # Fuel consumption anomaly
    start = int(n * 0.45)
    end = int(start + 150)
    apply_ramp(df,"fuel_level",start,end,0,-45)

    # Mobility
    start = int(n * 0.80)
    end = start + 150
    apply_ramp(df,"wheel_slip_ratio",start,end,0,0.55)

    start = int(n * 0.30)
    end = start + 100
    apply_ramp(df,"wheel_slip_ratio",start,end,0,0.35)

    start = int(n * .80)
    end = int(start + 200)
    apply_ramp(df, 'terrain_slope', start, end,0, 30)

    start = int(n * .05)
    end = int(start + 200)
    apply_ramp(df, 'terrain_slope', start, end,0, 35)

    start = int(n * 0.80)
    end = int(start + 200)
    apply_ramp(df,"surface_speed",start,end,0,-2)


def inject_deep_space_faults(df):

    n = len(df)

    # RTG degradation
    start = int(n * 0.30)
    end = int(start+400)
    apply_ramp(df,"rtg_output",start,end,0,-50)

    # Processor overheating
    start = int(n * 0.50)
    end = int(start+200)
    apply_ramp(df,"processor_temperature",start,end,0,15)

    # Signal degradation
    start = int(n * 0.65)
    end = int(start+40)
    apply_ramp(df,"signal_to_noise_ratio",start,end,0,-20)

    # Trajectory drift
    start = int(n * 0.80)
    end = int(start+200)
    apply_ramp(df,"trajectory_error",start,end,0,5)

    # Antenna failure
    start = int(n * 0.35)
    end = int(start+400)
    df.loc[start:end, "antenna_status"] = 0

    # Delta-v depletion
    start = int(n * 0.70)
    end = int(start+350)
    apply_ramp(df, "delta_v_remaining", start, end, 0, -40)

    # Memory integrity degradation
    start = int(n * 0.55)
    end = int(start+150)
    apply_ramp(df,"memory_integrity",start,end,0,-8)


# Output data
def generate_mission_telemetry(num_points=5000):
    nominal_core_telemetry = generate_nominal_core_telemetry(num_points)
    nominal_core_telemetry.to_csv(DATA_DIR / "nominal_core_telemetry.csv", index=False)
    nominal_mission_telemetry = generate_specific_telemetry(nominal_core_telemetry, mission=mission)
    nominal_mission_telemetry.to_csv(DATA_DIR / "nominal_mission_telemetry.csv", index=False)
    mission_telemetry = inject_faults(nominal_mission_telemetry)
    return mission_telemetry

# Main
if __name__ == "__main__":
    mission_telemetry = generate_mission_telemetry()
    mission_telemetry.to_csv(DATA_DIR / "mission_telemetry.csv", index=False)
    print("Nominal core telemetry data generated and saved to nominal_core_telemetry.csv")
    print("Nominal mission-specific telemetry data generated and saved to nominal_mission_telemetry.csv")
    print("Mission-specific telemetry data generated and saved to mission_telemetry.csv")
