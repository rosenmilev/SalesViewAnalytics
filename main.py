import pandas as pd
import numpy as np
import sqlite3
from sqlite3 import Error


def read_data(file):
    data = pd.read_csv('sales_dataset.csv')
    return data


class CleanData:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        # To move setting of these values outside class, user input preferably.
        self.critical_columns = ['Order ID', 'City', 'State', 'Postal Code', 'Row ID', 'Product ID', 'Sales', 'Country',
                                 'Order Date', 'Ship Date', 'Customer ID', 'Customer Name', 'Row ID', 'Product Name']
        self.categorical_columns = ['Ship Mode', 'Segment', 'Category', 'Sub-Category']

    # What percent of data is missing and deside if the dataset is suitable for analysis.
    def calculate_missing_values_percentage(self):
        total_cells = self.dataframe.shape[0] * self.dataframe.shape[1]
        total_missing = self.dataframe.isnull().sum().sum()
        percent_missing_total = (total_missing / total_cells) * 100
        return percent_missing_total

    # Depending on the importance and type of missing values, handle them by removing the row with missing value,
    # or fill it with the most common value for that column.

    def handling_missing_values(self):
        # Handle the critical columns by deleting the rows with missing data.
        self.dataframe = self.dataframe.dropna(subset=self.critical_columns)
        # Handle the categorical columns by filling them with most common value in each column.
        for column in self.categorical_columns:
            self.dataframe = self.dataframe[column].fillna(self.dataframe[column].mode()[0])


data = read_data('sales_dataset.csv')

handle_data = CleanData(data)
print(handle_data.calculate_missing_values_percentage())



if __name__ == '__main__':
    pass


