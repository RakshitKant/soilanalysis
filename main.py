from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3
import joblib
import pandas as pd
import logging
from datetime import datetime
from contextlib import closing
from typing import Optional

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("soilsense")

# --------------------------------------------------
# App
# --------------------------------------------------
app = FastAPI(
    title="SoilSense API",
    version="1.0.0",
    description="AI-powered Soil Fertility Prediction API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Config
# --------------------------------------------------
DB_NAME = "predictions.db"
MODEL_PATH = "soil_model.pkl"

# --------------------------------------------------
# Load Model
# --------------------------------------------------
try:
    saved = joblib.load(MODEL_PATH)

    if isinstance(saved, dict):
        model = saved["model"]
        MODEL_ACCURACY = round(saved.get("accuracy", 0) * 100, 2)
    else:
        model = saved
        MODEL_ACCURACY = None

    MODEL_NAME = type(model).__name__
    logger.info(f"Loaded {MODEL_NAME}")

except Exception as e:
    logger.exception("Model loading failed")
    raise RuntimeError(f"Unable to load model: {e}")

# --------------------------------------------------
# Database
# --------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_connection()) as conn:

        conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            ph REAL,
            ec REAL,
            organic_carbon REAL,
            sulfur REAL,
            zinc REAL,
            iron REAL,
            copper REAL,
            manganese REAL,
            boron REAL,
            fertility TEXT,
            confidence REAL,
            timestamp TEXT
        )
        """)

        conn.commit()


init_db()

# --------------------------------------------------
# Request Model
# --------------------------------------------------
class AnalyzeRequest(BaseModel):

    N: float = Field(..., ge=0)
    P: float = Field(..., ge=0)
    K: float = Field(..., ge=0)

    pH: float = Field(..., ge=0, le=14)

    EC: float
    OC: float
    S: float
    Zn: float
    Fe: float
    Cu: float
    Mn: float
    B: float

# --------------------------------------------------
# Helpers
# --------------------------------------------------
FEATURE_COLUMNS = [
    "N",
    "P",
    "K",
    "pH",
    "EC",
    "OC",
    "S",
    "Zn",
    "Fe",
    "Cu",
    "Mn",
    "B"
]

RECOMMENDATIONS = {
    "Low":
        "Increase organic matter and apply balanced fertilizers.",

    "Medium":
        "Maintain nutrient balance and monitor irrigation.",

    "High":
        "Soil is healthy. Continue current farming practices."
}


def fertility_name(pred: int):

    mapping = {
        0: "Low",
        1: "Medium",
        2: "High"
    }

    return mapping.get(pred, "Unknown")

# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.get("/")
def root():

    return {
        "status": "online",
        "service": "SoilSense AI",
        "model": MODEL_NAME,
        "accuracy":
            f"{MODEL_ACCURACY}%"
            if MODEL_ACCURACY
            else "Unknown",
        "version": app.version
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "database": "connected",
        "model_loaded": True
    }


@app.get("/api/dashboard")
def dashboard():

    with closing(get_connection()) as conn:

        total = conn.execute(
            "SELECT COUNT(*) FROM predictions"
        ).fetchone()[0]

    return {
        "status": "online",
        "predictions": total,
        "model": MODEL_NAME,
        "accuracy":
            f"{MODEL_ACCURACY}%"
            if MODEL_ACCURACY
            else "Unknown"
    }


@app.post("/api/analyze")
def analyze(data: AnalyzeRequest):

    try:

        values = [[
            data.N,
            data.P,
            data.K,
            data.pH,
            data.EC,
            data.OC,
            data.S,
            data.Zn,
            data.Fe,
            data.Cu,
            data.Mn,
            data.B
        ]]

        df = pd.DataFrame(
            values,
            columns=FEATURE_COLUMNS
        )

        prediction = int(model.predict(df)[0])

        confidence: Optional[float]

        try:

            probs = model.predict_proba(df)[0]

            confidence = round(
                float(max(probs)) * 100,
                2
            )

        except Exception:

            confidence = None

        fertility = fertility_name(prediction)

        with closing(get_connection()) as conn:

            conn.execute("""
            INSERT INTO predictions(
                nitrogen,
                phosphorus,
                potassium,
                ph,
                ec,
                organic_carbon,
                sulfur,
                zinc,
                iron,
                copper,
                manganese,
                boron,
                fertility,
                confidence,
                timestamp
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                data.N,
                data.P,
                data.K,
                data.pH,
                data.EC,
                data.OC,
                data.S,
                data.Zn,
                data.Fe,
                data.Cu,
                data.Mn,
                data.B,
                fertility,
                confidence,
                datetime.utcnow().isoformat()
            ))

            conn.commit()

        logger.info(
            f"Prediction -> {fertility}"
        )

        return {
            "success": True,
            "prediction": {
                "fertility": fertility,
                "confidence": confidence
            },
            "recommendation":
                RECOMMENDATIONS.get(
                    fertility,
                    "No recommendation available."
                ),
            "model": MODEL_NAME,
            "timestamp":
                datetime.utcnow().isoformat()
        }

    except Exception as e:

        logger.exception(e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/api/history")
def history(limit: int = 20):

    with closing(get_connection()) as conn:

        rows = conn.execute("""
        SELECT
            id,
            fertility,
            confidence,
            timestamp
        FROM predictions
        ORDER BY id DESC
        LIMIT ?
        """, (limit,)).fetchall()

    return [
        dict(row)
        for row in rows
    ]
# --------------------------------------------------
# Future Analytics Endpoints
# --------------------------------------------------

@app.get("/api/stats")
def stats():

    with closing(get_connection()) as conn:

        total = conn.execute(
            "SELECT COUNT(*) FROM predictions"
        ).fetchone()[0]

        low = conn.execute(
            "SELECT COUNT(*) FROM predictions WHERE fertility='Low'"
        ).fetchone()[0]

        medium = conn.execute(
            "SELECT COUNT(*) FROM predictions WHERE fertility='Medium'"
        ).fetchone()[0]

        high = conn.execute(
            "SELECT COUNT(*) FROM predictions WHERE fertility='High'"
        ).fetchone()[0]

        avg_conf = conn.execute(
            """
            SELECT AVG(confidence)
            FROM predictions
            """
        ).fetchone()[0]

    return {
        "total_predictions": total,
        "low": low,
        "medium": medium,
        "high": high,
        "average_confidence": round(avg_conf or 0, 2)
    }


@app.delete("/api/history")
def clear_history():

    with closing(get_connection()) as conn:

        conn.execute(
            "DELETE FROM predictions"
        )

        conn.commit()

    logger.warning("Prediction history cleared")

    return {
        "success": True,
        "message": "History deleted successfully"
    }


@app.get("/api/history/{prediction_id}")
def history_item(prediction_id: int):

    with closing(get_connection()) as conn:

        row = conn.execute(
            """
            SELECT *
            FROM predictions
            WHERE id=?
            """,
            (prediction_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Prediction not found"
        )

    return dict(row)


# --------------------------------------------------
# Utility Functions
# --------------------------------------------------

def model_information():

    return {
        "model_name": MODEL_NAME,
        "accuracy": MODEL_ACCURACY,
        "features": FEATURE_COLUMNS,
        "classes": [
            "Low",
            "Medium",
            "High"
        ]
    }


@app.get("/api/model")
def model_details():

    return {
        "success": True,
        "model": model_information()
    }


# --------------------------------------------------
# Startup Event
# --------------------------------------------------

@app.on_event("startup")
def startup():

    logger.info("=" * 50)
    logger.info(" SoilSense API Started ")
    logger.info("=" * 50)

    logger.info(
        f"Model : {MODEL_NAME}"
    )

    logger.info(
        f"Accuracy : {MODEL_ACCURACY}"
    )

    logger.info(
        "Database initialized"
    )


# --------------------------------------------------
# Shutdown Event
# --------------------------------------------------

@app.on_event("shutdown")
def shutdown():

    logger.info(
        "Stopping SoilSense API"
    )


# --------------------------------------------------
# Exception Handler
# --------------------------------------------------

from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc)
        }
    )


# --------------------------------------------------
# Version Endpoint
# --------------------------------------------------

@app.get("/api/version")
def version():

    return {
        "api": app.version,
        "model": MODEL_NAME,
        "accuracy": MODEL_ACCURACY
    }


# --------------------------------------------------
# Root Metadata
# --------------------------------------------------

@app.get("/api")
def api():

    return {
        "name": "SoilSense AI",
        "documentation": "/docs",
        "health": "/health",
        "dashboard": "/api/dashboard",
        "prediction": "/api/analyze",
        "history": "/api/history",
        "stats": "/api/stats"
    }


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )