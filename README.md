# Rosbag Parser
This is a Python project that utilizes the ROS (Robot Operating System) and Pandas libraries to process data from bag files and save the data on .csv files.

## Prerequisites
Before running this project, make sure you have the following installed:

- ROS (Robot Operating System)
- Pandas library
- Python 3

## Installation

1. Clone this repository.
```git clone https://github.com/username/project.git```
2. Navigate into the project directory.
3. Install the required Python packages using pip.
```pip install -r requirements.txt```

## Usage

1. Place your bag file(s) in a folder.
2. Run the script using the following command:
```python3 rosbag_parser.py /path/to/rosbag/folder```
3. This creates csvs for each rosbag, with the same name and will be saved in the rosbag directory.

