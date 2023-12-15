import pandas as pd


def read_data(file_path):
    data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip()
    return data


class CleanData:
    def __init__(self, dataframe):
        self.dataframe = dataframe.copy()
        # TODO Move setting of these values outside class dynamically.
        self.rows_dropped = 0
        self.critical_columns = ['Order ID', 'City', 'State', 'Postal Code', 'Product ID', 'Sales', 'Country',
                                 'Order Date', 'Ship Date', 'Customer ID', 'Customer Name', 'Product Name']
        self.categorical_columns = ['Ship Mode', 'Segment', 'Category', 'Sub-Category']
        self.columns_to_drop = ['Row ID']
        self.column_type_map = {'Order Date': 'datetime',
                                'Ship Date': 'datetime',
                                'Sales': 'float64',
                                'Postal Code': 'str',
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
            self.remove_redundant_columns()
            self.handling_missing_values()
            self.correct_datatypes()
            self.drop_nan_rows()
            self.format_column_name()

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
        self.dataframe = self.dataframe.dropna(subset=self.critical_columns).copy()
        # Handle the categorical columns by filling them with most common value in each column.
        for column in self.categorical_columns:
            mode_value = self.dataframe[column].mode()[0]
            self.dataframe.loc[:, column] = self.dataframe[column].fillna(mode_value)

    # Remove all the redundant columns, selected by user
    def remove_redundant_columns(self):
        print(self.dataframe.columns)
        for column in self.columns_to_drop:
            if column in self.dataframe.columns:
                self.dataframe.drop(columns=column, inplace=True)
            else:
                print(f'Column {column} not found')
        unnamed_columns = [col for col in self.dataframe.columns if col.startswith('Unnamed')]
        if unnamed_columns:
            self.dataframe.drop(columns=unnamed_columns, inplace=True)
        print("Columns after dropping:", self.dataframe.columns)

    # Assign correct datatype for each column, change the date format to match SQLite one.
    def correct_datatypes(self):
        for col, data_type in self.column_type_map.items():
            try:
                if data_type == 'datetime':
                    self.dataframe[col] = pd.to_datetime(self.dataframe[col], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
                elif data_type in ['float64', 'int32']:
                    self.dataframe[col] = pd.to_numeric(self.dataframe[col], errors='coerce')
                elif data_type == 'str':
                    self.dataframe[col] = self.dataframe[col].astype(str)
                # No need to use copy() here since direct assignment is being used
            except Exception as e:
                print(f"Error converting column {col}: {e}")

    def drop_nan_rows(self):
        starting_row_count = len(self.dataframe)
        self.dataframe = self.dataframe.dropna().copy()
        final_row_count = len(self.dataframe)
        if starting_row_count != final_row_count:
            self.rows_dropped = starting_row_count - final_row_count
            print(f"Rows dropped: {self.rows_dropped}")

    # Format all the column names to consist only from lower case and replaces all not alnum symbols to _
    def format_column_name(self):
        self.dataframe.columns = self.dataframe.columns.str.lower().str.replace('[^a-zA-Z0-9]', '_', regex=True)



data = read_data('sales_dataset.csv')
cleaner = CleanData(data)
cleaner.main()
cleaned_data = cleaner.dataframe
cleaned_data.to_csv('sales_dataset_cleaned.csv', index=False)
