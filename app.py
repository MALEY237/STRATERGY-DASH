from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import os
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

app = Flask(__name__)

# Database connection parameters
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:MODELING@localhost:5432/RetailerAnalyticsDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define models
class RetailAnalytics(db.Model):
    __tablename__ = 'retail_analytics'
    id = db.Column(db.Integer, primary_key=True)
    Retailer = db.Column(db.String)
    Retailer_ID = db.Column('Retailer ID', db.Integer)
    Date = db.Column(db.String)
    Month = db.Column(db.Integer)
    Region = db.Column(db.String)
    State = db.Column(db.String)
    Beverage_Brand = db.Column('Beverage Brand', db.String)
    Category = db.Column(db.String)
    Price_per_Unit = db.Column('Price per Unit', db.Float)
    Units_Sold = db.Column('Units Sold', db.Integer)
    Sugar_No_sugar = db.Column('Sugar/No sugar', db.String)
    WEATHER_C = db.Column('WEATHER°C', db.Float)
    Revenue = db.Column(db.Float)
    Profit = db.Column(db.Float)

# Load data from both CSV and database
def load_data():
    # Load from PostgreSQL first (preferred source)
    try:
        # Query data from PostgreSQL using Flask-SQLAlchemy
        with app.app_context():
            # Get all records as a dataframe
            query = db.session.query(RetailAnalytics).statement
            db_df = pd.read_sql(query, db.engine)
            
            print("Data loaded from PostgreSQL database")
            return db_df
    
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("Falling back to CSV data only")
        
        # Load from CSV as fallback
        csv_df = pd.read_csv('RetailAnalytics.csv', sep=';')
        
        # Clean price column - remove $ and convert to float
        csv_df['Price per Unit'] = csv_df['Price per Unit'].str.replace('$', '').str.strip().astype(float)
        
        # Calculate revenue
        csv_df['Revenue'] = csv_df['Price per Unit'] * csv_df['Units Sold']
        
        # Assume profit margin of 30%
        csv_df['Profit'] = csv_df['Revenue'] * 0.3
        
        return csv_df

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/operational')
def operational():
    return render_template('operational.html')

# API endpoints
@app.route('/api/kpi_data')
def kpi_data():
    df = load_data()
    
    # Get region filter if provided
    region = request.args.get('region', None)
    
    # Apply region filter if provided
    if region and region != 'all':
        df = df[df['Region'] == region]
    
    # Calculate KPIs
    total_revenue = df['Revenue'].sum()
    total_profit = df['Profit'].sum()
    total_units = df['Units Sold'].sum()
    regions_count = 1 if region and region != 'all' else df['Region'].nunique()
    
    return jsonify({
        'total_revenue': round(total_revenue, 2),
        'total_profit': round(total_profit, 2),
        'total_units': round(total_units, 2),
        'regions_count': regions_count
    })

@app.route('/api/revenue_by_region')
def revenue_by_region():
    df = load_data()
    
    # Get region filter if provided
    region = request.args.get('region', None)
    
    # Apply region filter if provided
    if region and region != 'all':
        df = df[df['Region'] == region]
    
    # Revenue by region
    region_revenue = df.groupby('Region')['Revenue'].sum().reset_index()
    region_revenue = region_revenue.sort_values('Revenue', ascending=False)
    
    return jsonify({
        'regions': region_revenue['Region'].tolist(),
        'revenue': region_revenue['Revenue'].tolist()
    })

@app.route('/api/revenue_by_category')
def revenue_by_category():
    df = load_data()
    
    # Get region filter if provided
    region = request.args.get('region', None)
    
    # Apply region filter if provided
    if region and region != 'all':
        df = df[df['Region'] == region]
    
    # Revenue by category
    category_revenue = df.groupby('Category')['Revenue'].sum().reset_index()
    category_revenue = category_revenue.sort_values('Revenue', ascending=False)
    
    return jsonify({
        'categories': category_revenue['Category'].tolist(),
        'revenue': category_revenue['Revenue'].tolist()
    })

