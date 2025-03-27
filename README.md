# Energy Data Collector

![Screenshot 2025-03-27 at 13 50 24](https://github.com/user-attachments/assets/e0ffce32-2bdf-4343-adf8-afa75ccd7bb1)

## 🌍 Project Overview

The Energy Data Collector is a sophisticated Python script designed to aggregate and analyze energy consumption, carbon emissions, and electricity pricing data. This tool provides comprehensive insights into manufacturing energy usage, helping organizations and researchers understand their environmental and economic energy footprint.

## ✨ Key Features

- **Multi-Source Data Integration**
  - Fetches actual total load data from ENTSO-E API
  - Retrieves CO2 intensity from Electricity Maps API
  - Captures electricity pricing information

- **Comprehensive Energy Analysis**
  - Calculates energy consumption in kWh
  - Estimates carbon emissions (CO2 equivalent)
  - Computes energy costs

- **Flexible Data Collection**
  - Configurable data collection period (default: 7 days)
  - Stores data in InfluxDB for easy visualization and analysis

## 🔧 Technology Stack

- Python 3.8+
- InfluxDB
- Requests library
- python-dotenv
- ElementTree XML parsing

## 🚀 Installation

1. Clone the repository:


2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root with the following:
   ```
   ENTSOE_API_KEY=your_entsoe_api_key
   ELECTRICITYMAPS_API_KEY=your_electricitymaps_api_key
   ```

## 🔍 Use Cases

- **Manufacturing Energy Monitoring**
  - Track daily energy consumption
  - Analyze carbon footprint
  - Understand energy cost dynamics

- **Sustainability Reporting**
  - Generate detailed energy usage reports
  - Calculate carbon emissions
  - Support ESG (Environmental, Social, Governance) initiatives

- **Research and Analysis**
  - Collect historical energy data
  - Perform trend analysis
  - Support academic and industrial research

## 📊 Data Collection Process

1. Retrieve total load data from ENTSO-E
2. Fetch current CO2 intensity
3. Get electricity pricing information
4. Apply manufacturing energy factor
5. Calculate energy consumption, emissions, and costs
6. Store data points in InfluxDB

## ⚙️ Configuration

- **Customizable Parameters**
  - `days_to_collect`: Number of past days to collect data (default: 7)
  - `interval_minutes`: Data collection interval (placeholder in current version)

## 🛠 Logging

The script uses Python's logging module to provide detailed information about:
- API requests
- Data retrieval status
- Error handling
- Database interactions

## 🚧 Current Limitations

- EPEX SPOT prices method is a placeholder
- Requires active API keys for ENTSO-E and Electricity Maps
- Current implementation focuses on German energy market

## 🔮 Future Improvements

- Support multiple country zones
- Implement more robust price data retrieval
- Add more comprehensive error handling
- Create visualization tools
- Develop machine learning models for energy prediction

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
