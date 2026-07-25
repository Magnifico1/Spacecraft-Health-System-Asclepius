import requests
import pandas as pd
from core.config import OUTPUT_DIR

# Load Llama model

from core.config import DATA_DIR

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

if mission == "earth_observation":
    from core.missions.earth_observation import mission_profile

elif mission == "lunar_exploration":
    from core.missions.lunar_exploration import mission_profile

elif mission == "deep_space":
    from core.missions.deep_space import mission_profile


# Prepare event context

def prepare_event_context(events_df):

    context = ""

    for _, event in events_df.iterrows():

        context += f"""
Subsystem: {event['subsystem']}
Event: {event['event_type']}
Rule-detected: {event['rule_detected']}
ML-detected: {event['ml_detected']}
Confidence: {event['confidence']}
Severity: {event['event_severity']}
Start time: {event['start_time']}
End time: {event['end_time']}
Duration: {event['duration']}

"""

    return context


# Generate reasoning

def generate_reasoning(events_df):

    context = prepare_event_context(events_df)

    prompt = f"""
You are an autonomous spacecraft mission operations assistant supporting a flight operations team.

Mission Profile:

Name:
{mission_profile["name"]}

Description:
{mission_profile["description"]}

{mission_profile["mission_objectives"]}

Mission Priorities:
{mission_profile["priorities"]}

Critical Subsystems:
{mission_profile["critical_subsystems"]}

Available Operator Actions:
{mission_profile["available_actions"]}

Analyse the following spacecraft event log and produce a professional engineering assessment.

Every statement in the report must be directly supported by:
- the event log,
- the mission profile, or
- logical operational consequences of the detected events.

Do not infer physical root causes, hardware faults, environmental conditions, or software defects unless they are explicitly supported by the available evidence.

If the evidence does not support a conclusion, explicitly state:
"Further investigation required."

Do not invent spacecraft systems, failures, mission phases, manoeuvres, landing procedures, or hardware that are not supported by the evidence. 
Do not introduce possible causes unless they are supported by event data or mission profile information.

If evidence is insufficient, state:
"Further investigation required."

Explain how current failures affect mission objectives.

------------------------------------------------------------
Event Log
------------------------------------------------------------

{context}

------------------------------------------------------------
Guidance
------------------------------------------------------------

Interpret confidence as follows:

High:
- Rule-based detection and ML anomaly detection agree.

Medium:
- Only one detector identified the anomaly.

Low:
- Weak or conflicting evidence.

Interpret event severity as the operational impact of an event.

Long-duration events generally indicate persistent subsystem degradation and should be prioritised over brief transient anomalies.

Only describe relationships between subsystem events if the event log provides evidence that one event plausibly contributes to another.

Do not infer causal relationships solely because events occur close together in time.
If causality cannot be established, describe the events as concurrent rather than related.
When ranking events:
1. Critical severity always outranks Warning or Investigation.
2. Within the same severity level, use confidence and duration.
3. Mission priorities may adjust ranking only when events have similar severity.

Generate an engineering report with the following sections:

1. Executive Summary
- Mission scenario (earth observation, lunar exploration, or deep) 
- Overall mission health (Normal / Degraded / Critical)
- Overall mission risk (Low / Medium / High)
- Number of confirmed failures
- Number of uncertain anomalies
- Brief summary of the spacecraft state.

2. Mission Health Assessment
- Describe the overall condition of the spacecraft.
- Explain which subsystems are most at risk.

3. Priority Assessment
Rank the events from highest to lowest operational priority.

For each event include:
- Subsystem
- Event
- Duration
- Confidence
- Event severity
- Why it is prioritised.

4. Confirmed Failures vs Uncertain Anomalies
Separate events into:
- Confirmed failures
- Uncertain anomalies requiring monitoring

Explain why each belongs in that category.

5. Subsystem Interaction Assessment
Identify any plausible relationships between subsystem events.

For example:
- Power degradation contributing to communication degradation.
- OBC overload affecting spacecraft autonomy.
- AOCS degradation affecting communication pointing.

Only report interactions supported by the event log.

6. Likely Causes
Provide likely engineering causes for each significant event.

Clearly distinguish between:
- evidence-based conclusions
- hypotheses requiring investigation

When proposing causes or operator actions that depend on spacecraft capabilities or root causes not explicitly stated in the event log or mission profile, qualify them using phrases such as 'possible', 'if available', or 'further investigation required'. Do not present hypotheses as facts.

7. Recommended Operator Actions
Prioritise recommendations.

For each recommendation provide:
- Recommended action
- Reason
- Confidence in the recommendation

Recommendations should be appropriate for spacecraft operations.

8. Overall Mission Outlook
Briefly assess:
- Immediate operational risks
- Potential cascading failures
- Most important subsystem to monitor next

Write in the style of a spacecraft flight operations engineering report.
Be concise, objective, and technically precise.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()["response"]


# Main

if __name__ == "__main__":

    events = pd.read_csv(OUTPUT_DIR / "mission_events.csv")

    report = generate_reasoning(events)

    print("\n" + "=" * 60)
    print("MISSION REASONING REPORT")
    print("=" * 60)
    print(report)