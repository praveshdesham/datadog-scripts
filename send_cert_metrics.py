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
                cluster = row['cluster name'].strip()
                namespace = row['namespace'].strip()
                cert = row['certificate name'].strip()
                days_due = int(row['days due'].strip())
                renewal = row['method of renewal'].strip().replace(" ", "_").replace("/", "-")
                
                # Format metric line with custom tags
                # Metric type 'g' represents a Gauge
                metric_line = (
                    f"kubernetes.certificate.days_due:{days_due}|g|"
                    f"#cluster:{cluster},namespace:{namespace},certificate:{cert},method_of_renewal:{renewal}"
                )
                
                sock.sendto(metric_line.encode('utf-8'), (DOGSTATSD_HOST, DOGSTATSD_PORT))
                print(f"Sent: {metric_line}")

    except Exception as e:
        print(f"Failed to send metrics: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    # Specify full path to sample.csv if needed
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample.csv')
    send_metrics(csv_path)
