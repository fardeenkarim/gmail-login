# Gmail Login Automation

A Python script to automate logging into multiple Gmail accounts using `selenium` and `undetected-chromedriver`. This tool is designed to handle multiple accounts in batches, managing browser sessions and overcoming common bot detection mechanisms.

## Features

- **Batch Processing**: Processes accounts in configurable batches (default: 10).
- **Concurrent Execution**: Launches multiple browser instances to handle batches in parallel.
- **Anti-Detection**: Uses `undetected-chromedriver` to bypass Google's automated software detection.
- **Headless Mode Support**: Can be configured to run processing in the background.
- **Robust Navigation**: Handles various login screens and "Not now" prompts.

## Prerequisites

- Python 3.7+
- Google Chrome Browser installed
- [Pip](https://pip.pypa.io/en/stable/installation/)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gmail-login.git
   cd gmail-login
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

**Important**: For security reasons, credential files are excluded from this repository. You must create them manually.

1. Create a file named `email.csv` in the project root:
   ```csv
   email
   user1@gmail.com
   user2@gmail.com
   ...
   ```

2. Create a file named `password.csv` in the project root:
   ```csv
   password
   pass123
   pass456
   ...
   ```

   *Note: Ensure the row order in `password.csv` corresponds exactly to the `email.csv` file.*

## Usage

Run the script from the terminal:

```bash
python app.py
```

The script will:
1. Load emails and passwords.
2. Launch browser windows for each batch.
3. Automate the login process for each account.

## Disclaimer

This tool is for educational and testing purposes only. Use responsible and ensure you comply with Google's Terms of Service. The author is not responsible for any misuse or account suspensions.
