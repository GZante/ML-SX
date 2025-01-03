import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

# Load data from Excel file
file_path = "file-path_goes_here"
df = pd.read_excel(file_path)

# Ignore the column named "Reference (DOI)"
df = df.drop(columns=["Reference (DOI)"])

# Filter out extraction efficiency values lower than 1% and higher than 99%
df = df[(df['E'] <= 0.99) & (df['E'] >= 0.01)]

# Preprocessing
features = df.drop(columns=["E"])
target = df["E"]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.3, random_state=42)

# Scaling features using MinMaxScaler
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Initialize GradientBoostingRegressor
gbr = GradientBoostingRegressor()

# Define the parameter grid for GridSearchCV
param_grid = {
    'n_estimators': [100, 200, 300],
    'learning_rate': [0.01, 0.1, 0.2],
    'max_depth': [3, 4, 5],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'subsample': [0.8, 1.0]
}

# Perform GridSearchCV to find the best parameters using the training set
grid_search = GridSearchCV(gbr, param_grid, cv=5, scoring='neg_mean_squared_error', n_jobs=-1)
grid_search.fit(X_train_scaled, y_train)

# Get the best parameters and the best model
best_params = grid_search.best_params_
best_gbr = grid_search.best_estimator_

# Train the model with the best parameters on the training set
best_gbr.fit(X_train_scaled, y_train)

# Prediction on testing set
y_pred = best_gbr.predict(X_test_scaled)

# Metrics for testing set
r_squared = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mse = mean_squared_error(y_test, y_pred)
aard = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

# Training set predictions and metrics
y_train_pred = best_gbr.predict(X_train_scaled)
train_r_squared = r2_score(y_train, y_train_pred)
train_aard = np.mean(np.abs((y_train - y_train_pred) / y_train)) * 100
train_mse = mean_squared_error(y_train, y_train_pred)
train_rmse = np.sqrt(train_mse)
train_mae = mean_absolute_error(y_train, y_train_pred)

# Results
print("Best GradientBoostingRegressor with Optimized Parameters:")
print(f"Best parameters: {best_params}")
print(f"Testing - R2: {r_squared:.4f}, MAE: {mae:.4f}, RMSE: {rmse:.4f}, MSE: {mse:.4f}, AARD: {aard:.4f}%")
print(f"Training - R2: {train_r_squared:.4f}, MAE: {train_mae:.4f}, RMSE: {train_rmse:.4f}, MSE: {train_mse:.4f}, AARD: {train_aard:.4f}%")

# Plotting
plt.scatter(y_test, y_pred)
# Linear fit in red
z = np.polyfit(y_test, y_pred, 1)
p = np.poly1d(z)
plt.plot(y_test, p(y_test), "r-", label='Best Linear Fit')

# y = x line for comparison
plt.plot(y_test, y_test, 'k-', label='y = x')

# Adjusting labels and adding legend
plt.xlabel("Experimental E")
plt.ylabel("Calculated E")
plt.title("Best Model Performance with GradientBoostingRegressor")
plt.legend(frameon=False)
plt.show()
