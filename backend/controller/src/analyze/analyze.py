"""
This file contains functions for analyzing event logs.
"""

import json

from src.analyze.event_log_analysis import EventLogAnalysis


def analyze_simod_scenario_output(simulated_event_log_df, parameters_dict):
    """
    Analyze a simod scenario output and return the results.

    Args:
        simulated_event_log_df (pandas.DataFrame): The simulated event log to analyze
        parameters_dict (dict): The parameters to analyze
    Returns:
        str: A JSON string containing the analysis results

    Curl example:
        curl -X GET http://localhost:8888/analyze/event-log -o result.json
    """

    analysis_machine = EventLogAnalysis(simulated_event_log_df, simod_params=parameters_dict)
    analysis_result = analysis_machine.full_analysis()

    return json.dumps(analysis_result)


def analyze_agent_scenario_output(simulated_event_log_df, parameters_dict):
    """
    Analyze a agent scenario output and return the results.

    Args:
        simulated_event_log_df (pandas.DataFrame): The simulated event log to analyze
    Returns:
        str: A JSON string containing the analysis results

    Curl example:
        curl -X GET http://localhost:8888/analyze/event-log -o result.json
    """

    analysis_machine = EventLogAnalysis(simulated_event_log_df, agent_param=parameters_dict)
    analysis_result = analysis_machine.full_analysis()

    return json.dumps(analysis_result)
