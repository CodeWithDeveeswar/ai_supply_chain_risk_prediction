import pandas as pd
import joblib
import os
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    balanced_accuracy_score,
    confusion_matrix
)

warnings.filterwarnings("ignore")

# ================= CONFIG =================
DATA_PATH = "data/supply_chain_data.csv"
MODEL_PATH = "model/risk_model.pkl"
REPORT_DIR = "model/reports"

os.makedirs("model", exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# ================= LOAD DATA =================
if not os.path.exists(DATA_PATH):
    print(f"Dataset not found: {DATA_PATH}")
    exit()

df = pd.read_csv(DATA_PATH)

if df.empty:
    print("Dataset is empty.")
    exit()

print("\n" + "=" * 60)
print("TRAINING STARTED")
print("=" * 60)
print(f"Dataset Rows : {len(df)}")

# ================= CLEAN DATA =================
df = df.dropna()

features = [
    "delay",
    "traffic",
    "weather",
    "inventory",
    "order_value",
    "port_delay"
]

X = df[features]
y = df["risk"]

# ================= SPLIT DATA =================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ================= BUILD MODEL =================
model = RandomForestClassifier(
    n_estimators=400,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)

print("\nTraining Random Forest Model...")
model.fit(X_train, y_train)

# ================= PREDICTION =================
y_pred = model.predict(X_test)

# ================= METRICS =================
accuracy = accuracy_score(y_test, y_pred)
bal_acc = balanced_accuracy_score(y_test, y_pred)

print("\n" + "=" * 60)
print("MODEL REPORT")
print("=" * 60)

print(f"Accuracy            : {accuracy * 100:.2f}%")
print(f"Balanced Accuracy   : {bal_acc * 100:.2f}%")

print("\nClass Distribution:")
print(y_test.value_counts())

print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

# ================= CONFUSION MATRIX =================
labels = ["Low", "Medium", "High"]
cm = confusion_matrix(y_test, y_pred, labels=labels)

plt.figure(figsize=(6, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=labels,
    yticklabels=labels
)

plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()

cm_path = os.path.join(REPORT_DIR, "confusion_matrix.png")
plt.savefig(cm_path)
plt.close()

# ================= FEATURE IMPORTANCE =================
importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values()

plt.figure(figsize=(6, 4))
importance.plot(kind="barh")

plt.title("Feature Importance")
plt.xlabel("Importance Score")
plt.tight_layout()

fi_path = os.path.join(REPORT_DIR, "feature_importance.png")
plt.savefig(fi_path)
plt.close()

# ================= CLASS-WISE ACCURACY =================
print("\nClass-wise Accuracy:")

for i, label in enumerate(labels):
    correct = cm[i][i]
    total = cm[i].sum()

    if total == 0:
        class_acc = 0
    else:
        class_acc = (correct / total) * 100

    print(f"{label:<6}: {class_acc:.2f}%")

print("=" * 60)

# ================= SAVE MODEL =================
joblib.dump(model, MODEL_PATH)

# ================= OUTPUT FILES =================
print("\nFiles Generated:")
print(f"Model              : {MODEL_PATH}")
print(f"Confusion Matrix   : {cm_path}")
print(f"Feature Importance : {fi_path}")

print("\nTraining Completed Successfully.")