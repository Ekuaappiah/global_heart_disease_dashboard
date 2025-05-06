# Global-Heart-Disease-Visualisation-Project_Team1

This web-based interactive dashboard provides data visualizations and insights for exploring and analyzing global health and demographic data. Users can interact with various charts to understand trends in mortality rates, prevalence rates, and risk factors across countries and regions over time.

## Features

The dashboard contains 4 pages which different features

Overview Page

- Global Heart Disease Analytics Overview: Interactive summary of key statistics, including total countries analyzed, most recent year of data, and average mortality and prevalence rates.
  Key Metrics & Insights
- Total Countries Analyzed: Displays the number of countries and territories with heart disease data.
  Most Recent Year of Data: Shows the latest year for which data is available.
- Average Mortality Rate: Presents the average heart disease mortality rate (per 100,000 people).
- Average Prevalence Rate: Displays the average heart disease prevalence rate (per 100,000 people).
- Top 8 Countries by Metric: View the top 8 countries based on selected metrics such as Prevalence Rate, - **Mortality Rate, and Incidence Rate. Allows filtering by year for more granular analysis.
- Global GDP & Health Expenditure Trend: Visualize trends for GDP and health expenditure as a percentage of GDP over time.
- Life Expectancy & Health Expenditure Trends: Compare trends in life expectancy and health expenditure (% of GDP) over time.
- Risk Factor Analysis
- Global Risk Factors (Latest Year): Displays key risk factors such as Obesity Prevalence Rate, Physical Activity Rate, Alcohol Consumption, and Diabetes Prevalence Rate for the most recent year.
  Health Expenditure & Risk Factor Trends: Explore correlations between health expenditure and major risk factors, like obesity and physical inactivity, across different countries.
- Data Sources: A comprehensive list of authoritative global health and economic databases used in the analysis, including sources like WHO Global Health Observatory, World Bank, and Global Burden of Disease (GBD) Study.

Global Health Maps

- Interactive Visualizations: Explore a wide range of interactive charts, including choropleth maps, bar plots, and scatter plots to analyze global health data.
- Customizable Filters: Filter data by year, region, economic indicators, age group, and gender to view the most relevant insights.
- Economic Indicators: Display economic metrics such as GDP per capita and health expenditure alongside health outcomes for comprehensive analysis.
- Trend Analysis: Visualize trends with regression lines on scatter plots to analyze correlations between economic factors and health outcomes.
- Responsive Layout: Fully responsive design optimized for both desktop and mobile viewing, with adjustable chart sizes and interactive components.
- Real-Time Updates: Dynamic updates to visualizations based on user selections, providing real-time insights across different health and economic metrics.

Trend Analysis

- Prevalence Rate by Continent**: View the average prevalence rate by continent.
- Mortality Rate Over Time**: Analyze the trend of mortality rates over time by continent and age group.
- Mortality Rate by Country & Gender**: Compare mortality rates across countries and genders.
- Average Mortality per Country**: View the average mortality rate per country.
- Risk Factors Analysis by Region**: Visualize risk factors like alcohol consumption, diabetes prevalence, and obesity by country or continent.

Correlation Analysis

- Interactive Heatmap: Visualize correlations between multiple health metrics across countries and years.
- Scatter Plot: Explore relationships between selected health factors with dynamic axis selection.
- Sankey Diagram: Analyze the flow of risk factors impacting heart disease across continents and regions.
- Year and Country Filters: Filter data by year and country to focus on specific trends or regions.
- Dynamic Feature Selection: Choose from a wide range of health features for detailed visual analysis.
- Tooltip & Data Warnings: Get helpful tooltips and warnings for any missing or insufficient variance in the data.

## Installation
To run this app locally, follow these steps:

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/Ekuaappiah/global_heart_disease_dashboard.git
cd global_heart_disease_dashboard.git
```

### 2. Set Up a Virtual Environment

It’s recommended to use a virtual environment for Python projects:

```bash
python3 -m venv venv
source venv/bin/activate  # On Mac OS
source venv/Scripts/activate # On Windows
```

### 3. Install Dependencies

Install the required Python libraries using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Run the App

Once the dependencies are installed, you can run the app:

```bash
python main_dashboard.py
```

The app will be running on your local machine at `http://127.0.0.1:8050/`. Open this URL in your browser to access the dashboard.

## Usage

Find below a link to the User guide
User Guide Link = [(https://github.com/Ekuaappiah/global_heart_disease_dashboard#)]

## Screenshots of Dash App

You can view them here

## Dependencies

This project requires the following Python packages:

- **Dash**: Web framework for building the app.
- **Plotly**: Data visualization library.
- **Pandas**: Data manipulation and analysis library.
- **Flask**: Web server for Dash.
- **pycountry_convert**: Country to continent conversion.
- **dash-bootstrap-components**: Bootstrap components for Dash.

To install these dependencies, run:

```bash
pip install - r requirements
```

## Known Issues

- Large datasets may cause slight performance delays when loading.
- Currently, the app does not support multi-language options.
- There are a few minor UI tweaks needed for better mobile responsiveness.

## Roadmap

- **Multi-language support**: Add support for multiple languages in the UI.
- **Additional metrics**: Include more health metrics such as vaccination rates.
- **Improved performance**: Optimize the dashboard for large datasets.

## Contributing

We welcome contributions to this project! If you'd like to contribute, follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to your branch (`git push origin feature-branch`).
6. Open a Pull Request to merge your changes into the `main` branch.

Please ensure your code follows the Python style guide (PEP 8) and passes the linter.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- **Plotly**: For providing powerful and interactive charting capabilities.
- **Dash**: For making it easy to create interactive web apps with Python.
- **WHO (World Health Organization)**: Data source for health-related metrics used in the app.
- **GBD (GLobal Burden of Disease)**: Data source for risk factors and metric analysis data
- Special thanks to all the contributors who helped in making this project a reality!

## 👤 Author

**Emmanuella – Data Scientist**  
[LinkedIn](https://www.linkedin.com/in/emmanuella-appiah-16a215213) 

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---