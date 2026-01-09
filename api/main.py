from fastapi import FastAPI, HTTPException
import pandas as pd
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(
    title="Library API",
    description="API for Library Books and Customers",
    version="1.0.0"
)

# Paths to CSV files in volume
BOOKS_CSV = Path("/library_data/books.csv")
CUSTOMERS_CSV = Path("/library_data/customers.csv")

# Pydantic models
class Book(BaseModel):
    id: int
    customer_id: int
    books: str
    book_checkout: Optional[str]
    book_returned: Optional[str]
    date_validity: str
    checkout_duration: Optional[float]

class Customer(BaseModel):
    customer_id: int
    customer_name: str

class HealthResponse(BaseModel):
    status: str
    books_csv: str
    customers_csv: str

@app.get("/")
def root():
    """API root"""
    return {
        "message": "Library API",
        "endpoints": {
            "GET /books": "Get all book transactions",
            "GET /customers": "Get all customers",
        }
    }

@app.get("/books")
def get_books(limit: int = 100, offset: int = 0):
    """Get all books"""
    if not BOOKS_CSV.exists():
        raise HTTPException(status_code=404, detail="books.csv not found. Run ETL first.")
    
    try:
        df = pd.read_csv(BOOKS_CSV)
        
        # Apply pagination
        paginated = df.iloc[offset:offset+limit]
        
        return {
            "total": len(df),
            "limit": limit,
            "offset": offset,
            "count": len(paginated),
            "books": paginated.to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customers")
def get_customers(limit: int = 100, offset: int = 0):
    """Get all customers"""
    if not CUSTOMERS_CSV.exists():
        raise HTTPException(status_code=404, detail="customers.csv not found. Run ETL first.")
    
    try:
        df = pd.read_csv(CUSTOMERS_CSV)
        
        df = df.replace({pd.NA: None, float('nan'): None})
        
        # Apply pagination
        paginated = df.iloc[offset:offset+limit]
        
        return {
            "total": len(df),
            "limit": limit,
            "offset": offset,
            "count": len(paginated),
            "customers": paginated.to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)