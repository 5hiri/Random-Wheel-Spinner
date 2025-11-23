# Random Wheel Spinner

A modern desktop application for spinning a random wheel, built with Python and CustomTkinter.

## Features

- **Spin the Wheel**: Spinning animation with physics-based easing.
- **Manage Entries**: Add and remove entries easily.
- **Weighted Probabilities**: Assign weights to entries (e.g., 2.0 for double chance).
- **Save & Load**: Save your wheel configurations to your local application data folder.
- **Configuration Management**: Rename, delete, and load saved wheels.

## Installation

1.  Ensure you have Python installed.
2.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the application:

```bash
python main.py
```

## Data Location

Your saved wheel configurations are stored in your system's default application data directory (e.g., `%LOCALAPPDATA%\User\RandomWheelSpinner` on Windows).
