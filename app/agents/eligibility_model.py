import numpy as np
import lightgbm as lgb

# --------------------------------------------------
# Feature order (MUST stay consistent)
# --------------------------------------------------
FEATURES = [
    "log_income",           # ↓ eligibility
    "income_per_capita",    # ↓ eligibility
    "family_size",          # ↑ eligibility
    "employment_years",     # ↑ eligibility
    "credit_score",         # ↑ eligibility
    "net_worth",            # ↓ eligibility
]

# Monotonic constraints aligned with policy
# -1 = decreasing, +1 = increasing
MONOTONE = [-1, -1, +1, +1, +1, -1]

# --------------------------------------------------
# Synthetic Training Data
# --------------------------------------------------
def generate_synthetic_data(n_samples=12000, seed=42):
    rng = np.random.default_rng(seed)

    income = np.exp(rng.normal(np.log(6000), 1.5, n_samples))
    income = np.clip(income, 500, 1e9)

    family_size = rng.integers(1, 7, n_samples)
    employment_years = rng.integers(0, 35, n_samples)
    credit_score = rng.normal(650, 90, n_samples).clip(300, 900)

    assets = rng.normal(50000, 150000, n_samples).clip(0, 5e7)
    liabilities = rng.normal(20000, 100000, n_samples).clip(0, 5e7)
    net_worth = assets - liabilities

    log_income = np.log1p(income)
    income_per_capita = income / family_size

    X = np.column_stack([
        log_income,
        income_per_capita,
        family_size,
        employment_years,
        credit_score,
        net_worth,
    ])

    # Policy-driven labels
    y = (
        (income_per_capita < 10000) |
        ((income_per_capita < 18000) & (family_size >= 3))
    ).astype(int)

    return X, y

# --------------------------------------------------
# Train model
# --------------------------------------------------
X_train, y_train = generate_synthetic_data()

train_set = lgb.Dataset(X_train, label=y_train)

params = {
    "objective": "binary",
    "metric": "binary_logloss",
    "learning_rate": 0.05,
    "num_leaves": 31,
    "max_depth": -1,
    "min_data_in_leaf": 50,
    "feature_fraction": 0.9,
    "bagging_fraction": 0.9,
    "bagging_freq": 1,
    "monotone_constraints": MONOTONE,
    "verbosity": -1,
    "seed": 42,
}

model = lgb.train(
    params,
    train_set,
    num_boost_round=300
)

# --------------------------------------------------
# Prediction API
# --------------------------------------------------
def predict_eligibility(features: dict):
    """
    Predict eligibility outcome.

    Returns:
        decision (str): APPROVE | SOFT_DECLINE | REJECT
        probability (float)
    """

    # Safe extraction
    income = max(0, features.get("income") or 0)
    family_size = max(1, int(features.get("family_size") or 1))
    employment_years = max(0, int(features.get("employment_years") or 0))
    credit_score = features.get("credit_score") or 650

    assets = features.get("assets") or 0
    liabilities = features.get("liabilities") or 0
    net_worth = assets - liabilities

    log_income = np.log1p(income)
    income_per_capita = income / family_size

    X = np.array([[ 
        log_income,
        income_per_capita,
        family_size,
        employment_years,
        credit_score,
        net_worth
    ]])

    prob = float(model.predict(X)[0])

    if prob >= 0.75:
        decision = "APPROVE"
    elif prob >= 0.45:
        decision = "SOFT_DECLINE"
    else:
        decision = "REJECT"

    return decision, prob
