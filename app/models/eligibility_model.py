import numpy as np
from sklearn.linear_model import LogisticRegression

# Dummy pre-trained model (for demo)
model = LogisticRegression()

# Fake training (replace with real data if available)
X_train = np.array([
    [3000, 1, 2, 650],
    [8000, 4, 10, 720],
    [1500, 5, 0, 500],
])
y_train = [1, 1, 0]  # 1 = eligible, 0 = not eligible

model.fit(X_train, y_train)


def predict_eligibility(features: dict):
    X = np.array([[
        features.get("income", 0),
        features.get("family_size", 1),
        features.get("employment_years", 0),
        features.get("credit_score", 650)
    ]])

    prob = model.predict_proba(X)[0][1]

    if prob > 0.7:
        return "APPROVE", prob
    elif prob > 0.4:
        return "SOFT_DECLINE", prob
    else:
        return "REJECT", prob
