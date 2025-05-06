from fastapi import FastAPI, HTTPException, Depends, Form, Security, Request 
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import sqlite3
import hashlib
from datetime import datetime, timedelta
import jwt
from fastapi.middleware.cors import CORSMiddleware
import logging
from starlette.responses import JSONResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

app = FastAPI(title="Loan Management API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"


def init_db():
    """Initialize the database tables if they do not exist"""
    with sqlite3.connect("loan_management.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS loans
                      (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, term INTEGER,
                       monthly_income REAL, status TEXT, balance REAL,
                       FOREIGN KEY(user_id) REFERENCES users(id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS payments
                      (id INTEGER PRIMARY KEY, loan_id INTEGER, amount REAL, date TEXT,
                      FOREIGN KEY(loan_id) REFERENCES loans(id))''')
        conn.commit()


init_db()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class UserRegister(BaseModel):
    name: str
    email: str
    password: str


class LoanApplication(BaseModel):
    amount: float
    term: int
    monthly_income: float


class Payment(BaseModel):
    amount: float


# Helper functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(email: str):
    expiration = datetime.utcnow() + timedelta(hours=2)  # Add 2 hours to the current UTC time
    token = jwt.encode({"sub": email, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_access_token(token: str):
    """Verify JWT access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_db_connection():
    try:
        conn = sqlite3.connect("loan_management.db", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        logger.info("Database connection successful")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

def get_current_user(token: str = Security(oauth2_scheme)):
    if not token:
        logger.error("Token is missing")
        raise HTTPException(status_code=401, detail="Token missing")

    logger.info(f"Received token: {token}")
    try:
        email = verify_access_token(token)
        logger.info(f"Verified email: {email}")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE email=?", (email,))
        user = c.fetchone()
        
        if not user:
            logger.error(f"User not found for email: {email}")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        return user["id"]

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled Exception: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(e)},
        )

# 🚀 *User Registration*
@app.post("/register")
async def register(user: UserRegister):
    """Register a new user"""
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                      (user.name, user.email, hash_password(user.password)))
            conn.commit()
            return {"message": "User registered successfully"}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Email already registered")


# 🚀 *Login & Authentication*
@app.post("/token")
async def login(username: str = Form(...), password: str = Form(...)):
    """Login and generate access token"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (username,))
        user = c.fetchone()

    if not user or user["password"] != hash_password(password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"access_token": create_access_token(username), "token_type": "bearer"}


# 🚀 *Apply for a Loan*
@app.post("/loans/apply")
async def apply_loan(loan: LoanApplication, user_id: int = Depends(get_current_user)):
    """Apply for a loan with validation"""
    if loan.amount > (loan.monthly_income * 5):
        raise HTTPException(status_code=400, detail="Loan amount cannot exceed 5x monthly income")
    if not (6 <= loan.term <= 36):
        raise HTTPException(status_code=400, detail="Loan term must be between 6 and 36 months")

    status = "Approved" if loan.amount <= 500 else "Pending"
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""INSERT INTO loans (user_id, amount, term, monthly_income, status, balance)
                    VALUES (?, ?, ?, ?, ?, ?)""", (user_id, loan.amount, loan.term, loan.monthly_income, status, loan.amount))
        conn.commit()
        return {"message": "Loan application submitted successfully"}


# 🚀 *Update Loan Status*
@app.put("/loans/{loan_id}/status")
async def update_loan_status(loan_id: int, status: str):
    """Update loan status to Approved or Rejected"""
    if status not in ["Approved", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE loans SET status=? WHERE id=?", (status, loan_id))
        conn.commit()

    return {"message": f"Loan {loan_id} status updated to {status}"}


# 🚀 *Get User Loan Details*
@app.get("/loans")
async def get_loan_details(user_id: int = Depends(get_current_user)):
    """Retrieve loan details for the current user"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, amount, term, status, balance FROM loans WHERE user_id=?", (user_id,))
        loans = c.fetchall()
        c.execute("SELECT name, email FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
        result = {
            "user": {"name": user[0], "email": user[1]},
            "loans": [
                {
                    "loan_id": loan[0],
                    "amount": loan[1],
                    "term": loan[2],
                    "status": loan[3],
                    "remaining_balance": loan[4],
                }
                for loan in loans
            ]
        }
        return result


# Run FastAPI application
if _name_ == "_main_":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)