"""
This module is responsible for managing Simod and Prosimos.
It contains the functions that can be used by the controller
to access the simod simulator.
"""

# Module-level constants
MODEL_NAME = "simod_simulator_manager"
MODEL_VERSION = "1.0.0"
MODEL_DESCRIPTION = "Module for managing Simod and Prosimos."


# ========= Public module functions =========
__all__ = ["create_test_message_simod_simulator_manager"]


def create_test_message_simod_simulator_manager():
    """
    Create a test message for the Simod simulator manager.

    Returns:
        str: A simple test message from the Simod simulator manager.
    """
    return "Hello, this is a simple test message from the simod simulator manager!"


# ========= Private module functions =========
def _example_helper_function():
    """
    Example helper function.

    Returns:
        str: An example message from a helper function.
    """
    return "This is an example of a helper function."
