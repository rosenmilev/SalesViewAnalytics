import pandas as pd
import numpy as np



def read_data(file_path):
    data = pd.read_csv(file_path)
    return data


class CleanData:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        # TODO Move setting of these values outside class, user input preferably.
        self.critical_columns = ['Order ID', 'City', 'State', 'Postal Code', 'Product ID', 'Sales', 'Country',
                                 'Order Date', 'Ship Date', 'Customer ID', 'Customer Name', 'Row ID', 'Product Name']
        self.categorical_columns = ['Ship Mode', 'Segment', 'Category', 'Sub-Category']
        self.columns_to_drop = ['Row ID']
        self.column_type_map = {'Order Date': 'datetime',
                                'Ship Date': 'datetime',
                                'Sales': 'float',
                                'Postal Code': 'int',
                                'Ship Mode': 'str',
                                'Customer Name': 'str',
                                'Country': 'str',
                                'Segment': 'str',
                                'City': 'str',
                                'State': 'str',
                                'Region': 'str',
                                'Product ID': 'str',
                                'Category': 'str',
                                'Sub-Category': 'str',
                                'Product Name': 'str',
                                }

    def main(self):
        if self.calculate_missing_values_percentage() <= 30:
            self.handling_missing_values()
            for col in self.dataframe.columns.values:
                self.remove_redundant_columns(col)
                if col:
                    self.correct_datatypes(col)

    # What percent of data is missing and deside if the dataset is suitable for analysis.
    # TODO implement logic not to accept datasets with more than 30% missing values.
    def calculate_missing_values_percentage(self):
        total_cells = self.dataframe.shape[0] * self.dataframe.shape[1]
        print(total_cells)
        total_missing = self.dataframe.isnull().sum().sum()
        print(total_missing)
        percent_missing_total = (total_missing / total_cells) * 100
        return round(percent_missing_total, 3)

    # Depending on the importance and type of missing values, handle them by removing the row with missing value,
    # or fill it with the most common value for that column.
    # TODO Think how to provide to user decision how to handle missing values and which columns to drop.
    def handling_missing_values(self):
        # Handle the critical columns by deleting the rows with missing data.
        self.dataframe = self.dataframe.dropna(subset=self.critical_columns)
        # Handle the categorical columns by filling them with most common value in each column.
        for column in self.categorical_columns:
            mode_value = self.dataframe[column].mode()[0]
            self.dataframe.loc[:, column] = self.dataframe[column].fillna(mode_value)

    # Remove all the redundant columns
    def remove_redundant_columns(self, column_name):
        # Drop user defined columns since they are not needed for db design.
        self.dataframe.drop(columns=self.columns_to_drop, inplace=True, errors='ignore')

    def correct_datatypes(self, column_name):
        if column_name == 'Order Date' or column_name == 'Ship Date':
            self.dataframe[column_name] = pd.to_datetime(self.dataframe[column_name])
        elif column_name == 'Sales':
            self.dataframe[column_name] = self.dataframe[column_name].astype(float)
        elif column_name == 'Postal Code':
            self.dataframe[column_name] = self.dataframe[column_name].astype(int)
        else:
            self.dataframe[column_name] = self.dataframe[column_name].astype(str)


data = read_data('sales_dataset.csv')

handle_data = CleanData(data)

print(handle_data.calculate_missing_values_percentage())
# handle_data.remove_redundant_columns()
handle_data.handling_missing_values()
cleaned_data = handle_data.dataframe
print(handle_data.calculate_missing_values_percentage())
print(handle_data.dataframe.dtypes)


if __name__ == '__main__':
    pass
