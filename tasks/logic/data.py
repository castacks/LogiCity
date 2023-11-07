import numpy as np
from torch.utils.data import Dataset
from prettytable import PrettyTable

class LogicDataset(Dataset):
    def __init__(self, dataX, dataY, Xname, Yname, adjust=False):
        self.dataX = dataX
        self.dataY = dataY
        self.Yname = Yname  # Store the Yname
        
        if adjust:
            self.print_distribution("Before adjustment")
            self.balance_data()
            self.print_distribution("After adjustment")
        else:
            self.print_distribution("Dataset distribution")

    def print_distribution(self, message):
        unique_rows, counts = np.unique(self.dataY, axis=0, return_counts=True)

        # Create a PrettyTable instance
        table = PrettyTable()
        # Use Yname for the field names
        table.field_names = self.Yname + ["Count"]
        table.title = message

        # Populate the table with data
        for row, count in zip(unique_rows, counts):
            # Convert row to labels using Yname
            label_row = [self.Yname[i] if x == 1 else "" for i, x in enumerate(row)]
            table.add_row(label_row + [count])

        # Sort the table by the 'Count' column
        table.sortby = "Count"
        table.reversesort = True

        print(table)

    def balance_data(self):
        # Get all unique rows and their counts
        unique_rows, counts = np.unique(self.dataY, axis=0, return_counts=True)
        unique_counts = dict(zip(map(tuple, unique_rows), counts))

        # Find the minimum occurrence across unique rows
        min_count = min(unique_counts.values())

        # Initialize new balanced data containers
        new_dataX = []
        new_dataY = []

        # Iterate over each unique row and sample the necessary number of instances
        for row in unique_rows:
            indices = np.where((self.dataY == row).all(axis=1))[0]
            sampled_indices = np.random.choice(indices, min_count, replace=False)
            new_dataX.append(self.dataX[sampled_indices])
            new_dataY.append(self.dataY[sampled_indices])

        # Concatenate the balanced data
        self.dataX = np.vstack(new_dataX)
        self.dataY = np.vstack(new_dataY)

    def __len__(self):
        return self.dataX.shape[0]

    def __getitem__(self, idx):
        return self.dataX[idx], self.dataY[idx]
