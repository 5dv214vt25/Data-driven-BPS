# Stage 1: Base with Java 8
FROM openjdk:8 as base

# Stage 2: Python + Java
FROM python:3.9-slim

WORKDIR /simod

COPY simod/requirements.txt /simod/
RUN pip install --no-cache-dir -r requirements.txt

COPY simod /simod/

EXPOSE 6001

CMD ["echo", "Simod container running"]

#pytest pytest-asyncio flake8 pep8-naming flask black isort click >=8.1.3,<9.0.0 hyperopt >=0.2.7,<0.3.0 lxml >=4.9.2,<5.0.0 matplotlib >=3.6.0,<4.0.0 networkx >=3.1,<4.0.0 numpy >=1.24.3,<2.0.0 pandas >=2.1.0,<3.0.0 pendulum >=2.1.2,<3.0.0 pydantic >=2.3.0,<3.0.0 python-dotenv >=1.0.0,<2.0.0 python-multipart >=0.0.6,<1.0.0 pytz >=2023.3,<2024.0.0 PyYAML >=6.0,<7.0.0 requests >=2.28.2,<3.0.0 scipy >=1.10.1,<2.0.0 statistics >=1.0.3.5,<2.0.0 tqdm >=4.64.1,<5.0.0 xmltodict >=0.13.0,<1.0.0 prosimos >=2.0.5,<3.0.0 extraneous-activity-delays >=2.1.21,<3.0.0 openxes-cli-py >=0.1.15,<1.0.0 pix-framework >=0.13.16,<1.0.0 log-distance-measures >=1.0.2,<2.0.0
