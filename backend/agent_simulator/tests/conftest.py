import os
import sys

# File is used for managing imports from the src directory.
# Note that if your workspace has real time linting or similar (any IDE nowadays),
# it will complain on imports, this is a local static problem and not a
# problem when actually executing the code, since the path is set to the source folder.
# However all tests for agetnt_sim should be able to run localy in a venv by doing:
# cd ~/agent_simulator/tests
# pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
