# Python Interface for LMAS Tool Wear Data

This repository contains the tool wear data used in our paper
["A Generalized Method for Featurization of Manufacturing
Signals, with Application to Tool Condition Monitoring"](http://ws680.nist.gov/publication/get_pdf.cfm?pub_id=922857)

## Data
The time series audio data for each tool is in `data/Audio Data`.

The time series acceleration data for each tool is in `data/Vibration Data`.

Metadata for each tool, including the tool wear and tool cut type is at `data/Metadata`.

All files without a file extension are plain text (space separated)

## Usage
Each file in the root directory can be used to fit a set of models or plot a set of graphs.

To plot data for a particular tool (tool 12 in this case):
```sh
python plot.py 12
```
 To plot the Power Spectral Density for a particular tool:
```sh
 python psd.py 12
```

To plot wear-vs-time for each tool:
```sh
 python wear.py 12
```

## Notebook
We also provide some simple tools for reading and pre-processing the data.
```sh
cd notebooks
jupyter visualization.ipynb
```

## Known issues
* Some data seems to be missing from metadata18.csv

## License
MIT
