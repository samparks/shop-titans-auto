import os
import csv
from datetime import datetime
from typing import List, Optional


class CSVStorage:
    """Handles writing workflow data to CSV files."""
    
    def __init__(self, workflow_name: str, columns: List[str], output_dir: str = "output"):
        self.workflow_name = workflow_name
        self.columns = ["timestamp"] + columns
        self.output_dir = output_dir
        
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        self.filepath = os.path.join(output_dir, f"{workflow_name}-{timestamp}.csv")
        
        # Write header row
        with open(self.filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writeheader()
    
    def write_row(self, **data) -> None:
        """Append a row to the CSV. Timestamp is added automatically."""
        data["timestamp"] = datetime.now().isoformat()
        
        with open(self.filepath, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writerow(data)
    
    def get_filepath(self) -> str:
        """Return the path to the CSV file."""
        return self.filepath