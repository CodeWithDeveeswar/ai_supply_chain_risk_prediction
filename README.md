# 🚀 AI-Based Supply Chain Risk Prediction System

An AI-powered web application that predicts supply chain risk levels using a **Random Forest** machine learning model. The system enables administrators to analyze supply chain data, generate predictions, visualize insights through an interactive dashboard, and export reports.

---

## 📑 Table of Contents

- [Features](#-features)
- [Technologies Used](#️-technologies-used)
- [Project Structure](#-project-structure)
- [Installation](#️-installation)
- [Run the Application](#️-run-the-application)
- [Machine Learning](#-machine-learning)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)
- [License](#-license)

---

## ✨ Features

| | |
|---|---|
| 🔐 | Admin Login |
| 🤖 | AI-Based Risk Prediction |
| 📂 | Manual Data Entry & CSV Upload |
| 📊 | Interactive Dashboard with Charts |
| 📜 | Prediction History |
| 🔍 | Search & Filter Records |
| 📥 | Excel Report Export |
| 🖼️ | Dashboard Image Export |
| 💾 | SQLite Database Storage |

---

## 🛠️ Technologies Used

**Frontend**
- HTML5
- CSS3
- JavaScript
- Bootstrap
- Chart.js

**Backend**
- Python
- Flask

**Machine Learning**
- Scikit-learn
- Pandas
- NumPy
- Joblib

**Database**
- SQLite

---

## 📂 Project Structure

```text
ai_supply_chain_risk_prediction/
│
├── app.py
├── requirements.txt
├── config.py
│
├── model/
│   ├── train_model.py
│   ├── risk_model.pkl
│   └── reports/
│
├── database/
│   ├── database.db
│   └── db_setup.py
│
├── data/
│   └── supply_chain_data.csv
│
├── uploads/
│
├── Downloads/
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│
└── utils/
    ├── excel_export.py
    └── predictor.py
```

---

## ⚙️ Installation

**1. Clone the repository**

```bash
git clone https://github.com/CodeWithDeveeswar/ai_supply_chain_risk_prediction.git
```

**2. Navigate to the project directory**

```bash
cd ai_supply_chain_risk_prediction
```

**3. (Optional) Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

**1. Initialize the database**

```bash
python database/db_setup.py
```

**2. Train the model**

```bash
python model/train_model.py
```

**3. Start the Flask server**

```bash
python app.py
```

**4. Open your browser**

```
http://127.0.0.1:5000
```

---

## 📊 Machine Learning

| Detail | Description |
|---|---|
| **Algorithm** | Random Forest Classifier |
| **Prediction Classes** | Low, Medium, High Risk |
| **Evaluation Metrics** | Accuracy, Balanced Accuracy, Classification Report, Confusion Matrix, Feature Importance |

---

## 🚀 Future Enhancements

- [ ] Multi-user Authentication
- [ ] Cloud Database Integration
- [ ] Live Supply Chain Data Feeds
- [ ] REST API Support
- [ ] Deep Learning Models
- [ ] Email Notifications

---

## 👨‍💻 Author

**Deveeswar K**
MCA Student

---

## 📄 License

This project is developed for **academic and educational purposes**.
