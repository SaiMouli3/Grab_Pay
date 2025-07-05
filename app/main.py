import uvicorn
import webbrowser
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.models.schemas import Transaction
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Depends
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.agents.router import agentic_system
from app.core.state import AgentState
from app.models.database import SessionLocal, Base, engine
from typing import Optional
import os
from pathlib import Path
import asyncio
from contextlib import asynccontextmanager

# Set up paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

# Create static directories if they don't exist
STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(exist_ok=True)
(STATIC_DIR / "js").mkdir(exist_ok=True)

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Self-Healing Agentic System",
    description="An agentic system for processing transactions with self-healing capabilities.",
    version="1.0.0"
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Database connection management
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"})

# Serve static files directly
@app.get("/static/{path:path}", response_class=FileResponse)
async def serve_static(path: str):
    return FileResponse(STATIC_DIR / path)

# Connection status endpoint
@app.get("/api/connection")
async def check_connection():
    try:
        # First try to create a new session
        db = SessionLocal()
        
        # Test the connection by executing a simple query
        try:
            result = db.execute("SELECT 1").fetchone()
            if result and result[0] == 1:
                return JSONResponse(content={"connected": True})
            else:
                return JSONResponse(content={"connected": False, "error": "Invalid query result"}, status_code=500)
        except Exception as e:
            error_msg = str(e)
            if "No such file or directory" in error_msg:
                return JSONResponse(content={"connected": False, "error": "Database file not found. Please restart the application."}, status_code=500)
            return JSONResponse(content={"connected": False, "error": error_msg}, status_code=500)
        finally:
            try:
                db.close()
            except:
                pass
    except Exception as e:
        error_msg = str(e)
        if "No such file or directory" in error_msg:
            return JSONResponse(content={"connected": False, "error": "Database file not found. Please restart the application."}, status_code=500)
        return JSONResponse(content={"connected": False, "error": error_msg}, status_code=500)

@app.post("/process_transaction/", response_model=AgentState)
async def process_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    try:
        # Create transaction record
        db_transaction = Transaction(
            capture_id=transaction.capture_id,
            request_id=transaction.request_id,
            charge_id=transaction.charge_id,
            status=transaction.status,
            amount_value=transaction.amount.value,
            amount_currency=transaction.amount.currency,
            transaction_metadata=transaction.transaction_metadata,
            is_valid=None,
            is_fraudulent=None,
            fulfillment_status=None,
            error_message=None,
            history=[]
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)

        # Process transaction through agentic system
        initial_state = AgentState(
            transaction=db_transaction,
            is_valid=None,
            is_fraudulent=None,
            fulfillment_status=None,
            error_message=None,
            history=[]
        )
        
        final_state = agentic_system.invoke(initial_state)
        
        # Update transaction record with processing results
        db_transaction.is_valid = final_state.is_valid
        db_transaction.is_fraudulent = final_state.is_fraudulent
        db_transaction.fulfillment_status = final_state.fulfillment_status
        db_transaction.error_message = final_state.error_message
        db_transaction.history = final_state.history
        db.commit()
        
        return final_state
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    db = SessionLocal()
    try:
        # Get recent transactions
        transactions = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(10).all()
        
        # Get statistics
        total_transactions = db.query(Transaction).count()
        successful_transactions = db.query(Transaction).filter(Transaction.status == "SUCCESS").count()
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "transactions": transactions,
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions
        })
    finally:
        db.close()

@app.get("/transaction/{transaction_id}")
async def get_transaction(transaction_id: int, request: Request):
    db = SessionLocal()
    try:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return templates.TemplateResponse("transaction_detail.html", {
            "request": request,
            "transaction": transaction
        })
    finally:
        db.close()

@app.get("/api/transactions")
def get_transactions(skip: int = 0, limit: int = 10):
    db = SessionLocal()
    try:
        transactions = db.query(Transaction).offset(skip).limit(limit).all()
        return transactions
    finally:
        db.close()

if __name__ == "__main__":
    # Check if database exists and create if needed
    from pathlib import Path
    db_path = Path(DATABASE_URL.replace('sqlite:///', ''))
    if not db_path.exists():
        print(f"Creating database at {db_path}")
        Base.metadata.create_all(bind=engine)
    
    # Open browser when server starts
    webbrowser.open("http://127.0.0.1:8000/")
    
    # Run the server
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
