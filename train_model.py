import pandas as pd
import numpy as np
import re
import nltk
import joblib

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

nltk.download("stopwords", quiet=True)

# ----------------------------------------------------
# 1. Load Dataset
# ----------------------------------------------------
print("Loading dataset from dataset/phishing_email.csv...")
df = pd.read_csv("dataset/phishing_email.csv")
print(f"Total records loaded: {len(df)}")

# ----------------------------------------------------
# 2. Preprocessing
# ----------------------------------------------------
stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))

def clean_text(text):
    text = str(text).lower()
    # Corrected regex for stripping URLs cleanly
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    # Remove non-alphabetic characters
    text = re.sub(r"[^a-zA-Z]", " ", text)
    words = text.split()
    words = [
        stemmer.stem(word)
        for word in words
        if word not in stop_words
    ]
    return " ".join(words)

print("Preprocessing messages (lowercasing, URL removal, tokenization, stop-words, stemming)...")
df["clean_text"] = df["email_text"].apply(clean_text)

# ----------------------------------------------------
# 3. TF-IDF Feature Extraction
# ----------------------------------------------------
print("Extracting TF-IDF features (max_features=5000)...")
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df["clean_text"])
y = df["label"]

# ----------------------------------------------------
# 4. Stratified Train/Test Split (80:20)
# ----------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
print(f"Training samples: {X_train.shape[0]} | Testing samples: {X_test.shape[0]}")

# ----------------------------------------------------
# 5. Comparative Evaluation of 5 Classifiers (Table II)
# ----------------------------------------------------
print("\n" + "=" * 76)
print("BENCHMARKING 5 SUPERVISED CLASSIFIERS (MATCHING RESEARCH PAPER TABLE II)")
print("=" * 76)
print(f"{'Model':24s} | {'Acc (%)':8s} | {'Prec (%)':8s} | {'Rec (%)':8s} | {'F1 (%)':8s}")
print("-" * 76)

benchmark_models = {
    "Multinomial Naive Bayes": MultinomialNB(),
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Linear SVM (Raw Margin)": LinearSVC(random_state=42),
}

for name, clf in benchmark_models.items():
    clf.fit(X_train, y_train)
    pred = clf.predict(X_test)
    acc = accuracy_score(y_test, pred) * 100
    prec = precision_score(y_test, pred, pos_label="spam", zero_division=0) * 100
    rec = recall_score(y_test, pred, pos_label="spam", zero_division=0) * 100
    f1 = f1_score(y_test, pred, pos_label="spam", zero_division=0) * 100
    print(f"{name:24s} | {acc:8.2f} | {prec:8.2f} | {rec:8.2f} | {f1:8.2f}")

print("=" * 76)

# ----------------------------------------------------
# 6. Train Production Models: Linear SVM (Champion) & RF
# ----------------------------------------------------
print("\nTraining Calibrated Linear SVM (Paper Champion)...")
cal_svm = CalibratedClassifierCV(estimator=LinearSVC(random_state=42), cv=5)
cal_svm.fit(X_train, y_train)

svm_pred = cal_svm.predict(X_test)
svm_acc = accuracy_score(y_test, svm_pred) * 100
svm_f1 = f1_score(y_test, svm_pred, pos_label="spam") * 100
print(f"Linear SVM Champion -> Accuracy: {svm_acc:.2f}%, F1-Score: {svm_f1:.2f}%")

print("\nTraining Random Forest (Comparative Benchmark)...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

rf_pred = rf_model.predict(X_test)
rf_acc = accuracy_score(y_test, rf_pred) * 100
rf_f1 = f1_score(y_test, rf_pred, pos_label="spam") * 100
print(f"Random Forest -> Accuracy: {rf_acc:.2f}%, F1-Score: {rf_f1:.2f}%")

# ----------------------------------------------------
# 7. Extract Feature Weights for Explainability (XAI)
# ----------------------------------------------------
raw_svm = benchmark_models["Linear SVM (Raw Margin)"]
feature_names = vectorizer.get_feature_names_out()
weights = raw_svm.coef_[0]
feature_weights = {word: float(weight) for word, weight in zip(feature_names, weights)}

# ----------------------------------------------------
# 8. Save Models and Metadata
# ----------------------------------------------------
print("\nSaving trained models and vectorizer to models/ ...")
# Default model points to the Paper's Champion (Linear SVM)
joblib.dump(cal_svm, "models/phishing_model.pkl")
joblib.dump(cal_svm, "models/svm_model.pkl")
joblib.dump(rf_model, "models/rf_model.pkl")
joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")
joblib.dump(feature_weights, "models/feature_weights.pkl")

print("\nAll models and XAI feature weights saved successfully!")
