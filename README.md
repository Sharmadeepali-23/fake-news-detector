# 🛡️ VeriNews - AI Fake News Detector Website

A production-ready **Fake News Detector Web Application** built with Python 3.12, Flask, Scikit-learn, SQLite, and modern web design standards.

---

## 🌟 Key Features

1. **AI News Detector Hub**:
   - Accepts both news headline and full article text.
   - Computes real-time credibility predictions (**REAL NEWS ✅** / **FAKE NEWS ❌**).
   - Generates exact **Confidence Scores (%)**.
   - Extracts top **TF-IDF Keyword Indicators** and article metadata (Word count, Read time).

2. **Machine Learning Pipeline**:
   - Text preprocessing: punctuation removal, lowercasing, NLTK stopword filtering & WordNet lemmatization.
   - TF-IDF Vectorization (`ngram_range=(1, 2)`).
   - Multi-model evaluation comparing:
     - Logistic Regression
     - Multinomial Naive Bayes
     - Passive Aggressive Classifier
     - Random Forest Classifier
   - Automatically serializes the top-performing model to `model/model.pkl` and `vectorizer.pkl`.

3. **Prediction Audit & History**:
   - Persists all past predictions in SQLite via SQLAlchemy.
   - Search by keyword and filter by status (All, Real News, Fake News).
   - Single item deletion & bulk clear history.
   - Export history to downloadable **CSV file**.
   - Download official **PDF Verification Certificates** for any prediction record.

4. **Admin Dashboard & Analytics**:
   - Protected admin authentication (`admin` / `Admin@123456`).
   - Counter cards for total predictions, real vs fake breakdown, and average confidence.
   - Interactive **Chart.js Visualizations**:
     - Real vs Fake Distribution Doughnut Chart.
     - 7-Day Prediction Activity Trend Line Chart.
   - Real-time audit activity feed.

5. **Modern UI & Aesthetic System**:
   - Dark + Blue Theme with Glassmorphism backdrop filters.
   - Persistent **Dark/Light Mode** switcher.
   - Typing effect header animation & loading state spinners.
   - Fully responsive across mobile, tablet, and desktop devices.

---

## 📁 Project Structure

```text
fake-news-detector/
├── app.py                  # Main Flask application & route controllers
├── config.py               # Application configuration & paths
├── database.py             # Database initialization & default admin seeder
├── models.py               # SQLAlchemy ORM models (User, PredictionHistory)
├── forms.py                # Flask-WTF forms & CSRF protection
├── predict.py              # ML inference module & feature extraction
├── train_model.py          # ML training pipeline & model comparison script
├── utils.py                # Preprocessing, PDF generator, CSV exporter & metadata helpers
├── requirements.txt        # Python dependency manifest
├── Procfile                # Heroku / Render deployment process definition
├── runtime.txt             # Python runtime specification
├── gunicorn.conf.py        # Production WSGI server configuration
├── README.md               # Complete project documentation
├── dataset/
│   ├── README.md           # Dataset instructions
│   ├── Fake.csv            # Fake news CSV dataset
│   └── True.csv            # Real news CSV dataset
├── model/
│   ├── model.pkl           # Winning trained model binary
│   ├── vectorizer.pkl      # Trained TF-IDF vectorizer binary
│   └── model_meta.pkl      # Model metadata & evaluation metrics
├── uploads/                # Directory for generated reports & files
├── static/
│   ├── css/
│   │   └── style.css       # Design system, CSS variables & glassmorphism styles
│   └── js/
│       ├── main.js         # Theme toggle, typing effect & AJAX detector logic
│       └── charts.js       # Chart.js initialization for admin dashboard
└── templates/
    ├── base.html           # Master layout template
    ├── index.html          # Home page with hero section & stats
    ├── detector.html       # Interactive news analysis console
    ├── history.html        # Searchable prediction history table
    ├── login.html          # Admin authentication page
    ├── admin.html          # Admin analytics dashboard
    ├── 404.html            # Custom 404 error page
    └── 500.html            # Custom 500 error page
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites & Environment Setup
Ensure you have **Python 3.12+** installed on your system.

```bash
# Clone or navigate to the project directory
cd "Fake news detector"

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Train the Machine Learning Model
Run the model training pipeline:

```bash
python train_model.py
```

*Note: If `dataset/Fake.csv` and `dataset/True.csv` are present, it will train on them. If they are not found, `train_model.py` automatically generates a balanced sample dataset so you can run and test the app immediately out-of-the-box!*

### 3. Launch the Web Application
Run the Flask server:

```bash
python app.py
```

Open your browser and navigate to:
**`http://localhost:5000`**

---

## 🔑 Admin Credentials

To access the Admin Dashboard at `http://localhost:5000/login`:
- **Username**: `admin`
- **Password**: `Admin@123456`

---

## 🌐 Deployment Instructions

### 1. Render / Railway Deployment
1. Connect your GitHub repository to Render or Railway.
2. Select **Python Environment**.
3. Build Command:
   ```bash
   pip install -r requirements.txt && python train_model.py
   ```
4. Start Command:
   ```bash
   gunicorn app:app --config gunicorn.conf.py
   ```

### 2. PythonAnywhere Deployment
1. Upload the project folder to your PythonAnywhere web dashboard.
2. Create a virtualenv with Python 3.12 and run `pip install -r requirements.txt`.
3. Run `python train_model.py` in the Bash console.
4. Point your Web app WSGI configuration file to `app.py` (`from app import app as application`).

---

## 🔒 Security Measures
- **CSRF Protection**: Integrated via `Flask-WTF` on all post requests.
- **SQL Injection Prevention**: Built using `SQLAlchemy ORM` parameterized queries.
- **XSS Sanitization**: Managed via `Jinja2` autoescaping.
- **Password Hashing**: Encrypted using Werkzeug `PBKDF2` key stretching.
