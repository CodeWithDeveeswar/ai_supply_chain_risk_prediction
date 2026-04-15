import pandas as pd
import joblib
import os
import warnings

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, balanced_accuracy_score

warnings.filterwarnings("ignore")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("data/supply_chain_data.csv")

if df.empty:
    print("❌ CSV is empty")
    exit()

# ---------------- FEATURE SELECTION ----------------
# 🔥 Only meaningful features (avoid noise)
X = df[[
    "delay",
    "traffic",
    "weather",
    "inventory",
    "order_value",
    "port_delay"
]]

y = df["risk"]

# ---------------- TRAIN / TEST SPLIT ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y   # 🔥 keeps class balance
)

# ---------------- MODEL ----------------
model = RandomForestClassifier(
    n_estimators=400,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight="balanced_subsample",
    random_state=42
)

model.fit(X_train, y_train)

# ---------------- PREDICTION ----------------
y_pred = model.predict(X_test)

# ---------------- METRICS ----------------
accuracy = accuracy_score(y_test, y_pred)
bal_acc = balanced_accuracy_score(y_test, y_pred)

print("\n" + "="*50)
print("📊 MODEL PERFORMANCE SUMMARY")
print("="*50)

print(f"✅ Accuracy            : {round(accuracy*100, 2)}%")
print(f"⚖️ Balanced Accuracy  : {round(bal_acc*100, 2)}%")

print("\n📦 Class Distribution:")
print(y_test.value_counts())

print("\n📈 Classification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

print("="*50)

# ---------------- SAVE MODEL ----------------
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/risk_model.pkl")

print("\n🔥 Model trained and saved successfully")