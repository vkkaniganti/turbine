import pandas as pd
from .base_reader import BaseReader

class XPRReader(BaseReader):
    def read(self):
        # Example: adjust parsing logic to real .xpr format
        df = pd.read_csv(self.filepath, sep="\t")  # assuming tab-separated
        return df.values.tolist()
