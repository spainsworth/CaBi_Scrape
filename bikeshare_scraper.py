import requests
import csv
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

# GBFS endpoints
STATION_STATUS_URL = 'https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/station_status.json'
FREE_BIKE_STATUS_URL = 'https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/free_bike_status.json'

# Output CSV paths
STATION_CSV = 'station_status_log.csv'
FREE_BIKE_CSV = 'free_bikes_log.csv'

# CSV headers
STATION_HEADERS = [
    'station_id',
    'timestamp',  # YYYY/MM/DD HH:MM in EST
    'ebikes_available',
    'classic_bikes_available',
    'docks_available'
]
FREE_BIKE_HEADERS = [
    'bike_id',
    'timestamp',  # YYYY/MM/DD HH:MM in EST
    'lat',
    'lon'
]

def fetch_station_status(timestamp):
    resp = requests.get(STATION_STATUS_URL)
    resp.raise_for_status()
    stations = resp.json().get('data', {}).get('stations', [])
    return [{
        'station_id': s.get('station_id'),
        'timestamp': timestamp,
        'ebikes_available': s.get('num_ebikes_available', 0),
        'classic_bikes_available': s.get('num_bikes_available', 0) - s.get('num_ebikes_available', 0),
        'docks_available': s.get('num_docks_available', 0)
    } for s in stations]


def fetch_free_bike_status(timestamp):
    resp = requests.get(FREE_BIKE_STATUS_URL)
    resp.raise_for_status()
    bikes = resp.json().get('data', {}).get('bikes', [])
    return [{
        'bike_id': b.get('bike_id'),
        'timestamp': timestamp,
        'lat': b.get('lat'),
        'lon': b.get('lon')
    } for b in bikes]


def append_to_csv(records, headers, path):
    file_exists = os.path.isfile(path)
    with open(path, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerows(records)


def main():
    est = ZoneInfo("America/New_York")
    now = datetime.now(est).strftime('%Y/%m/%d %H:%M')

    station_records = fetch_station_status(now)
    append_to_csv(station_records, STATION_HEADERS, STATION_CSV)

    bike_records = fetch_free_bike_status(now)
    append_to_csv(bike_records, FREE_BIKE_HEADERS, FREE_BIKE_CSV)


def timed_run():
    """
    Runs main() and prints execution time in seconds.
    """
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    elapsed = end - start
    print(f"Script execution time: {elapsed:.2f} seconds")


if __name__ == '__main__':
    timed_run()

# ========================================================================
# To measure runtime:
# Run locally with `python bikeshare_scraper.py` and watch the printed execution time.
# You can also pipe through the UNIX `time` command:
#   time python bikeshare_scraper.py
# ========================================================================
