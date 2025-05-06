from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import pycountry_convert as pc
from dash.dependencies import Input, Output

# Color schemes
BLUE_BLACK = "#17202A"
PREVALENCE_COLORS = ["#2980B9", "#1F618D", "#17202A", "#5499C7", "#2471A3"]
MORTALITY_COLORS = ["#154360", "#1F618D", "#17202A", "#5499C7", "#2980B9"]
AGE_GROUP_COLORS = ["#0B5345", "#117A65", "#148F77", "#1ABC9C", "#48C9B0"]
RISK_FACTOR_COLORS = ["#0B5345", "#117A65", "#148F77", "#1ABC9C", "#48C9B0"]

card_font = style={"fontWeight": "500","fontSize": "1.25rem", "textAlign": "center"}

# Layout function
def get_metric_analysis_layout(df):
    """
     Creates the layout for the metric analysis page of the dashboard.

     Args:
         df (pd.DataFrame): The main DataFrame containing heart disease metrics and related data

     Returns:
         dbc.Container: A Bootstrap container with the complete layout including:
             - Prevalence rate by continent visualization
             - Mortality rate over time analysis
             - Country and gender-specific mortality analysis
             - Average mortality per country visualization
             - Risk factor analysis by continent

     Note:
         The layout includes multiple interactive components with dropdowns for:
         - Year selection
         - Continent selection
         - Age group selection
         - Country selection
         - Gender selection
         - Risk factor selection
     """
    years = sorted(df['Year'].unique())
    continents = sorted(df['Region'].dropna().unique())
    countries = sorted(df['Country'].unique())
    age_groups = sorted(df['Age_Group'].unique())
    genders = ['Male', 'Female', 'Both']
    
    return dbc.Container([
        html.H3("Heart Disease Metric Analysis", className="text-center fw-semibold mb-3 p-3 rounded shadow-sm",
                style={"fontSize": "clamp(1.7rem, 4vw, 2.7rem)",
                       "background": "linear-gradient(135deg, #17202A 0%, #2C3E50 100%)", "color": "white"}),

        html.H5("Exploring Global Health Trends and Patterns 🔬", className="text-center mb-3 p-2 bg-light rounded shadow-sm",
                style={"fontSize": "clamp(1.6rem, 2vw, 1.8rem)",'border': '1px solid #dee2e6',}),

        dbc.Row([
            # Plot 1: Prevalence Rate by Continent
            dbc.Col(dbc.Card([dbc.CardHeader("Average Prevalence Rate by Continent", style=card_font),
                              dbc.CardBody([
                                  dcc.Dropdown(id='prevalence-year-dropdown',
                                               options=[{"label": str(year), "value": year} for year in years],
                                               value=years[0], clearable=False, className="mb-4"),
                                  dcc.Graph(id='prevalence-rate-continent',  style={"paddingBottom": "14px"})
                              ])], className="shadow-sm border"), width=12, lg=6, className="mb-4"),

            # Plot 2: Mortality Rate Over Time
            dbc.Col(dbc.Card([dbc.CardHeader("Mortality Rate Over Time", style=card_font ),
                              dbc.CardBody([
                                  dbc.Row([
                                      dbc.Col([
                                          html.Label("Select Continent:"),
                                          dcc.Dropdown(
                                              id='mortality-continent-dropdown',
                                              options=[{"label": cont, "value": cont} for cont in continents],
                                              value=continents[0],
                                              clearable=False
                                          )
                                      ], width=6),

                                      dbc.Col([
                                          html.Label("Select Age Group:"),
                                          dcc.Dropdown(
                                              id='mortality-age-dropdown',
                                              options=[{"label": age, "value": age} for age in age_groups],
                                              value=age_groups[0],
                                              clearable=False
                                          )
                                      ], width=6)
                                  ], className="mb-3"),

                                  dcc.Graph(id='age-grouped-mortality')
                              ])], className="shadow-sm border"), width=12, lg=6, className="mb-4"),
        ]),

        dbc.Row([
            # Plot 3: Mortality Rate by Country & Gender
            dbc.Col(dbc.Card([dbc.CardHeader("Mortality Rate by Country & Gender", style=card_font ),
                              dbc.CardBody([
                                  dcc.Dropdown(id='mortality-country-dropdown',
                                               options=[{"label": country, "value": country} for country in countries],
                                               value=countries[0], clearable=False),
                                  dcc.Dropdown(id='mortality-gender-dropdown',
                                               options=[{"label": gender, "value": gender} for gender in genders],
                                               value=genders[0], clearable=False),
                                  dcc.Graph(id='country-gender-mortality')
                              ])], className="shadow-sm border"), width=12, className="mb-4"),
        ]),

        dbc.Row([
            # Plot 4: Average Mortality Per Country
            dbc.Col(dbc.Card([dbc.CardHeader("Average Mortality Rate Per Country", style=card_font),
                              dbc.CardBody([
                                  dcc.Dropdown(id='average-mortality-year-dropdown', options=[{"label": str(year), "value": year}
                             for year in years], value=years[0], clearable=False),
                                  dcc.Graph(id='average-mortality-country')
                              ])], className="shadow-sm border"), width=12, className="mb-4"),
        ]),

        dbc.Row([
            # Plot 5: Risk Factor Analysis per ccontinent
            dbc.Col(dbc.Card([dbc.CardHeader("Risk Factors Analysis by Continent", style=card_font ),
                              dbc.CardBody([
                                  dcc.Dropdown(id='risk-factor-dropdown', options=[
                                      {"label": "Alcohol Value", "value": "Alcohol_Value"},
                                      {"label": "Diabetes Prevalence Rate", "value": "Diabetes_Prevalence_Rate"},
                                      {"label": "Activity Prevalence Rate", "value": "Activity_Prevalence_Rate"},
                                      {"label": "Obesity Prevalence Rate", "value": "Obesity_Prevalence_Rate"}
                                  ], value="Alcohol_Value", clearable=False),
                                  dcc.Graph(id='risk-factors-by-region-plot')
                              ])], className="shadow-sm border"), width=12, className="mb-4"),
        ]),
    ], fluid=True)

    # Step 2: Register callbacks for the Risk Factors Plot

