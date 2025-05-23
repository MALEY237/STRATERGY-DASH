import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os

app = Flask(__name__)

# Database connection parameters
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:MODELING@localhost:5432/RetailerAnalyticsDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define model for retail analytics table
class RetailAnalytics(db.Model):
    __tablename__ = 'retail_analytics'
    id = db.Column(db.Integer, primary_key=True)
    Date = db.Column(db.String)
    Region = db.Column(db.String)
    State = db.Column(db.String)
    City = db.Column(db.String, nullable=True)  # Make city nullable
    Category = db.Column(db.String)
    Beverage_Brand = db.Column(db.String, name="Beverage Brand")
    Retailer = db.Column(db.String)
    Price_per_Unit = db.Column(db.Float, name="Price per Unit")
    Units_Sold = db.Column(db.Integer, name="Units Sold")
    Sugar_No_sugar = db.Column(db.String, name="Sugar/No sugar")
    WEATHER_C = db.Column(db.Float, name="WEATHER°C")
    Revenue = db.Column(db.Float)
    Profit = db.Column(db.Float)

def import_csv_to_db():
    try:
        # Load CSV data
        print("Loading CSV data...")
        csv_path = 'RetailAnalytics.csv'
        if not os.path.exists(csv_path):
            print(f"Error: {csv_path} not found")
            return
        
        df = pd.read_csv(csv_path, sep=';')
        
        # Print column names for debugging
        print("CSV Columns:", df.columns.tolist())
        
        # Check for NaN values
        for col in df.columns:
            nan_count = df[col].isna().sum()
            if nan_count > 0:
                print(f"Column {col} has {nan_count} NaN values")
        
        # Handle data cleaning and transformation
        # Clean price column - remove $ and convert to float
        if 'Price per Unit' in df.columns:
            df['Price per Unit'] = df['Price per Unit'].str.replace('$', '').str.strip().astype(float)
        
        # Calculate revenue
        if 'Units Sold' in df.columns and 'Price per Unit' in df.columns:
            df['Revenue'] = df['Price per Unit'] * df['Units Sold']
        
        # Calculate profit
        if 'Revenue' in df.columns:
            df['Profit'] = df['Revenue'] * 0.3
        
        with app.app_context():
            # Create connection
            engine = db.engine
            
            # Drop table if exists using text() for SQL statements
            print("Dropping existing table if it exists...")
            with engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS retail_analytics"))
                conn.commit()
            
            # Import data to PostgreSQL
            print("Importing data to PostgreSQL...")
            
            # Use to_sql with index as the primary key
            df.to_sql('retail_analytics', 
                     engine, 
                     if_exists='replace', 
                     index=True,
                     index_label='id')
            
            # Verify data was imported
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM retail_analytics"))
                count = result.scalar()
            
            print(f"Successfully imported {count} rows to retail_analytics table")
            return True
    
    except Exception as e:
        print(f"Error during import: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import_csv_to_db() 