"""
Monitoring Certificate Changes on CRT.SH for Target Domains
"""

import logging
import os
import sqlite3
import time
from datetime import datetime
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SLACK_TOKEN = os.getenv("SLACK_API_TOKEN")
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

if not SLACK_TOKEN or not CHANNEL_ID:
    raise ValueError("Slack Token or Channel ID not found in .env file")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Slack client
slack_client = WebClient(token=SLACK_TOKEN)


class DomainMonitor:
    def __init__(self, db_path='subdomains.db', domains_file='domains.txt'):
        self.db_path = db_path
        self.domains = self._load_domains(domains_file)
        self._setup_database()

    @staticmethod
    def _load_domains(domains_file):
        with open(domains_file, 'r') as file:
            return [line.strip() for line in file if line.strip()]

    def _setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS known_subdomains (
                    domain TEXT,
                    subdomain TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (domain, subdomain)
                )''')
            conn.commit()

    @staticmethod
    def _fetch_certificates(domain):
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error querying crt.sh: {response.text}")
        return {cert['name_value'] for cert in response.json() if '*' not in cert['name_value']}

    def _store_subdomains(self, domain, subdomains):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                'INSERT OR IGNORE INTO known_subdomains (domain, subdomain) VALUES (?, ?)',
                [(domain, sub) for sub in subdomains]
            )
            conn.commit()

    @staticmethod
    def _send_to_slack(message):
        try:
            slack_client.chat_postMessage(channel=CHANNEL_ID, text=message)
            logging.info("Message sent to Slack.")
        except SlackApiError as e:
            logging.error(f"Slack API Error: {e.response['error']}")

    def monitor_domains(self):
        logging.info("Starting domain monitoring...")
        while True:
            for domain in self.domains:
                try:
                    logging.info(f"Checking {domain} for new subdomains...")
                    current_subdomains = self._fetch_certificates(domain)
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT subdomain FROM known_subdomains WHERE domain = ?', (domain,))
                        stored_subdomains = {row[0] for row in cursor.fetchall()}
                    new_subdomains = current_subdomains - stored_subdomains
                    if new_subdomains:
                        message = f"New subdomains for {domain} detected:\n" + "\n".join(new_subdomains)
                        self._send_to_slack(message)
                        self._store_subdomains(domain, new_subdomains)
                        logging.info(f"New subdomains for {domain} found: {', '.join(new_subdomains)}")
                    else:
                        logging.info(f"No new subdomains found for {domain}.")
                except Exception as e:
                    logging.error(f"Error monitoring {domain}: {e}")
                    self._send_to_slack(f"Error monitoring {domain}: {e}")
            time.sleep(3600)  # Pause for 1 hour before the next check


if __name__ == "__main__":
    monitor = DomainMonitor()
    monitor.monitor_domains()
