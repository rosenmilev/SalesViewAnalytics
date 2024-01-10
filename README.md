# SalesViewAnalytics

Application usage

1. In 'SalesViewAnalytics/data/database/datasets' you could put csv file in the format, mentioned in the documentation or you can use the provided one for demo purposes. File name must be 'sales_dataset.csv'.

2. Initiate virtual environment and activate it. Install the dependencies from requirements.txt
IMPORTANT: After installing the requirements, you must manually install kivy.matplotlib with the following command: 'garden install matplotlib --kivy'.

3. Run the 'create_database.py' file, located in 'SalesViewAnalytics/data/database' to initiate database creation and populate it with data from the 'sales_dataset.csv'.

4. Start the application by running 'main.py' file, located in 'SalesViewAnalytics/app'.