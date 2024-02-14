# Import necessary libraries
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

class Forecast:
    pass

np.random.seed(42)
months = np.arange(1, 13)
sales = np.random.randint(50, 200, size=(12,))


months = months.reshape(-1, 1)


X_train, X_test, y_train, y_test = train_test_split(months, sales, test_size=0.2, random_state=42)


model = LinearRegression()
model.fit(X_train, y_train)


predictions = model.predict(X_test)


plt.scatter(X_test, y_test, color='black')
plt.plot(X_test, predictions, color='blue', linewidth=3)
plt.title('Sales Forecasting')
plt.xlabel('Month')
plt.ylabel('Sales')
plt.show()