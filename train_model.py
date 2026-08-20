import os
import sys
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

from utils import clean_text

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
DATASET_DIR = os.path.join(os.path.dirname(__file__), 'dataset')

FAKE_CSV = os.path.join(DATASET_DIR, 'Fake.csv')
TRUE_CSV = os.path.join(DATASET_DIR, 'True.csv')

def generate_sample_dataset():
    """Generates synthetic sample Fake.csv and True.csv if real datasets are absent."""
    print("[Train] Real datasets not found. Generating sample Fake.csv and True.csv for demonstration...")
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    fake_samples = [
        {"title": "SHOCKING: Secret Alien Technology Uncovered in Underground Bunker", "text": "Anonymous sources claim that government officials have been hiding alien spaceships in secret underground facilities. Scientists allegedly reverse engineered extraterrestrial weapons. Share before this video gets deleted!"},
        {"title": "Miracle Plant Cures All Known Diseases Overnight, Doctors Furious", "text": "Big pharma doesn't want you to know about this simple backyard weed that eliminates all illnesses instantly. Drinking this tea twice daily restores full vitality and reverses aging. Doctors are trying to ban it nationwide."},
        {"title": "BREAKING: Global Economy Will Collapse Tomorrow Morning Says Insider", "text": "Unnamed financial gurus warn that all banks will close permanently at sunrise. Citizens are advised to convert all cash into gold coins immediately. Major financial institutions refuse to comment on the impending chaos."},
        {"title": "Famous Celebrity Secretly Replaced by Clone, Fans Claim", "text": "Social media users noticed subtle changes in ear shape and voice frequency of the pop icon. conspiracy theorists insist the real star was cloned in a top secret laboratory. Leaked memos confirm the clone substitution."},
        {"title": "Scientists Confirm Drinking Saltwater Increases Intelligence by 300%", "text": "A groundbreaking rogue study asserts that drinking untreated ocean water activates dormant brain cells. Researchers recommend replacing regular drinking water with seawater for maximum cognitive advantage."}
    ] * 60  # 300 sample rows
    
    true_samples = [
        {"title": "Central Bank Maintains Benchmark Interest Rates Amid Moderate Inflation", "text": "WASHINGTON (Reuters) - The Federal Reserve opted to hold key interest rates steady during its monthly policy meeting. Chairman stated that economic indicators show sustained labor market growth alongside stabilizing inflation targets."},
        {"title": "Global Climate Conference Reaches Landmark Renewable Energy Agreement", "text": "PARIS (AP) - Representatives from over 190 nations agreed to accelerate investments in solar and wind infrastructure. The multilateral accord sets binding targets to reduce global carbon emissions by 45 percent over the next decade."},
        {"title": "Health Ministry Launches National Immunization Campaign for Children", "text": "GENEVA (WHO) - Health authorities introduced an updated vaccine initiative targeting preventable childhood diseases across underserved rural communities. Medical experts emphasized the critical role of community outreach programs."},
        {"title": "Tech Giant Announces Breakthrough in Quantum Computing Efficiency", "text": "SAN FRANCISCO - Researchers unveiled a new fault-tolerant quantum processor capable of running complex simulations with reduced error rates. Peer-reviewed benchmarks were published in the journal Nature on Thursday."},
        {"title": "NASA Telescope Discovers Earth-Sized Exoplanet in Habitable Zone", "text": "CAPE CANAVERAL - Astronomers analyzing space telescope data confirmed an exoplanet orbiting a nearby dwarf star at a distance compatible with liquid surface water. Further atmospheric spectroscopic observations are scheduled."}
    ] * 60  # 300 sample rows
    
    df_fake = pd.DataFrame(fake_samples)
    df_true = pd.DataFrame(true_samples)
    
    df_fake.to_csv(FAKE_CSV, index=False)
    df_true.to_csv(TRUE_CSV, index=False)
    print(f"[Train] Sample datasets saved to {DATASET_DIR}")

def load_data():
    """Loads Fake.csv and True.csv datasets, combines and labels them."""
    if not (os.path.exists(FAKE_CSV) and os.path.exists(TRUE_CSV)):
        generate_sample_dataset()
        
    print(f"[Train] Loading datasets from {DATASET_DIR}...")
    df_fake = pd.read_csv(FAKE_CSV)
    df_true = pd.read_csv(TRUE_CSV)
    
    df_fake['label'] = 0  # 0 for FAKE
    df_true['label'] = 1  # 1 for REAL
    
    # Standardize columns
    for df in [df_fake, df_true]:
        if 'text' not in df.columns:
            if 'content' in df.columns:
                df['text'] = df['content']
            elif 'title' in df.columns:
                df['text'] = df['title']
        if 'title' not in df.columns:
            df['title'] = ''

    df_combined = pd.concat([df_fake, df_true], ignore_index=True)
    
    # Combine title and text for stronger contextual feature representation
    df_combined['full_text'] = df_combined['title'].fillna('') + " " + df_combined['text'].fillna('')
    df_combined = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"[Train] Total dataset size: {len(df_combined)} records ({len(df_fake)} Fake, {len(df_true)} Real).")
    return df_combined

def train_and_evaluate():
    df = load_data()
    
    print("[Train] Preprocessing text corpus with NLTK lemmatizer & stopword removal...")
    df['cleaned_text'] = df['full_text'].apply(clean_text)
    
    # Filter out empty preprocessed texts
    df = df[df['cleaned_text'].str.strip() != ''].reset_index(drop=True)
    
    X = df['cleaned_text']
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("[Train] Vectorizing text using TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Multinomial Naive Bayes': MultinomialNB(),
        'Passive Aggressive Classifier': PassiveAggressiveClassifier(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    }
    
    print("\n" + "="*60)
    print(" MODEL TRAINING AND COMPARISON METRICS ")
    print("="*60)
    
    best_model_name = None
    best_model = None
    best_accuracy = 0.0
    model_results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train_tfidf, y_train)
        y_pred = model.predict(X_test_tfidf)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        model_results[name] = {
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'model': model
        }
        
        print(f" -> Accuracy:  {acc * 100:.2f}%")
        print(f" -> Precision: {prec * 100:.2f}%")
        print(f" -> Recall:    {rec * 100:.2f}%")
        print(f" -> F1 Score:  {f1 * 100:.2f}%")
        
        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name
            best_model = model
            
    print("\n" + "="*60)
    print(f" WINNING MODEL: {best_model_name} (Accuracy: {best_accuracy * 100:.2f}%)")
    print("="*60)
    
    # Ensure model directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    model_save_path = os.path.join(MODEL_DIR, 'model.pkl')
    vec_save_path = os.path.join(MODEL_DIR, 'vectorizer.pkl')
    meta_save_path = os.path.join(MODEL_DIR, 'model_meta.pkl')
    
    joblib.dump(best_model, model_save_path)
    joblib.dump(vectorizer, vec_save_path)
    joblib.dump({
        'name': best_model_name,
        'accuracy': best_accuracy,
        'all_metrics': {k: {m: v[m] for m in ['accuracy', 'precision', 'recall', 'f1_score']} for k, v in model_results.items()}
    }, meta_save_path)
    
    print(f"\n[Train] Saved winning model to '{model_save_path}'")
    print(f"[Train] Saved vectorizer to '{vec_save_path}'")
    print(f"[Train] Model training pipeline completed successfully!\n")

if __name__ == '__main__':
    train_and_evaluate()
