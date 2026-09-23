#!/usr/bin/env python3
import csv
import socket
import sys
import os

# DogStatsD configuration
DOGSTATSD_HOST = '127.0.0.1'
DOGSTATSD_PORT = 8125

def send_metrics(csv_file_path):
    if not os.path.exists(csv_file_path):
        print(f"Error: File {csv_file_path} not found.")
        sys.exit(1)

    # Open UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Extract fields based on the exact headers in sample.csv
                cluster = row.get('Cluster Name', '').strip()
                namespace = row.get('Namespace Name', '').strip()
                cert = row.get('Certificate Name', '').strip()
                expiry_date = row.get('Expiry Date', '').strip()
                
                # Format expiry date for tagging (replace spaces and colons to prevent DogStatsD parsing errors)
                safe_expiry = expiry_date.replace(" ", "_").replace(":", "-")
                
                try:
                    days_due = int(row.get('Days Due', 0))
                except ValueError:
                    print(f"Skipping row due to invalid 'Days Due' value: {row.get('Days Due')}")
                    continue
                
                # Format metric line with custom tags
                # Metric type 'g' represents a Gauge
                metric_line = (
                    f"kubernetes.certificate.days_due:{days_due}|g|"
                    f"#cluster:{cluster},namespace:{namespace},certificate:{cert},expiry_date:{safe_expiry}"
                )
                
                sock.sendto(metric_line.encode('utf-8'), (DOGSTATSD_HOST, DOGSTATSD_PORT))
                print(f"Sent: {metric_line}")

    except Exception as e:
        print(f"Failed to send metrics: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    # Assumes sample.csv is in the same directory as the script
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample.csv')
    send_metrics(csv_path)
