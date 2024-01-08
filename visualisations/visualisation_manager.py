import matplotlib.pyplot as plt
import numpy as np
from data.data_extraction.query_manager import DataExtractor


# This class takes data from Analytics class as data_prover, and visualise the information.
class Visualisations:
    def __init__(self):
        self.data_provider = DataExtractor()
        self.month_names = {
            '1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'Jun', '7': 'Jul', '8': 'Aug', '9': 'Sept',
            '10': 'Oct', '11': 'Nov', '12': 'Dec'
        }
        self.color_scheme_bars = {
            'facecolor': "#e0e0e0",
            'bars': "#0343df",
            'background': '#F7F7F7',
            'line1': "#001146",
            'line2': '#cb416b'

        }

    def create_figure(self):
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor(self.color_scheme_bars['facecolor'])
        ax.set_facecolor(self.color_scheme_bars['background'])
        plt.style.use('ggplot')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return fig, ax

    def top_ten_plot(self, data, x_label, y_label):
        # Sort the data by purchase values in descending order
        data_sorted = sorted(data, key=lambda x: x[1])
        x, y = self.separate_data(data_sorted)

        fig, ax = self.create_figure()
        bars = ax.barh(x, y, color=self.color_scheme_bars['bars'])

        # Add the data labels to the bars
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width if width < ax.get_xlim()[1] * 0.05 else width - (ax.get_xlim()[1] * 0.02)
            ax.text(label_x_pos, bar.get_y() + bar.get_height() / 2, f'{int(width)}', ha='center' if width < ax.get_xlim()[1] * 0.05 else 'right', va='center', color='black')

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        plt.tight_layout()
        return fig, ax

    def draw_line_chart(self, ax, x, y, color, label, marker):
        ax.plot(x, y, color=color, label=label, marker=marker)

    # Util methods
    def separate_data(self, data):
        x = [item[0] for item in data]
        y = [item[1] for item in data]
        return x, y

    # G
    def vis_top_customers(self, year='2018'):
        data = self.data_provider.top_ten_customers(year)
        print(data)
        fig, ax = self.top_ten_plot(data, 'Purchases', f'Top 10 customers {year}')
        return fig

    def vis_top_sub_categories(self, year='2018'):
        data = self.data_provider.top_ten_sub_categories(year)
        fig, ax = self.top_ten_plot(data, 'Purchases', 'Sub Category')
        return fig

    def vis_sales_by_category(self, year='2018'):
        data = self.data_provider.segment_sales(year)
        print(data)
        # 'data' is expected to be a dictionary like {'Consumer': 15000, 'Corporate': 10000, 'Home Office': 5000}

        labels, sizes = self.separate_data(data)
        total = sum(sizes)

        explode = (0.05, 0.05, 0.05)  # This should be the same length as the number of segments

        fig, ax = self.create_figure()
        wedges, texts, autotexts = ax.pie(sizes,
                                          explode=explode,
                                          labels=labels,
                                          autopct=lambda p: '{:.1f}%\n({:.0f})'.format(p, p * total / 100),
                                          startangle=140,
                                          shadow=True)

        # Improve the display of the percentage/absolute value inside the pie chart
        for text in autotexts:
            text.set_color('black')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Add a circle at the center to improve 3D appearance
        plt.tight_layout()
        return fig

    def vis_sales_by_month(self, year='2018'):
        current_year_data = self.data_provider.monthly_sales(year)

        x, current_year_sales = self.separate_data(current_year_data)
        last_year = str(int(year) - 1)
        last_year_data = self.data_provider.monthly_sales(last_year)
        x, last_year_sales = self.separate_data(last_year_data)

        months = list(self.month_names.values())

        current_year_sales = np.array(current_year_sales, dtype=float)
        last_year_sales = np.array(last_year_sales, dtype=float)

        # Calculate percentage change safely
        percentage_change = np.zeros_like(current_year_sales)
        non_zero = last_year_sales != 0
        percentage_change[non_zero] = (current_year_sales[non_zero] - last_year_sales[non_zero]) / last_year_sales[
            non_zero] * 100

        fig, ax = self.create_figure()
        self.draw_line_chart(ax, months, current_year_sales, self.color_scheme_bars['line1'], year, 'o')
        self.draw_line_chart(ax, months, last_year_sales, self.color_scheme_bars['line2'], last_year, 'o')

        max_sales = np.max(np.concatenate((current_year_sales, last_year_sales)))
        sales_annotation_offset = max_sales * 0.02  # 2% of the max sales for annotation offset

        # Annotate the sales values for the current and last years
        for i, (curr, last) in enumerate(zip(current_year_sales, last_year_sales)):
            # Current year sales value annotations
            ax.annotate(f'{int(curr)}',
                        (months[i], curr),
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha='center')

            # Last year sales value annotations
            ax.annotate(f'{int(last)}',
                        (months[i], last),
                        textcoords="offset points",
                        xytext=(0, -15 if curr > last else 15),
                        ha='center')

            # Percentage change annotations
            pct_change = (curr - last) / last * 100 if last != 0 else 0
            pct_change_y_position = curr + (sales_annotation_offset if curr > last else -sales_annotation_offset)
            pct_change_text_offset = 15 if curr > last else -15
            if pct_change != 0:  # Only annotate if there's a percentage change
                ax.annotate(f'{pct_change:.1f}%',
                            (months[i], pct_change_y_position),
                            textcoords="offset points",
                            xytext=(0, pct_change_text_offset),
                            ha='center',
                            color='green' if pct_change > 0 else 'red')

        ax.legend(loc='best')
        ax.set_ylabel('Total Sales')
        ax.set_xlabel('Month')

        ax.set_xticks(months)
        ax.set_xticklabels(months, rotation=45)

        plt.tight_layout()
        return fig

    def vis_two_items(self, current_value, last_value, name, current_dates, last_dates):
        # Data
        values = [current_value, last_value]
        labels = ['Current Year', 'Last Year']

        # Calculate percentage difference
        percentage_diff = ((current_value - last_value) / last_value) * 100 if last_value != 0 else 0

        # Creating the bar chart
        fig, ax = self.create_figure()
        bars = ax.bar(labels, values, color=[self.color_scheme_bars['bars'],'#cb416b'])

        # Adding the value labels to the bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{value}', ha='center', va='bottom')

        # Adding percentage difference above the bars
        max_height = max(values) + 0.3 * max(values)
        ax.text(0.5, max_height, f'Percentage Difference: {percentage_diff:.2f}%\n'
                                 f'Total Sales From {current_dates[0]} To {current_dates[1]}: {current_value}'
                                 f'\nTotal Sales From {last_dates[0]} To {last_dates[1]}: {last_value}',
                                ha='center', va='bottom', fontsize=12, color='black')

        ax.set_title(f'{name} Comparison')
        ax.set_ylabel('Values')

        plt.tight_layout()

        return fig


visualisations = Visualisations()
