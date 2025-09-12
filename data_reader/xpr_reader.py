from typing import List, Any, Dict
import pandas as pd
from pandas.errors import EmptyDataError, ParserError
from .base_reader import BaseReader


class XPRReader(BaseReader):
    """
    A reader for parsing .xpn files.

    This implementation assumes the .xpn format is a delimited text file,
    configurable via options passed to the pandas.read_csv function.
    """

    def __init__(self, filepath: str, **kwargs: Any):
        """
        Initializes the XPNReader.

        Args:
            filepath: The path to the .xpn file.
            **kwargs: Keyword arguments to be passed to pandas.read_csv.
                      This allows for customization of the parsing process
                      (e.g., sep, header, names).
        """
        super().__init__(filepath)
        self.read_options: Dict[str, Any] = kwargs

    def read(self):
        """
        Reads a .xpr file with format:
        Raw Scan Data Listing ...
        Data Seq:X,Y,Z,I,J,K
        Point Number ...
            1   -18.3390 -24.7582 ...
        Returns: pandas DataFrame with columns [Point#, X, Y, Z, I, J, K]
        """
        data = []
        start_reading = False

        with open(self.filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Detect start of numeric data (lines starting with a number)
                if line[0].isdigit():
                    start_reading = True

                if start_reading:
                    parts = line.split()
                    if len(parts) >= 7:  # PointNumber + 6 values
                        values = [float(x) for x in parts[0:7]]
                        data.append(values)

        # Create DataFrame
        df = pd.DataFrame(data, columns=["Point#", "X", "Y", "Z", "I", "J", "K"])
        return df.round(3)