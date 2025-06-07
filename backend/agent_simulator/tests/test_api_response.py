import json
import socket
import subprocess
import time
import unittest
import zipfile
from io import BytesIO

import requests

# NOTE: TODO: This test file includes a test that is does not pass localy on every computer, this is something that should be looked into.
#             This however is not the case when ran in the pipeline, we dont currently know what causes this test to fail on certain computers,
#             but it is most likely a windows - linux problem or a requirements in venv problem.


def wait_for_port(host, port, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError(f"Server at {host}:{port} did not start in time")


class TestAPIResponse(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api_url = "http://localhost:6002/api/start-agent-discovery"
        cls.api_process = subprocess.Popen(["python", "../src/api.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wait_for_port("localhost", 6002)

    @classmethod
    def tearDownClass(cls):
        cls.api_process.terminate()
        try:
            cls.api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.api_process.kill()

    def get_discovery_response(self, file_path, parameter_path=None):
        with open(file_path, "rb") as f:
            if parameter_path:
                with open(parameter_path, "rb") as p:
                    files = {"event_log": f, "parameters": p}
                    return requests.post(self.api_url, files=files)
            else:
                files = {"event_log": f}
                return requests.post(self.api_url, files=files)

    def validate_zip_response(self, response, expected_keys):
        if response.status_code != 200:
            print("Response status code:", response.status_code)
            print("Response content:\n", response.text)
        self.assertEqual(response.status_code, 200)
        with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
            self.assertEqual(set(zip_file.namelist()), {"model.pkl", "params.json", "visualization.json"})
            data = json.loads(zip_file.read("visualization.json").decode("utf-8"))
            self.assertIsInstance(data, dict)
            for key, t in expected_keys.items():
                self.assertIn(key, data)
                self.assertIsInstance(data[key], t)

    def test_discovery_with_various_inputs(self):
        cases = [
            {"file": "test_resources/LoanAppSmall.csv", "params": None},
            {"file": "test_resources/LoanAppSmall.csv", "params": "test_resources/start_discovery_params.json"},
        ]
        expected_keys = {
            "agent_nodes": str,
            "agent_edges": str,
            "role_nodes": str,
            "role_edges": str,
            "activity_nodes": str,
            "activity_edges": str,
            "activity_flow": str,
        }

        for case in cases:
            with self.subTest(case=case):
                response = self.get_discovery_response(case["file"], case["params"])
                self.validate_zip_response(response, expected_keys)


if __name__ == "__main__":
    unittest.main()
