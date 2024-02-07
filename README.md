# Certificate-Watch
Domain/subdomain monitoring by watching new certificates and alerting via slack 

## Overview

Certificate-Watch is a powerful Python tool for monitoring SSL/TLS certificate changes and discovering new subdomains of specific domains through crt.sh. It's designed to assist security professionals, system architects, reliability engineers and administrators in keeping track of new subdomains, potentially uncovering security threats or misconfigurations early. Notifications are sent in real-time via Slack, ensuring you're always informed about changes related to your domains.

## Features

- Real-time monitoring of SSL/TLS certificate changes for specified domains.
- Detection of new subdomains using crt.sh database.
- Automated Slack notifications for new certificate and subdomain discoveries.
- Easy to set up with minimal configuration required.
- SQLite database integration for tracking and persisting discovered subdomains.

## Getting Started

### Prerequisites

- Python 3.6+
- Slack Workspace and Channel
- `requirements.txt` packages

### Installation

1. Clone the repository:

`git clone https://github.com/e-u/certificate-watch.git`

2. Install the required Python packages:

`pip install -r requirements.txt`

3. Set up your `.env` file with your Slack API Token and Channel ID:

`SLACK_API_TOKEN=your_slack_api_token`
`SLACK_CHANNEL_ID=your_slack_channel_id`


4. Add the domains you wish to monitor in `domains.txt`, one domain per line.

### Usage

Run the script with Python:

`python monitor_domains.py`

The tool will start monitoring the specified domains for new subdomains and SSL/TLS certificate changes, sending alerts to your configured Slack channel.

## Configuration

- **SLACK_API_TOKEN**: Your Slack API token for sending notifications.
- **SLACK_CHANNEL_ID**: The Slack channel ID where notifications will be sent.
- **domains.txt**: List of domains to monitor, each on a new line.

## Contributing

Contributions are welcome! Please feel free to submit pull requests, suggest features, or report bugs.

## Show Your Support

If you find this project useful, please consider giving it a star ⭐!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
