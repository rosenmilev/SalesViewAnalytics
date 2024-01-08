import time

from kivy.config import Config

# Set the desired window size (width x height)
Config.set('graphics', 'width', '1550')
Config.set('graphics', 'height', '800')

from kivymd.uix.button import MDFlatButton
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.pickers import MDDatePicker
from kivymd.app import MDApp
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from kivymd.uix.card import MDCard
from visualisations.visualisation_manager import Visualisations
from visualisations.analytics_manager import reports, analytics

import csv
import os
import subprocess
from datetime import datetime
import logging


logging.getLogger('matplotlib').setLevel(logging.WARNING)


# Custom widget for displaying matplotlib figures
class PlotCard(MDCard):
    def add_plot(self, fig):
        canvas = FigureCanvasKivyAgg(fig)
        self.add_widget(canvas)


# Custom widget for dashboard cards
class DashboardCard(MDCard):
    pass


# Custom widget for navigation menu for switching between screens
class ContentNavigationDrawer(MDScrollView):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


# Main Kivy App - It has 3 screens
class SalesViewAnalytics(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Light"
        return Builder.load_file('main.kv')


# Generate all the dynamic widgets and their properties for Dashboard Screen
class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visualisations = Visualisations()
        self.data_provider = reports

    def on_kv_post(self, base_widget):
        monthly_sales = self.visualisations.vis_sales_by_month()
        top_customers = self.visualisations.vis_top_customers()
        top_sub_categories = self.visualisations.vis_top_sub_categories()
        sales_by_category = self.visualisations.vis_sales_by_category()

        self.ids.monthly_sales_card.add_plot(monthly_sales)
        self.ids.top_customers_card.add_plot(top_customers)
        self.ids.top_sub_categories_card.add_plot(top_sub_categories)
        self.ids.sales_by_category_card.add_plot(sales_by_category)

        self.ids.daily_info.card_title = f'Current date: {self.data_provider.current_date}'
        self.ids.daily_info.today_sales = f'{self.data_provider.current_month_today_sales}'
        self.ids.daily_info.average_sales_client = f'{self.data_provider.current_month_average_sales_by_client}'
        self.ids.daily_info.average_sales_order = f'{self.data_provider.current_month_average_sales_by_order}'
        self.ids.daily_info.number_of_clients = f'{self.data_provider.current_month_customer_count}'
        self.ids.daily_info.number_of_orders = f'{self.data_provider.current_month_orders_count}'


# Generate all the dynamic widgets and their properties for Report Screen
class ReportsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_prover = reports
        self.dates = ''
        self.current_report = []

    def on_save(self, instance, value, date_range):
        if date_range:
            self.dates = [date_range[0].strftime('%Y-%m-%d'), date_range[-1].strftime('%Y-%m-%d')]
            self.ids.r_date_picker.text = f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[-1].strftime('%Y-%m-%d')}"
        else:
            pass

    # Date picker settings
    def on_cancel(self, instance, value):
        pass

    def show_date_picker(self):
        date_dialog = MDDatePicker(min_year=2015, max_year=2018, mode='range', year=2018, month=12, day=23)

        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()
        # self.add_widget(self.table)

    def export_to_csv(self):
        try:
            dir_path = '../data/exported_files'
            os.makedirs(dir_path, exist_ok=True)  # Create directory if it doesn't exist
            file_name = f'report_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.csv'
            file_path = os.path.join(dir_path, file_name)

            # Write data to CSV
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                for row in self.current_report:
                    writer.writerow(row)

            # Save the path for later use
            self.exported_file_path = file_path

            # Show the dialog
            self.show_confirmation_dialog()
        except Exception as e:
            print(f"Error exporting to CSV: {e}")

    def show_confirmation_dialog(self):
        self.dialog = MDDialog(
            title="File Successfully Generated!",
            text="Would you like to open it?",
            buttons=[
                MDFlatButton(
                    text="NO", on_release=self.close_dialog
                ),
                MDFlatButton(
                    text="YES", on_release=self.open_exported_file
                ),
            ],
        )
        self.dialog.open()

    def close_dialog(self, *args):
        # Just close the dialog
        self.dialog.dismiss()

    def open_exported_file(self, *args):
        if os.name == 'nt':  # for Windows
            os.startfile(self.exported_file_path)
        else:
            opener = 'open' if os.name == 'mac' else 'xdg-open'
            subprocess.call([opener, self.exported_file_path])
        self.dialog.dismiss()

    def generate_report(self):
        self.current_report = []
        self.ids.table_container.clear_widgets()

        if not self.dates:
            return

        query_params = {
            'start_date': self.dates[0],
            'end_date': self.dates[1],
            'include_segment': self.ids.segment_checkbox.active,
            'include_customer': self.ids.customer_checkbox.active,
            'include_region': self.ids.region_checkbox.active,
            'include_product': self.ids.product_checkbox.active
        }

        data = self.data_prover.generate_report(query_params)

        data[0].append('Period')
        print(data)
        self.current_report.append(tuple(data[0], ))
        column_data = [(col, dp(30 if col != 'Product Name' else 100)) for col in data[0]]

        report_period = (f"{self.dates[0]} - {self.dates[1]}",)
        data_with_period = [row + report_period for row in data[1:]]
        self.current_report = tuple(self.current_report) + tuple(data_with_period)

        row_data = [tuple(map(str, row)) for row in data_with_period]  # Convert all items to strings

        # Creating the data table
        self.table = MDDataTable(
            size_hint=(0.9, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Center the table
            column_data=column_data,
            row_data=row_data,
            use_pagination=True,
            rows_num=10
        )
        if self.current_report:
            self.ids.export_button.opacity = 1
            self.ids.export_button.disabled = False
        self.ids.table_container.add_widget(self.table)


# Generate all the dynamic widgets and their properties for Analytics Screen
class AnalyticsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_provider = reports
        self.dates = ''
        self.dropdown_selection_1 = ''
        self.dropdown_selection_2 = ''
        self.data = ''

    def on_enter(self):
        menu_items_1 = [
            {
                "text": "Compare Segments",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Compare Segments": self.menu_1_callback(x),
            },
            {
                "text": "Compare Regions",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Compare Regions": self.menu_1_callback(x),
            },
            {
                "text": "Compare Products",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Compare Products": self.menu_1_callback(x),
            },
        ]
        self.menu_1 = MDDropdownMenu(
            caller=self.ids.analysis_dropdown,
            items=menu_items_1,
            width_mult=4,
        )

        self.menu_2 = MDDropdownMenu(
            caller=self.ids.item_dropdown,
            items='',
            width_mult=4,
        )

    def on_kv_post(self, base_widget):
        pass

    def open_menu_1(self, analysis_dropdown):
        # Open the menu on the button
        self.menu_1.caller = analysis_dropdown
        self.menu_1.open()

    def populate_and_enable_second_menu(self):
        if not self.dates or not self.dropdown_selection_1:
            return
        menu_items_2 = self.generate_menu_2_items()
        self.menu_2.items = menu_items_2
        self.menu_2.caller = self.ids.item_dropdown  # Ensure the caller is set
        self.ids.item_dropdown.disabled = False  # Enable the button
        self.ids.item_dropdown.opacity = 1  # Make the button fully visible

    def menu_1_callback(self, text_item):
        self.dropdown_selection_1 = text_item
        self.ids.analysis_dropdown.text = text_item
        self.menu_1.dismiss()
        self.populate_and_enable_second_menu()

    def menu_2_callback(self, text_item):
        self.dropdown_selection_2 = text_item
        self.ids.item_dropdown.text = text_item

        self.menu_2.dismiss()

    def generate_menu_2_items(self):

        self.data = self.generate_data(self.dates[0], self.dates[1])
        items_data = self.data
        if not items_data or not self.dates:
            return

        return [
            {
                "text": f"{item[1]}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{item[1]}": self.menu_2_callback(x),
            } for item in items_data[1:]
        ]

    def generate_result(self):
        if not self.dropdown_selection_1 or not self.dropdown_selection_2 or not self.dates:
            return
        self.ids.item_dropdown.disabled = True  # Enable the button
        self.ids.item_dropdown.opacity = 0

        self.ids.a_date_picker.text = "Select Period"
        self.ids.analysis_dropdown.text = "Select Type"
        self.ids.item_dropdown.text = 'Select Item'



        if 'Product' in self.dropdown_selection_1:

            current_item = [res for res in self.data if res[1] == self.dropdown_selection_2][0][2]

            params = (self.dates[0], self.dates[1], 'od.product_id', current_item)
        elif 'Segment' in self.dropdown_selection_1:
            current_item = [res for res in self.data if res[1] == self.dropdown_selection_2][0][1]
            params = (self.dates[0], self.dates[1], 'c.segment', current_item)
        elif 'Region':
            current_item = [res for res in self.data if res[1] == self.dropdown_selection_2][0][1]
            params = (self.dates[0], self.dates[1], 'st.region', current_item)

        result_current, result_last, figure = analytics.generate_result(params)

        # result_current.append(('Sales', 'Date'))
        # result_last.append(('Sales', 'Date'))

        column_data = [('Sales', dp(30)), ('Date', dp(30))]
        row_data_current = [tuple(map(str, row)) for row in result_current]
        row_data_last = [tuple(map(str, row)) for row in result_last]

        table_1 = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Center the table
            column_data=column_data,
            row_data=row_data_current,
            use_pagination=True,
            rows_num=10
        )

        table_2 = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Center the table
            column_data=column_data,
            row_data=row_data_last,
            use_pagination=True,
            rows_num=10
        )

        self.ids.a_plot.clear_widgets()
        self.ids.a_plot.add_plot(figure)

        self.ids.a_table_container_current.clear_widgets()
        self.ids.a_table_container_current.add_widget(table_1)

        self.ids.a_table_container_last.clear_widgets()
        self.ids.a_table_container_last.add_widget(table_2)




    def generate_data(self, start_date, end_date):
        if not self.dates:
            return

        if not self.dropdown_selection_1:
            pass

        query_params = {
            'start_date': start_date,
            'end_date': end_date,
            'include_segment': False,
            'include_customer': False,
            'include_region': False,
            'include_product': False
        }

        if self.dropdown_selection_1 == "Compare Segments":
            query_params["include_segment"] = True
        elif self.dropdown_selection_1 == "Compare Regions":
            query_params["include_region"] = True
        elif self.dropdown_selection_1 == 'Compare Products':
            query_params["include_product"] = True

        data = self.data_provider.generate_report(query_params)

        return data

    def on_save(self, instance, value, date_range):
        if date_range:
            self.dates = [date_range[0].strftime('%Y-%m-%d'), date_range[-1].strftime('%Y-%m-%d')]
            self.ids.a_date_picker.text = f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[-1].strftime('%Y-%m-%d')}"
        else:
            pass

    # Date picker settings
    def on_cancel(self, instance, value):
        pass

    def show_date_picker(self):
        date_dialog = MDDatePicker(min_year=2018, mode='range', max_year=2018, year=2018, month=12)

        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()


if __name__ == '__main__':
    SalesViewAnalytics().run()
