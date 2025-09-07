# Turbine Data Processor

## Overview

This application processes turbine blade scan data to identify and correct deviations from the nominal design. It reads raw scan data (`.XPR` files) and nominal data (`.XPN` files), calculates the deviation, applies corrections to bring the data within tolerance, and generates detailed reports and corrected data files.

## How to Run

To run the application, execute the `main.exe` file.

```
main.exe
```

This will launch a graphical user interface (GUI) where you can select the input folders.

## Input

The application requires two input folders:

1.  **RAW Folder**: This folder should contain the raw scan data files with the `.XPR` extension.
2.  **NOM Folder**: This folder should contain the nominal design data files with the `.XPN` extension.

For each `.XPR` file in the `RAW` folder, there must be a corresponding `.XPN` file with the same base name in the `NOM` folder.

## Output

The application generates output files in two folders: `Reports` and `logs`.

### Reports

The `Reports` folder will contain the following files for each processed input file:

-   `*_original.csv`: A CSV report of the initial deviation analysis before any correction.
-   `*_corrected.csv`: A CSV report of the deviation analysis after correction.
-   `*_corrected.pdf`: A PDF version of the corrected report.
-   `*_Correction.XPR`: A corrected version of the raw scan data file.

### Logs

The `logs` folder contains detailed log files for each processed input file. Each log file is named after the input file (e.g., `SEC_A4.log`) and contains information about the processing steps, including any errors or warnings (such as missing NOM files).

## Project Structure

Create the folder structure as below 
```
.
├── Reports/              # Output folder for reports and corrected files
├── logs/                 # Output folder for log files
├── data/
│   ├── RAW/              # Input folder for RAW (.xpr) files
│   └── NOM/              # Input folder for NOM (.xpn) files
├── main.exe              # Executable to run the application
├── ...
```
