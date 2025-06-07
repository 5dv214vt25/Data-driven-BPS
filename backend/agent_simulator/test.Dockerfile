FROM python:3.9-slim

WORKDIR /agent_simulator_test

COPY agent_simulator/requirements.txt /agent_simulator_test/
RUN pip install --no-cache-dir -r requirements.txt

COPY agent_simulator /agent_simulator_test/

RUN mkdir -p /agent_simulator_test/pickle_resources

COPY agent_simulator/tests/test_resources agent_simulator_test/pickle_resources/

EXPOSE 6003

CMD ["echo", "Running agent_sim test container"]
