# Retail Analytics Strategic Dashboard

A Flask-based dashboard for retail analytics data visualization, designed for investors and executives.

## Overview

This dashboard provides strategic insights for investors and executives, answering the question: "How is the business performing and where should we invest next?"

### Key Features

- **Two Complementary Dashboards**:
  - Strategic Dashboard for investors focused on high-level metric

- **KPI Widgets**: Total Revenue, Total Profit, Number of Regions, and Total Units Sold
- **Interactive Visualizations**: 
  - Revenue & profit growth over time
  - Revenue by region
  - Revenue share by product category
  - Geo-distribution of sales
  - Retailer performance
  - Product brand analysis
  - Weather impact on sales
- **Qualitative Insights**: Growing categories, outperforming regions, and investor highlights

## Requirements

- Python 3.8+
- Flask
- Pandas
- NumPy
- Web browser

## Installation

1. Clone this repository
2. Install the dependencies:
```
pip install -r requirements.txt
```

## Usage

1. Ensure you have the `RetailAnalytics.csv` file in the project root directory
2. Run the application:
```
python app.py
```
3. Open a web browser and navigate to: http://127.0.0.1:5000/
4. Toggle between the Strategic and Operational dashboards using the links in the header

## Data Sources

This dashboard uses the `RetailAnalytics.csv` file as its primary data source. The file contains retail sales data for various beverage products across different regions and time periods.

## Dashboard Plan

- **Strategic Dashboard**
  - **Story**: "How is the business performing and where should we invest next?"
  - **Type**: Strategic/Analytical
  - **Target Users**: Investors, Executives
  - **Key Metrics**:
    - Revenue and profit trends
    - Regional performance
    - Product category distribution
    - Growth indicators

- **Operational Dashboard**
  - **Story**: "What's happening at the product and retailer level?"
  - **Type**: Operational/Tactical
  - **Target Users**: Management, Operations Teams
  - **Key Metrics**:
    - Retailer performance
    - Product brand metrics
    - Sugar vs. No-sugar product analysis
    - Weather impact on sales

## Database Integration

The dashboard processes the CSV data for visualization, but can be adapted to connect to a PostgreSQL database as needed. The data model supports analysis of:

- Sales by region
- Performance trends over time
- Product category metrics
- Growth opportunities 