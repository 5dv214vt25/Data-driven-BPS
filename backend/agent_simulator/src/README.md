# AgentSimulator
This is the supplementary GitHub repository of the paper: "AgentSimulator: An Agent-based Approach for Data-driven Business Process Simulation".

![](https://github.com/lukaskirchdorfer/AgentSimulator/blob/main/AgentSim.png)

## Prerequisites
To execute the code, you need to create an environment (e.g., with `conda create -n myenv python=3.9`) and install the dependencies in `requirements.txt` (e.g., with `install --yes --file requirements.txt`).

## How to run the AgentSimulator
To run the script simulate.py you need to specify the following parameters:

`--log_path`: path to the entire log which you need to store in the folder raw_data

`--case_id`: name of the case_id column

`--activity_name`: name of the activity column

`--resource_name`: name of the resource column

`--end_timestamp`: name of the end timestamp column

`--start_timestamp`: name of the start timestamp column

The hyperparameters handover type and whether to consider extraneous delays are determined automatically. If you do not want them to be automatically determined but want to run a specific configuration, just add the following parameters:

`--central_orchestration`: True or False (whether handovers are centrally orchestrated or autonomous)

`--extr_dealys`: True or False (whether to discover extraneous delays)

Commands to run the datasets evaluated in our paper are in run_commands.sh
The 10 simulated logs as well as train and test splits are then stored in the folder simulated_data.

## Evaluation
The simulation results can be evaluated using the evaluation.ipynb notebook in the analysis_notebooks folder.
The raw event logs as well as all simulated event logs for the 9 mentioned processes can be found in this [Google Drive folder](https://drive.google.com/file/d/10OcbxF9hSoiItb8zAb3W5oxKTiNkaXHg/view?usp=sharing).

## Additional Results 
The following table complements the results mentioned in the paper and reports all six AgentSimulator configurations across all 9 processes and all metrics. The underlying simulated log files can also be found in the Google Drive folder.

| Metric | Method   | Loan | P2P   | CVS    | C1000 | C2000 | ACR   | Prod  | BPI12 | BPI17 |
|--------|----------|------|-------|--------|-------|-------|-------|-------|-------|-------|
| NGD    | FP Orch  | 0.07 | 0.24  | 0.12   | 0.26  | 0.26  | 0.35  | 0.61  | 0.15  | 0.19  |
|        | FP Auto  | 0.08 | 0.26  | 0.12   | 0.26  | 0.26  | 0.49  | 0.74  | 0.16  | 0.30  |
|        | LS Orch  | 0.12 | 0.32  | 0.11   | 0.27  | 0.29  | 0.31  | 0.68  | 0.19  | 0.20  |
|        | LS Auto  | 0.10 | 0.30  | 0.12   | 0.29  | 0.28  | 0.29  | 0.63  | 0.26  | 0.19  |
|        | PN Orch  | 0.07 | 0.32  | 0.27   | 0.57  | 0.55  | 0.75  | 0.87  | 0.20  | 0.33  |
|        | PN Auto  | 0.65 | 0.89  | 0.84   | 0.82  | 0.82  | 0.75  | 0.71  | 0.29  | 0.18  |
| AEDD   | FP Orch  | 3.14 | 1155.01 | 86.25 | 133.42 | 234.21 | 312.2 | 58.83 | 78.19 | 221.49 |
|        | FP Auto  | 3.41 | 1139.66 | 90.13 | 191.90 | 200.25 | 285.55 | 85.99 | 68.62 | 220.98 |
|        | LS Orch  | 3.74 | 1129.31 | 83.35 | 143.08 | 250.25 | 312.55 | 65.41 | 78.76 | 235.23 |
|        | LS Auto  | 2.97 | 1154.90 | 88.96 | 144.56 | 183.86 | 281.26 | 45.34 | 100.66 | 250.71 |
|        | PN Orch  | 2.48 | 1153.77 | 87.79 | 126.40 | 236.13 | 346.59 | 4607.41 | 77.08 | 235.42 |
|        | PN Auto  | 9.06 | 1329.20 | 177.69 | 96.85 | 176.74 | 297.54 | 80.11 | 46.20 | 243.99 |
| CEDD   | FP Orch  | 0.21 | 1.00  | 7.49   | 1.66  | 1.47  | 8.33  | 5.89  | 1.83  | 1.79  |
|        | FP Auto  | 0.21 | 0.99  | 7.47   | 1.79  | 1.29  | 6.92  | 5.69  | 1.91  | 1.64  |
|        | LS Orch  | 0.23 | 1.03  | 7.46   | 1.62  | 1.39  | 6.66  | 5.69  | 1.84  | 1.63  |
|        | LS Auto  | 0.22 | 1.01  | 7.48   | 1.75  | 1.57  | 8.57  | 5.57  | 1.80  | 1.66  |
|        | PN Orch  | 0.23 | 1.09  | 7.47   | 1.93  | 1.61  | 5.86  | 6.08  | 1.87  | 1.64  |
|        | PN Auto  | 0.24 | 3.68  | 0.79   | 2.30  | 2.16  | 6.57  | 6.01  | 1.85  | 1.63  |
| REDD   | FP Orch  | 1.34 | 671.29 | 81.13 | 12.70 | 9.05  | 26.90 | 15.17 | 48.88 | 50.01 |
|        | FP Auto  | 1.64 | 675.04 | 88.31 | 21.27 | 8.66  | 26.27 | 29.05 | 43.85 | 26.03 |
|        | LS Orch  | 2.33 | 647.30 | 77.18 | 13.30 | 5.99  | 25.64 | 41.78 | 38.24 | 48.18 |
|        | LS Auto  | 1.66 | 654.98 | 87.15 | 9.48  | 12.90 | 26.83 | 22.51 | 47.07 | 59.30 |
|        | PN Orch  | 1.33 | 667.96 | 84.96 | 8.00  | 6.40  | 26.50 | 2469.70 | 56.11 | 42.51 |
|        | PN Auto  | 5.20 | 873.70 | 176.97 | 7.43  | 11.25 | 28.74 | 55.50 | 70.30 | 38.29 |
| CTDD   | FP Orch  | 1.81 | 528.58 | 100.73 | 22.31 | 16.75 | 75.79 | 25.74 | 92.12 | 54.82 |
|        | FP Auto  | 1.32 | 531.18 | 110.01 | 34.74 | 16.25 | 75.89 | 40.57 | 95.52 | 22.75 |
|        | LS Orch  | 1.44 | 510.99 | 96.22 | 24.57 | 11.46 | 75.14 | 58.84 | 82.73 | 49.27 |
|        | LS Auto  | 1.64 | 474.71 | 109.15 | 18.02 | 21.46 | 75.22 | 27.63 | 73.63 | 69.42 |
|        | PN Orch  | 1.91 | 525.40 | 101.17 | 12.34 | 10.23 | 76.63 | 2170.93 | 74.98 | 56.56 |
|        | PN Auto  | 2.86 | 715.91 | 288.62 | 8.98  | 13.74 | 80.36 | 72.17 | 103.99 | 56.53 |

## Authors
Lukas Kirchdorfer, Robert Blümel, Timotheus Kampik, Han van der Aa, Heiner Stuckenschmidt
