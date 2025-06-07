def compute_activity_transition_dict_global(business_process_data):
    sequences = create_sequences_global(business_process_data)

    sequence_parts, next_act = create_labeled_sequences_global(sequences)

    dict_ = {}
    for i in range(len(next_act)):
        if sequence_parts[i] not in dict_.keys():
            dict_[sequence_parts[i]] = {next_act[i]: 1}
        else:
            if next_act[i] not in dict_[sequence_parts[i]].keys():
                dict_[sequence_parts[i]][next_act[i]] = 1
            else:
                dict_[sequence_parts[i]][next_act[i]] += 1

    for k, v in dict_.items():
        sum_values = 0
        for key, value in v.items():
            sum_values += value
        for key, value in v.items():
            v[key] = value / sum_values

    return dict_


def compute_activity_transition_dict(business_process_data):
    sequences, active_agents = create_sequences(business_process_data)
    sequence_parts, next_act, active_agent = create_labeled_sequences(sequences, active_agents)

    # Initialize a nested dictionary to store transition probabilities per agent
    dict_ = {}

    for i in range(len(next_act)):
        # Extract the agent of the current sequence part
        agent = active_agent[i]

        # Check if the sequence part exists in the dictionary
        if sequence_parts[i] not in dict_.keys():
            dict_[sequence_parts[i]] = {agent: {next_act[i]: 1}}
        else:
            # Check if the agent exists for the sequence part
            if agent not in dict_[sequence_parts[i]].keys():
                dict_[sequence_parts[i]][agent] = {next_act[i]: 1}
            else:
                # Check if the next activity exists for the agent
                if next_act[i] not in dict_[sequence_parts[i]][agent].keys():
                    dict_[sequence_parts[i]][agent][next_act[i]] = 1
                else:
                    dict_[sequence_parts[i]][agent][next_act[i]] += 1

    # Normalize transition probabilities for each agent and sequence part
    for seq_part, agents in dict_.items():
        for agent, transitions in agents.items():
            sum_values = sum(transitions.values())
            for key, value in transitions.items():
                transitions[key] = value / sum_values

    return dict_


# Function to create sequences of activities for each case
def create_sequences(df):
    df = df.sort_values(by=["case_id", "start_timestamp"])
    sequences = []
    active_agents = []
    for case_id, group in df.groupby("case_id"):
        sequences.append(list(group["activity_name"]))
        active_agents.append(list(group["agent"]))
    return sequences, active_agents


# Function to create sequences of activities for each case
def create_sequences_global(df):
    df = df.sort_values(by=["case_id", "start_timestamp"])
    sequences = []
    for case_id, group in df.groupby("case_id"):
        sequences.append(list(group["activity_name"]))
    return sequences


def create_labeled_sequences(encoded_sequences, active_agents):
    max_window_size = max(len(seq) for seq in encoded_sequences)
    x = []  # Initialize an empty list to store input sequences
    y = []  # Initialize an empty list to store target sequences
    active_agent = []

    counter = 0
    # Iterate over each encoded sequence in the input list
    for seq in encoded_sequences:
        # Iterate over different window sizes
        for window_size in range(1, max_window_size + 1):
            # Iterate over each index up to len(seq) - window_size
            for i in range(len(seq) - window_size):
                # Append the window of size window_size to x
                x.append(tuple(seq[i : i + window_size]))
                # Append the element immediately following the window to y
                y.append(seq[i + window_size])
                active_agent.append(active_agents[counter][i + window_size - 1])
        counter += 1
    return x, y, active_agent


def create_labeled_sequences_global(encoded_sequences):
    max_window_size = max(len(seq) for seq in encoded_sequences)
    x = []  # Initialize an empty list to store input sequences
    y = []  # Initialize an empty list to store target sequences

    # Iterate over each encoded sequence in the input list
    for seq in encoded_sequences:
        # Iterate over different window sizes
        for window_size in range(1, max_window_size + 1):
            # Iterate over each index up to len(seq) - window_size
            for i in range(len(seq) - window_size):
                # Append the window of size window_size to x
                x.append(tuple(seq[i : i + window_size]))
                # Append the element immediately following the window to y
                y.append(seq[i + window_size])
    return x, y
