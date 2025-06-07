import pandas as pd

# Script för att göra nya .csv filer för att testa manuellt lite lättare
# NOTE: Denna borde nog tas bort från repo vid överlämning
# TODO: Ta bort fil helt


# NOTE: Det är brodern som har kokat ihop denna fil

# Replace with your actual file path if needed
input_file = "kev_dev/raw_data/LoanApp.csv"
output_file = "kev_dev/raw_data/filtered_0.csv"

# List of resources to keep
resources_to_keep = ["Clerk-000001", "Clerk-000002", "Loan Officer-000003", "Senior Officer-000002", "Appraiser-000002"]

# Read the CSV file
df = pd.read_csv(input_file)

# Filter rows to only include those with the specified resources
filtered_df = df[df["resource"].isin(resources_to_keep)]

# Save the filtered data to a new CSV file
filtered_df.to_csv(output_file, index=False)

print(f"{len(df) - len(filtered_df)} rows were removed. File saved as '{output_file}'.")
