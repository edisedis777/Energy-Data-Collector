import os
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from influxdb import InfluxDBClient
from typing import List, Dict, Any


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class EnergyDataCollector:
    def __init__(self):
        # API Keys
        self.ENTSOE_API_KEY = os.getenv("ENTSOE_API_KEY")
        self.ELECTRICITYMAPS_API_KEY = os.getenv("ELECTRICITYMAPS_API_KEY")

        # InfluxDB Client
        try:
            self.influx_client = InfluxDBClient(
                host="localhost",
                port=8086,
                database="energy_data"
            )
            self.influx_client.ping()
            logger.info("Connected to InfluxDB successfully")
        except Exception as e:
            logger.error(f"InfluxDB Connection failed: {e}")
            raise

    def get_entsoe_load(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """
        Fetch actual total load data from ENTSO-E API

        Args:
            start (datetime): Start time for data retrieval
            end (datetime): End time for data retrieval

        Returns:
            List of dictionaries containing load data
        """
        url = "https://web-api.tp.entsoe.eu/api"

        # Prepare parameters with precise ENTSO-E datetime format
        params = {
            "securityToken": self.ENTSOE_API_KEY,
            "documentType": "A65",  # Actual total load
            "processType": "A16",  # Realised
            "in_Domain": "10Y1001A1001A83F",  # Germany
            "OutBiddingZone_Domain": "10Y1001A1001A83F",  # Germany (same as in_Domain)
            "periodStart": start.strftime("%Y%m%d%H%M"),
            "periodEnd": end.strftime("%Y%m%d%H%M"),
        }

        logger.info(f"Making ENTSO-E request with params: {params}")
        try:
            response = requests.get(url, params=params)
            logger.info(f"Response status: {response.status_code}")

            # Log the full URL for debugging
            logger.info(f"Request URL: {response.url}")

            response.raise_for_status()  # Raise an exception for bad status codes

            # Parse XML response
            root = ET.fromstring(response.content)

            namespace = {
                'ns': 'urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'
            }

            load_points = []
            for timeseries in root.findall('.//ns:TimeSeries', namespace):
                period = timeseries.find('.//ns:Period', namespace)
                if period is not None:
                    start_date_str = period.find('.//ns:timeInterval/ns:start', namespace).text
                    start_date = datetime.fromisoformat(start_date_str)

                    for point in period.findall('.//ns:Point', namespace):
                        quantity = float(point.find('.//ns:quantity', namespace).text)
                        load_points.append({
                            'time': start_date.isoformat(),
                            'load_kwh': quantity
                        })

            logger.info(f"Retrieved {len(load_points)} load points")
            return load_points

        except requests.RequestException as e:
            logger.error(f"ENTSO-E API request failed: {e}")
            return []
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return []

    def get_co2_intensity(self, zone: str = "DE") -> float:
        """
        Fetch CO2 intensity from Electricity Maps API

        Args:
            zone (str): Country code for CO2 intensity

        Returns:
            float: Carbon intensity in gCO2eq/kWh
        """
        url = "https://api.electricitymap.org/v3/carbon-intensity/latest"
        headers = {"auth-token": self.ELECTRICITYMAPS_API_KEY}
        params = {"zone": zone}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("carbonIntensity", 0)
        except requests.RequestException as e:
            logger.error(f"Electricity Maps API request failed: {e}")
            return 0

    def get_epex_prices(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """
        Fetch EPEX SPOT prices (Note: This is a placeholder -
        you'll need to replace with actual API implementation)

        Args:
            start (datetime): Start time for data retrieval
            end (datetime): End time for data retrieval

        Returns:
            List of dictionaries containing price data
        """
        # Placeholder implementation
        return [{
            'time': start.isoformat(),
            'price_eur_kwh': 0.10  # Example price
        }]

    def collect_and_store_data(self, days_to_collect: int = 7, interval_minutes: int = 15):
        """
        Collect energy data for the last specified number of days

        Args:
            days_to_collect (int): Number of past days to collect data for, defaults to 7
        """
        # Calculate date range
        # Use UTC for consistent data collection
def collect_and_store_data(self, days_to_collect: int = 7):
        """
        Collect energy data for the last specified number of days

        Args:
            days_to_collect (int): Number of past days to collect data for, defaults to 7
        """
        # Calculate date range
        # Use UTC for consistent data collection
        today_utc = datetime.now(timezone.utc)
        end_utc = today_utc.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        end_utc = end_utc.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_utc = end_utc - timedelta(days=days_to_collect - 1)
        start_utc = start_utc.replace(hour=0, minute=0, second=0, microsecond=0)

        logger.info(f"Requesting data from {start_utc} to {end_utc}")

        # Fetch data
        try:
            load_data = self.get_entsoe_load(start_utc, end_utc)
            co2_intensity = self.get_co2_intensity()
            price_data = self.get_epex_prices(start_utc, end_utc)

            # Manufacturing energy factor
            manufacturing_factor = 0.23

            # Prepare InfluxDB points
            points = []
            for load in load_data:
                energy_kwh = load.get('load_kwh', 0) * manufacturing_factor
                co2eq = energy_kwh * co2_intensity

                # Match price data (simplified)
                price = price_data[0] if price_data else {'price_eur_kwh': 0}
                cost = energy_kwh * price['price_eur_kwh']

                point = {
                    "measurement": "manufacturing_energy",
                    "time": load.get('time', end_utc.isoformat()),
                    "fields": {
                        "energy_kwh": energy_kwh,
                        "co2eq_g": co2eq,
                        "cost_eur": cost,
                        "co2_intensity": co2_intensity,
                        "price_eur_kwh": price['price_eur_kwh']
                    }
                }
                points.append(point)

            # Write to InfluxDB
            if points:
                self.influx_client.write_points(points)
                logger.info(f"Successfully wrote {len(points)} data points")
            else:
                logger.warning("No data points to write")

        except Exception as e:
            logger.error(f"Data collection and storage failed: {e}")

def main():
    """
    Main entry point for the energy data collection script
    """
    try:
        collector = EnergyDataCollector()
        collector.collect_and_store_data(days_to_collect=7, interval_minutes=15) # Pass interval_minutes here
    except Exception as e:
        logger.error(f"Script execution failed: {e}")

if __name__ == "__main__":
    main()