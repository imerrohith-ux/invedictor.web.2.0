import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

def predict_demand(sales_data: list, current_stock: int, safety_stock: int):
    """
    Predicts monthly demand based on historical sales data.
    
    Args:
        sales_data: List of dicts [{'date': 'YYYY-MM-DD', 'quantity': int}, ...]
        current_stock: Current inventory level
        safety_stock: Desired safety stock level
        
    Returns:
        dict: Prediction results
    """
    if not sales_data:
        return {
            "predicted_monthly_demand": 0,
            "average_daily_sales": 0,
            "trend": "insufficient_data",
            "reorder_quantity": 0,
            "risk_level": "unknown",
            "forecast_graph": []
        }

    df = pd.DataFrame(sales_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Fill missing dates with 0 sales for accurate daily average
    full_range = pd.date_range(start=df['date'].min(), end=df['date'].max())
    df = df.set_index('date').reindex(full_range, fill_value=0).reset_index()
    df.rename(columns={'index': 'date', 'quantity': 'quantity'}, inplace=True)

    # 1. Average Daily Sales (Last 30 days served as baseline, but we take all available for robust avg)
    # Give more weight to recent data? For simplicity, we stick to simple average for now
    # or last 3 months average.
    avg_daily_sales = df['quantity'].mean()
    
    # 2. Trend Analysis (Linear Regression)
    # X = days since start, Y = quantity
    df['days_ordinal'] = (df['date'] - df['date'].min()).dt.days
    
    X = df[['days_ordinal']]
    y = df['quantity']
    
    model = LinearRegression()
    model.fit(X, y)
    
    trend_slope = model.coef_[0]
    
    if trend_slope > 0.1:
        trend_type = "increasing"
    elif trend_slope < -0.1:
        trend_type = "decreasing"
    else:
        trend_type = "stable"

    # 3. Predict Next Month (30 days)
    # We project the regression line for the next 30 days
    last_day = df['days_ordinal'].max()
    next_30_days = np.array([[last_day + i] for i in range(1, 31)])
    predicted_sales = model.predict(next_30_days)
    
    # Ensure no negative predictions
    predicted_sales = np.maximum(predicted_sales, 0)
    
    predicted_monthly_demand = int(np.sum(predicted_sales))
    
    # If regression is too wild (e.g. negative total), fallback to average
    if predicted_monthly_demand <= 0:
        predicted_monthly_demand = int(avg_daily_sales * 30)

    # 4. Inventory Calculation
    reorder_qty = max(0, (predicted_monthly_demand + safety_stock) - current_stock)
    
    # 5. Risk Level
    days_cover = current_stock / avg_daily_sales if avg_daily_sales > 0 else 999
    if days_cover < 7:
        risk_level = "critical"
    elif days_cover < 15:
        risk_level = "low_stock"
    elif days_cover > 60:
        risk_level = "overstock"
    else:
        risk_level = "safe"

    return {
        "predicted_monthly_demand": predicted_monthly_demand,
        "average_daily_sales": round(avg_daily_sales, 2),
        "trend": trend_type,
        "reorder_quantity": reorder_qty,
        "risk_level": risk_level,
        "forecast_graph": predicted_sales.tolist() # Send back for visualization if needed
    }