@app.route('/api/revenue_over_time')
def revenue_over_time():
    df = load_data()
    
    # Get region filter if provided
    region = request.args.get('region', None)
    
    # Apply region filter if provided
    if region and region != 'all':
        df = df[df['Region'] == region]
    
    # Convert date to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    
    # Group by month
    monthly_data = df.groupby(pd.Grouper(key='Date', freq='M')).agg({
        'Revenue': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    return jsonify({
        'dates': monthly_data['Date'].dt.strftime('%b %Y').tolist(),
        'revenue': monthly_data['Revenue'].tolist(),
        'profit': monthly_data['Profit'].tolist()
    })

@app.route('/api/revenue_by_state')
def revenue_by_state():
    df = load_data()
    
    # Revenue by state
    state_revenue = df.groupby(['Region', 'State'])['Revenue'].sum().reset_index()
    
    # Create a dictionary with regions and their states
    region_data = {}
    for region in df['Region'].unique():
        region_states = state_revenue[state_revenue['Region'] == region]
        region_data[region] = {
            'states': region_states['State'].tolist(),
            'revenue': region_states['Revenue'].tolist()
        }
    
    return jsonify(region_data)

@app.route('/api/state_growth_data')
def state_growth_data():
    df = load_data()
    
    # Get region filter if provided
    region = request.args.get('region', None)
    
    # Convert date to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    
    # Find the last quarter
    max_date = df['Date'].max()
    last_quarter_start = max_date - pd.DateOffset(months=3)
    
    # Previous quarter
    prev_quarter_start = last_quarter_start - pd.DateOffset(months=3)
    
    # Filter for last and previous quarter
    last_quarter = df[(df['Date'] >= last_quarter_start) & (df['Date'] <= max_date)]
    prev_quarter = df[(df['Date'] >= prev_quarter_start) & (df['Date'] < last_quarter_start)]
    
    # Apply region filter if provided
    if region and region != 'all':
        last_quarter = last_quarter[last_quarter['Region'] == region]
        prev_quarter = prev_quarter[prev_quarter['Region'] == region]
    
    # Group by state for each quarter
    last_q_state_revenue = last_quarter.groupby(['Region', 'State'])['Revenue'].sum().reset_index()
    prev_q_state_revenue = prev_quarter.groupby(['Region', 'State'])['Revenue'].sum().reset_index()
    
    # Merge data
    state_data = pd.merge(last_q_state_revenue, prev_q_state_revenue, 
                          on=['Region', 'State'], how='outer', 
                          suffixes=('_last', '_prev'))
    
    # Fill NaN values with 0
    state_data['Revenue_prev'] = state_data['Revenue_prev'].fillna(0)
    state_data['Revenue_last'] = state_data['Revenue_last'].fillna(0)
    
    # Calculate growth percentage
    state_data['Growth'] = ((state_data['Revenue_last'] - state_data['Revenue_prev']) / 
                            state_data['Revenue_prev'].replace(0, 1)) * 100
    
    # Group by region
    result = {}
    for r in state_data['Region'].unique():
        # If region filter is provided, only include matching region
        if region and region != 'all' and r != region:
            continue
        
        region_data = state_data[state_data['Region'] == r]
        result[r] = {
            'states': region_data['State'].tolist(),
            'revenue': region_data['Revenue_last'].tolist(),
            'growth': region_data['Growth'].tolist()
        }
    
    return jsonify(result)

@app.route('/api/growth_by_category')
def growth_by_category():
    df = load_data()
    
    # Get region filter if provided
    region = request.args.get('region', None)
    
    # Apply region filter if provided
    if region and region != 'all':
        df = df[df['Region'] == region]
    
    # Convert date to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    
    # Find the last quarter
    max_date = df['Date'].max()
    last_quarter_start = max_date - pd.DateOffset(months=3)
    
    # Previous quarter
    prev_quarter_start = last_quarter_start - pd.DateOffset(months=3)
    
    # Filter for last and previous quarter
    last_quarter = df[(df['Date'] >= last_quarter_start) & (df['Date'] <= max_date)]
    prev_quarter = df[(df['Date'] >= prev_quarter_start) & (df['Date'] < last_quarter_start)]
    
    # Group by category
    last_q_revenue = last_quarter.groupby('Category')['Revenue'].sum()
    prev_q_revenue = prev_quarter.groupby('Category')['Revenue'].sum()
    
    # Calculate growth
    growth = ((last_q_revenue - prev_q_revenue) / prev_q_revenue) * 100
    
    # Sort by growth and get top 3
    top_growth = growth.sort_values(ascending=False).head(3)
    
    return jsonify({
        'categories': top_growth.index.tolist(),
        'growth': top_growth.values.tolist()
    })

@app.route('/api/outperforming_regions')
def outperforming_regions():
    df = load_data()
    
    # Get region filter if provided
    region = request.args.get('region', None)
    
    # Convert date to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    
    # Find the last quarter
    max_date = df['Date'].max()
    last_quarter_start = max_date - pd.DateOffset(months=3)
    
    # Filter for last quarter
    last_quarter = df[(df['Date'] >= last_quarter_start) & (df['Date'] <= max_date)]
    
    # Apply region filter if provided
    if region and region != 'all':
        last_quarter = last_quarter[last_quarter['Region'] == region]
    
    # Group by region and calculate growth
    region_growth = last_quarter.groupby('Region')['Revenue'].sum()
    
    # Calculate average growth
    avg_growth = region_growth.mean()
    
    # Get regions outperforming average
    outperforming = region_growth[region_growth > avg_growth]
    
    return jsonify({
        'regions': outperforming.index.tolist(),
        'revenue': outperforming.values.tolist()
    })

@app.route('/api/retailer_performance')
def retailer_performance():
    df = load_data()
    
    # Group by retailer
    retailer_data = df.groupby('Retailer').agg({
        'Revenue': 'sum',
        'Units Sold': 'sum'
    }).reset_index()
    
    # Sort by revenue
    retailer_data = retailer_data.sort_values('Revenue', ascending=False)
    
    return jsonify({
        'retailers': retailer_data['Retailer'].tolist(),
        'revenue': retailer_data['Revenue'].tolist(),
        'units': retailer_data['Units Sold'].tolist()
    })

@app.route('/api/product_performance')
def product_performance():
    df = load_data()
    
    # Group by beverage brand
    brand_data = df.groupby('Beverage Brand').agg({
        'Revenue': 'sum',
        'Units Sold': 'sum'
    }).reset_index()
    
    # Sort by revenue
    brand_data = brand_data.sort_values('Revenue', ascending=False)
    
    return jsonify({
        'brands': brand_data['Beverage Brand'].tolist(),
        'revenue': brand_data['Revenue'].tolist(),
        'units': brand_data['Units Sold'].tolist()
    })

@app.route('/api/sugar_vs_nosugar')
def sugar_vs_nosugar():
    df = load_data()
    
    # Group by sugar type
    sugar_data = df.groupby('Sugar/No sugar').agg({
        'Revenue': 'sum',
        'Units Sold': 'sum'
    }).reset_index()
    
    return jsonify({
        'categories': sugar_data['Sugar/No sugar'].tolist(),
        'revenue': sugar_data['Revenue'].tolist(),
        'units': sugar_data['Units Sold'].tolist()
    })

@app.route('/api/weather_impact')
def weather_impact():
    df = load_data()
    
    # Create temperature brackets
    df['Temp Bracket'] = pd.cut(df['WEATHER°C'], 
                                bins=[0, 10, 20, 30, 40], 
                                labels=['Cold (0-10°C)', 'Cool (10-20°C)', 
                                        'Warm (20-30°C)', 'Hot (30-40°C)'])
    
    # Group by temperature bracket
    temp_data = df.groupby('Temp Bracket').agg({
        'Revenue': 'sum',
        'Units Sold': 'sum'
    }).reset_index()
    
    return jsonify({
        'temp_brackets': temp_data['Temp Bracket'].tolist(),
        'revenue': temp_data['Revenue'].tolist(),
        'units': temp_data['Units Sold'].tolist()
    })

@app.route('/api/db_status')
def db_status():
    """Check database connection status and return info about data sources"""
    try:
        # Check connection and get row count
        with app.app_context():
            db_count = db.session.query(RetailAnalytics).count()
            
            # Get table columns
            db_columns = [column.name for column in RetailAnalytics.__table__.columns]
            
            # Get some sample data (first 3 rows)
            sample_data = db.session.query(RetailAnalytics).limit(3).all()
            sample_regions = [row.Region for row in sample_data]
        
        # Get CSV info
        csv_df = pd.read_csv('RetailAnalytics.csv', sep=';')
        csv_count = len(csv_df)
        
        return jsonify({
            'status': 'connected',
            'database': {
                'name': 'RetailerAnalyticsDB',
                'table': 'retail_analytics',
                'rows': db_count,
                'columns': db_columns,
                'sample_regions': sample_regions
            },
            'csv': {
                'file': 'RetailAnalytics.csv',
                'rows': csv_count,
                'columns': list(csv_df.columns)
            },
            'source': 'Using database as primary data source'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'csv': {
                'file': 'RetailAnalytics.csv',
                'rows': len(pd.read_csv('RetailAnalytics.csv', sep=';')),
                'columns': list(pd.read_csv('RetailAnalytics.csv', sep=';').columns)
            },
            'source': 'Using CSV as fallback data source'
        })

if __name__ == '__main__':
    app.run(debug=True) 