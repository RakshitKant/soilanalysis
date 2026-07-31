# 🌱 SoilSense AI

An AI-powered soil fertility prediction system built using **Machine Learning**, **FastAPI**, and a responsive web interface. The application predicts soil fertility from laboratory soil parameters, stores prediction history, and provides recommendations to improve soil health.

---

## Features

* Machine Learning based soil fertility prediction
* FastAPI REST API
* Responsive frontend using HTML, CSS, and JavaScript
* SQLite database for storing prediction history
* Dashboard with prediction statistics
* Prediction confidence score
* Soil health recommendations
* API health monitoring
* Automatic prediction history management

---

## Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* FastAPI
* Uvicorn
* Pandas
* Scikit-learn
* Joblib
* SQLite
* Pydantic

---

## Project Structure

```text
soilanalysis/
│
├── main.py               # FastAPI backend
├── index.html            # Frontend
├── soil_model.pkl        # Trained ML model
├── predictions.db        # SQLite database (auto-generated)
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/RakshitKant/soilanalysis.git

cd soilanalysis
```

### 2. Create a Virtual Environment (Recommended)

#### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Backend

```bash
python main.py
```

or

```bash
uvicorn main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

Interactive API documentation:

```
http://localhost:8000/docs
```

### 5. Launch the Frontend

Simply open:

```
index.html
```

in your preferred web browser.

If your backend is deployed, update the following line inside `index.html`:

```javascript
const API = "http://localhost:8000";
```

Replace it with your deployed backend URL.

---

## Sample Input

| Parameter      | Value |
| -------------- | ----: |
| Nitrogen (N)   |    58 |
| Phosphorus (P) |    30 |
| Potassium (K)  |    35 |
| pH             |   7.1 |
| EC             |  0.61 |
| Organic Carbon |  0.72 |
| Sulfur         |    11 |
| Zinc           |  0.88 |
| Iron           |   4.3 |
| Copper         |  0.55 |
| Manganese      |   2.8 |
| Boron          |  0.46 |

---

## API Endpoints

| Method | Endpoint         | Description               |
| ------ | ---------------- | ------------------------- |
| GET    | `/`              | API status                |
| GET    | `/health`        | Health check              |
| POST   | `/api/analyze`   | Predict soil fertility    |
| GET    | `/api/dashboard` | Dashboard information     |
| GET    | `/api/history`   | Prediction history        |
| DELETE | `/api/history`   | Delete prediction history |
| GET    | `/api/stats`     | Prediction statistics     |
| GET    | `/api/model`     | Model details             |
| GET    | `/docs`          | Swagger documentation     |

---

## Example Response

```json
{
  "success": true,
  "prediction": {
    "fertility": "High",
    "confidence": 96.72
  },
  "recommendation": "Soil is healthy. Continue current farming practices.",
  "model": "RandomForestClassifier"
}
```

---

## How It Works

1. Enter soil nutrient values through the web interface.
2. Submit the sample.
3. The frontend sends the data to the FastAPI backend.
4. The trained machine learning model predicts the soil fertility.
5. The prediction is stored in the SQLite database.
6. The dashboard and history are updated automatically.

---

## Future Improvements

* Crop recommendation system
* Fertilizer recommendation engine
* Weather data integration
* Satellite imagery analysis
* GIS-based soil mapping
* Multi-language support
* User authentication
* Cloud deployment
* Mobile application

---

## Author

**Rakshit**

GitHub: https://github.com/RakshitKant

---

## License

This project is licensed under the MIT License.

---

If you found this project useful, consider giving it a ⭐ on GitHub.
