from sklearn.metrics import accuracy_score, classification_report
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from config.database import get_db_connection


# Database connection
connection = get_db_connection()

query = """
SELECT
    vehicle_count,
    average_speed,
    traffic_density,
    weather,
    accident,
    traffic_level
FROM traffic_data
"""

df = pd.read_sql(query, connection)

connection.close()


# Check data
print("Traffic Data:")
print(df)

print("\nTotal Records:", len(df))


# Convert accident into numeric value
df["accident"] = df["accident"].astype(int)


# Convert weather into dummy variables
df = pd.get_dummies(
    df,
    columns=["weather"],
    dtype=int
)


# Features and target
X = df.drop("traffic_level", axis=1)

y = df["traffic_level"]


# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# Create model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# Train model
model.fit(X_train, y_train)


# Prediction
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

# Save Model
with open("models/traffic_model.pkl", "wb") as file:
    pickle.dump(model, file)

# Save Feature Columns
with open("models/feature_columns.pkl", "wb") as file:
    pickle.dump(X.columns.tolist(), file)

print("\nModel evaluation completed!")
print("Model saved successfully!")

# Save model
with open("models/traffic_model.pkl", "wb") as file:
    pickle.dump(model, file)


# Save feature columns
with open("models/feature_columns.pkl", "wb") as file:
    pickle.dump(X.columns.tolist(), file)


print("\nModel trained successfully!")

print("traffic_model.pkl created successfully!")

print("feature_columns.pkl created successfully!")