def register_callbacks_metrics(app,df_main):
    """
       Registers all callbacks for the metric analysis page components.

       Args:
           app (dash.Dash): The Dash application instance
           df_main (pd.DataFrame): The main DataFrame containing all metrics data

       Note:
           This function sets up callbacks for:
           - Prevalence rate visualization updates
           - Age-grouped mortality rate updates
           - Country-gender mortality rate updates
           - Average mortality rate updates
           - Risk factor analysis updates
       """
    @app.callback(
        Output('prevalence-rate-continent', 'figure'),
        [Input('prevalence-year-dropdown', 'value')]
    )
    def update_prevalence_rate(year):
        """
               Updates the prevalence rate visualization based on selected year.

               Args:
                   year (int): Selected year for data visualization

               Returns:
                   plotly.graph_objects.Figure: Bar chart showing average prevalence rates by continent
               """
        df_filtered = df_main[df_main['Year'] == year]
        avg_prevalence = df_filtered.groupby(
            'Region')['PrevalenceRate'].mean().reset_index()
        return px.bar(avg_prevalence, x='Region', y='PrevalenceRate',
                      title=f'Average Prevalence Rate by Continent ({year})',
                      template='plotly_white', color='Region',
                      color_discrete_sequence=PREVALENCE_COLORS)

    @app.callback(
        Output('age-grouped-mortality', 'figure'),
        [Input('mortality-continent-dropdown', 'value'),
         Input('mortality-age-dropdown', 'value')]
    )

    def update_age_grouped_mortality(continent, age_group):
        """
              Updates the mortality rate visualization based on selected continent and age group.

              Args:
                  continent (str): Selected continent for filtering data
                  age_group (str): Selected age group for filtering data

              Returns:
                  plotly.graph_objects.Figure: Line chart showing mortality rate trends over time
              """
        df_filtered = df_main[(df_main['Region'] == continent) & (
            df_main['Age_Group'] == age_group)]
        mean_mortality = df_filtered.groupby(
            'Year')['MortalityRate'].mean().reset_index()
        return px.line(mean_mortality, x='Year', y='MortalityRate',
                       title=f'Mortality Rate Over Time in {continent} ({age_group})',
                       template='plotly_white', line_shape='spline',
                       color_discrete_sequence=MORTALITY_COLORS)
    
    @app.callback(
        Output('country-gender-mortality', 'figure'),
        [Input('mortality-country-dropdown', 'value'),
         Input('mortality-gender-dropdown', 'value')]
    )

    def update_country_gender_mortality(country, gender):
        """
                Updates the mortality rate visualization based on selected country and gender.

                Args:
                    country (str): Selected country for filtering data
                    gender (str): Selected gender ('Male', 'Female', or 'Both')

                Returns:
                    plotly.graph_objects.Figure: Line chart showing mortality rate trends by country and gender
                """
        df_filtered = df_main[(df_main['Country'] == country)
                              & (df_main['Gender'] == gender)]
        mean_mortality = df_filtered.groupby(
            'Year')['MortalityRate'].mean().reset_index()
        return px.line(mean_mortality, x='Year', y='MortalityRate',
                       title=f'Mortality Rate in {country} ({gender})',
                       template='plotly_white', line_shape='spline',
                       color_discrete_sequence=MORTALITY_COLORS)
    @app.callback(
        Output('average-mortality-country', 'figure'),
        [Input('average-mortality-year-dropdown', 'value')]
    )

    def update_average_mortality(year):
        """
            Updates the average mortality rate visualization based on selected year.

            Args:
                year (int): Selected year for data visualization

            Returns:
                plotly.graph_objects.Figure: Bar chart showing average mortality rates by country
            """
        df_filtered = df_main[df_main['Year'] == year]
        avg_mortality = df_filtered.groupby(['Country_Code', 'Country'])[
            'MortalityRate'].mean().reset_index()
        return px.bar(avg_mortality, x='Country_Code', y='MortalityRate',
                      title=f'Average Mortality Rate per Country ({year})',
                      template='plotly_white', color='MortalityRate',
                      color_continuous_scale=PREVALENCE_COLORS,
                      hover_data={'Country_Code': False, 'Country': True})
    @app.callback(
        Output('risk-factors-by-region-plot', 'figure'),
        [Input('risk-factor-dropdown', 'value')]
    )
    def update_risk_factors_plot(risk_factor):
        """
              Updates the risk factors visualization based on selected risk factor.

              Args:
                  risk_factor (str): Selected risk factor for analysis ('Alcohol_Value',
                                   'Diabetes_Prevalence_Rate', 'Activity_Prevalence_Rate',
                                   or 'Obesity_Prevalence_Rate')

              Returns:
                  plotly.graph_objects.Figure: Bar chart showing average risk factor values by continent

              Note:
                  Includes hover data showing country-specific information for each continent
              """
        if risk_factor not in df_main.columns:
            return px.bar(title="Invalid Selection - No Data Available")
        df_main[risk_factor] = pd.to_numeric(
            df_main[risk_factor], errors='coerce')
        # Selecting only necessary columns and dropping missing values
        df_filtered = df_main[['Region', 'Country', risk_factor]].dropna()
        # Group data by Continent but keep Country values for hover
        grouped_df = df_filtered.groupby(['Region', 'Country'], as_index=False)[risk_factor].mean()
        return px.bar(
            grouped_df,
            x="Region",
            y=risk_factor,
            title=f'Average {risk_factor.replace("_", " ")} by Continent',
            template='plotly_white',
            color="Region",
            color_discrete_sequence=RISK_FACTOR_COLORS,
            hover_data={"Country": True}  # Show country names on hover
        )
