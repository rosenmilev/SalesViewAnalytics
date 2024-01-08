from data.data_extraction.query_manager import QueryGenerator, DataExtractor
from visualisations.visualisation_manager import Visualisations


class Reports:
    def __init__(self):
        self.query_gen = QueryGenerator()
        self.data_extractor = DataExtractor()

        # Determine variables used by GUI dashboard in order to use them in different screens of the gui application
        self.current_date = ''
        self.first_day_of_current_month = ''

        self.current_month_sales = ''
        self.current_month_today_sales = ''
        self.current_month_customer_count = ''
        self.current_month_average_sales_by_client = ''
        self.current_month_average_sales_by_order = ''

        # Update all the variables with latest data
        self.generate_dashboard_info()

    # With the data from GUI app widgets, fill with params of dynamic query generator(QueryGenerator class)
    def generate_report(self, query_params):
        # Assume these are fetched from the GUI
        start_date = query_params['start_date']
        end_date = query_params['end_date']
        include_segment = query_params['include_segment']
        include_customer = query_params['include_customer']
        include_region = query_params['include_region']
        include_product = query_params['include_product']

        self.query_gen.set_date_range(start_date, end_date)

        if include_segment:
            self.query_gen.add_segment()
        else:
            self.query_gen.remove_segment()

        if include_customer:
            self.query_gen.add_customer()
        else:
            self.query_gen.remove_customer()
        if include_region:
            self.query_gen.add_region()
        else:
            self.query_gen.remove_region()
        if include_product:
            self.query_gen.add_product()
        else:
            self.query_gen.remove_product()

        result = self.query_gen.generate_query(
            include_segment=include_segment,
            include_customer=include_customer,
            include_region=include_region,
            include_product=include_product
        )

        return result

    # Generate dynamically information for dashboard,
    # based on the current date(which is determined by last sales record date)
    def generate_dashboard_info(self):
        self.current_date = self.data_extractor.determine_current_date()[0][0]
        current_year, current_month, current_day = self.current_date.split("-")
        self.first_day_of_current_month = f"{current_year}-{current_month}-01"
        self.current_month_today_sales = self.data_extractor.sales_for_period(self.current_date, self.current_date)[0][0]
        self.current_month_sales = self.data_extractor.sales_for_period(self.first_day_of_current_month, self.current_date)[0][0]
        self.current_month_customer_count = self.data_extractor.customer_count_for_period(self.first_day_of_current_month, self.current_date)[0][0]
        self.current_month_average_sales_by_client = round(self.current_month_sales / self.current_month_customer_count, 2)
        self.current_month_average_sales_by_order = round(self.current_month_sales / self.data_extractor.order_count_for_period(self.first_day_of_current_month, self.current_date)[0][0])

        return self.current_date


class Analytics:
    def __init__(self):
        self.data_extractor = DataExtractor()
        self.visualisations = Visualisations()
        self.data_provider = reports

    # start_date, end_date, selection_type, selection
    def generate_result(self, params):
        result_current = self.data_extractor.daily_sales(params[0], params[1], params[2], params[3])
        start_date_last_year = params[0].replace('2018', '2017')
        end_date_last_year = params[1].replace('2018', '2017')

        result_last = self.data_extractor.daily_sales(start_date_last_year, end_date_last_year, params[2], params[3])

        total_current = round(sum([daily[1] for daily in result_current]), 2)
        total_last = round(sum([daily[1] for daily in result_last]), 2)

        if params[2] == 'od.product_id':
            figure = self.visualisations.vis_two_items(total_current, total_last, f'Product: {params[3]}',
                                                       (params[0], params[1]),
                                                       (start_date_last_year, end_date_last_year))
        elif params[2] == 'c.segment':
            figure = self.visualisations.vis_two_items(total_current, total_last, f'Segment: {params[3]}',
                                                       (params[0], params[1]),
                                                       (start_date_last_year, end_date_last_year))
        elif params[2] == 'st.region':
            figure = self.visualisations.vis_two_items(total_current, total_last, f'Region: {params[3]}',
                                                       (params[0], params[1]),
                                                       (start_date_last_year, end_date_last_year))

        return result_current, result_last, figure




reports = Reports()
analytics = Analytics()
