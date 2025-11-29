# train_model.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

df = pd.read_csv("data/hospital_history.csv")
features = ["aqi", "temp", "season", "viral_cases", "festival_flag"]
X = df[features]
y = df["hospital_load"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/hospital_model.pkl")

print("Model saved to models/hospital_model.pkl")
print("Train score:", model.score(X_train, y_train))
print("Test score:", model.score(X_test, y_test))
