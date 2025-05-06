import plotly.express as px
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Tooltip style
tooltip_style = {
    "color": "white",
    "backgroundColor": "#333",
    "borderRadius": "5px",
    "padding": "8px",
    "fontSize": "14px"
}

def create_choropleth(df, year, continent, metric, age_group, gender, economic_indicator=None):
    """
        Creates a choropleth map visualization of health or economic metrics by country.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing country-level data with columns for Year, Region, Country_Code,
            Age_Group, Gender, and various metrics (MortalityRate, IncidenceRate, PrevalenceRate, GDP, etc.)
        year : int
            The year to filter data for
        continent : str
            The continent/region to filter for ("All" or specific continent name)
        metric : str
            The health metric to visualize ('MortalityRate', 'IncidenceRate', or 'PrevalenceRate')
        age_group : str
            Age group to filter for ('Age-standardized' or specific age group)
        gender : str
            Gender to filter for ('All', 'Male', or 'Female')
        economic_indicator : str, optional
            Economic metric to visualize instead of health metric ('GDP' or 'Health_Expenditure (% of GDP)')

        Returns
        -------
        plotly.graph_objects.Figure
            A choropleth map figure object with hover tooltips and customized styling
        """
    filtered_df = df[df['Year'] == year]
    if continent != "All":
        filtered_df = filtered_df[filtered_df['Region'] == continent]
    if age_group != "Age-standardized":
        filtered_df = filtered_df[filtered_df['Age_Group'] == age_group]
    if gender != "All":
        filtered_df = filtered_df[filtered_df['Gender'] == gender]

    metric_labels = {
        'MortalityRate': 'Mortality Rate (per 100,000)',
        'IncidenceRate': 'Incidence Rate (per 100,000)',
        'PrevalenceRate': 'Prevalence Rate (per 100,000)',
        'GDP': 'GDP per Capita (USD)',
        'Health_Expenditure (% of GDP)': 'Healthcare Expenditure (% of GDP)'
    }

    if economic_indicator and economic_indicator != 'None':
        selected_metric = economic_indicator
        color_scale = 'Pubu'
    else:
        selected_metric = metric
        color_scale = 'Gnbu'

    continent_scope_mapping = {
        'North America': 'north america',
        'South America': 'south america',
        'Europe': 'europe',
        'Asia': 'asia',
        'Oceania': 'world',
        'Africa': 'africa',
        'All': 'world'
    }

    # Updated hover text with lighter styling and better spacing
    filtered_df = filtered_df.copy() # Avoiding SettingWithCopyWarning
    filtered_df.loc[:, 'Hover_Text'] = filtered_df.apply(
        lambda row: (
            f"<span style='font-family: Arial, sans-serif;'>"
            f"<span style='font-size: 16px; color: #2c3e50; font-weight: 600;'>{row['Country']}</span><br><br>"
            f"<span style='color: #7f8c8d; font-size: 12px;'>📅 Year:</span> "
            f"<span style='color: #3498db; font-weight: 500;font-size: 12px;'>{year}</span><br>"
            f"<span style='color: #7f8c8d; font-size: 12px;'>📊 {metric_labels[selected_metric]}:</span> "
            f"<span style='color: #27ae60; font-weight: 500; font-size: 12px;'"
            f">{row[selected_metric]:,.2f}</span><br>"
            + (f"<span style='color: #7f8c8d; font-size: 12px;'>💰 GDP:</span> "
               f"<span style='font-size: 12px; color: #e67e22; font-weight: 500;'>${row['GDP']:,.2f}</span><br>"
               if ('GDP' in filtered_df.columns and pd.notna(row['GDP']) and
                   selected_metric != 'GDP') else "")
            + (f"<span style='color: #7f8c8d; font-size: 12px;'>🏥 Health Expenditure:</span> "
               f"<span style='color: #e74c3c; font-weight: 500; font-size: 12px;'"
               f">{row['Health_Expenditure (% of GDP)']:,.2f}%</span>"
               if ('Health_Expenditure (% of GDP)' in filtered_df.columns and
                   pd.notna(row['Health_Expenditure (% of GDP)']) and
                   selected_metric != 'Health_Expenditure (% of GDP)') else "")
            + "</span>"
        ),
        axis=1
    )

    fig = px.choropleth(
        filtered_df,
        locations='Country_Code',
        color=selected_metric,
        hover_name=None,
        hover_data={'Hover_Text': True, 'Country_Code': False},
        custom_data=['Hover_Text'],  # Add custom data for hover template
        color_continuous_scale=color_scale,
        title=f'{metric_labels.get(selected_metric, selected_metric)} Distribution ({year})'
    )

    # Update hover template to use custom hover text
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>"
    )

    fig.update_layout(
        autosize=True,
        margin={"r": 10, "t": 80, "l": 10, "b": 10},
        coloraxis_colorbar=dict(
            title=f"{selected_metric.replace('_', ' ').title()} (%)",
            x=1.05,
            len=0.6,
            thickness=20
        ),
        geo=dict(
            showframe=False,
            projection_type='natural earth',
            projection_scale=1.2,
            scope=continent_scope_mapping.get(continent, 'world')
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            bordercolor="#e5e5e5",
            font_family="Arial, sans-serif"
        )
    )

    return fig


def create_barplot(df, year, continent, metric, age_group, gender):
    """
       Creates a horizontal bar plot showing top 10 countries for a selected health metric.

       Parameters
       ----------
       df : pandas.DataFrame
           DataFrame containing country-level data with columns for Year, Region, Country,
           Age_Group, Gender, and various health metrics
       year : int
           The year to filter data for
       continent : str
           The continent/region to filter for ("All" or specific continent name)
       metric : str
           The health metric to visualize ('MortalityRate', 'IncidenceRate', or 'PrevalenceRate')
       age_group : str
           Age group to filter for ('Age-standardized' or specific age group)
       gender : str
           Gender to filter for ('All', 'Male', or 'Female')

       Returns
       -------
       plotly.graph_objects.Figure
           A horizontal bar plot figure showing the top 10 countries for the selected metric
       """
    filtered_df = df[df['Year'] == year]
    if continent != "All":
        filtered_df = filtered_df[filtered_df['Region'] == continent]
    if age_group != "Age-standardized":
        filtered_df = filtered_df[filtered_df['Age_Group'] == age_group]
    if gender != "All":
        filtered_df = filtered_df[filtered_df['Gender'] == gender]

    # Ensure data is available
    if filtered_df.empty:
        return px.bar(
            title=f'No data available for selected filters',
            labels={'x': 'Country', 'y': metric}
        )

    # Handle NaN values and sorting
    top_10_countries = (
        filtered_df.dropna(subset=[metric])
        .nlargest(10, metric)[['Country', metric, 'Region', 'GDP']]
        # Sort in ascending order for better bar chart visualization
        .sort_values(metric, ascending=True)
    )

    # Create custom hover text with rich formatting
    top_10_countries['hover_text'] = top_10_countries.apply(
        lambda row: (
            f"<span style='font-family: Arial, sans-serif; font-size: 16px;'>"
            f"<b style='color: #2c3e50;'>{row['Country']}</b><br><br>"
            f"<span style='color: #7f8c8d;'>🌐 Region:</span> "
            f"<span style='color: #3498db; font-weight: bold;'>{row['Region']}</span><br>"
            f"<span style='color: #7f8c8d;'>📊 {metric.replace('_', ' ').title()}:</span> "
            f"<span style='color: #27ae60; font-weight: bold;'>{row[metric]:,.2f}</span><br>"
            f"<span style='color: #7f8c8d;'>💰 GDP per capita:</span> "
            f"<span style='color: #e67e22; font-weight: bold;'>${row['GDP']:,.2f}</span>"
            "</span>"
        ),
        axis=1
    )

    # Enhanced bar plot with more styling
    fig = px.bar(
        top_10_countries,
        x=metric,
        y='Country',
        orientation='h',
        color='Country',
        custom_data=['hover_text'],  # Add custom hover data
        title=f'Top 10 Countries - {metric.replace("_", " ").title()} ({year})'
    )

    fig.update_traces(
        # Use custom hover text
        hovertemplate='%{customdata[0]}<extra></extra>',
    )

    fig.update_layout(
        height=700,
        title_x=0.5,
        xaxis_title=f'{metric.replace("_", " ").title()}',
        yaxis_title='Country',
        bargap=0.2,
        template='plotly_white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Arial, sans-serif",
            bordercolor="#e5e5e5"
        )
    )

    return fig


def create_scatter_plot(df, year, continent, metric, economic_indicator, age_group, gender):
    """
        Creates a scatter plot to visualize correlation between health metrics and economic indicators.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing country-level data with health and economic indicators
        year : int
            The year to filter data for
        continent : str
            The continent/region to filter for ("All" or specific continent name)
        metric : str
            The health metric for y-axis ('MortalityRate', 'IncidenceRate', or 'PrevalenceRate')
        economic_indicator : str
            The economic indicator for x-axis ('GDP' or 'Health_Expenditure (% of GDP)')
        age_group : str
            Age group to filter for ('Age-standardized' or specific age group)
        gender : str
            Gender to filter for ('All', 'Male', or 'Female')

        Returns
        -------
        plotly.graph_objects.Figure
            A scatter plot figure with trend line showing correlation between selected metrics
        """
    # Filter data based on user selections
    filtered_df = df[df['Year'] == year]
    if continent != "All":
        filtered_df = filtered_df[filtered_df['Region'] == continent]
    if age_group != "Age-standardized":
        filtered_df = filtered_df[filtered_df['Age_Group'] == age_group]
    if gender != "All":
        filtered_df = filtered_df[filtered_df['Gender'] == gender]

    # Ensure data is available and drop NaNs
    filtered_df = filtered_df.dropna(subset=[metric, economic_indicator])

    if filtered_df.empty:
        return px.scatter(title=f"No data available for selected filters")

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x=economic_indicator,
        y=metric,
        color="Region",
        hover_name="Country",
        title=f'Correlation: {economic_indicator.replace("_", " ")} vs {metric.replace("_", " ")} ({year})',
        trendline="ols",  # Ordinary Least Squares (OLS) regression line
        labels={
            economic_indicator: economic_indicator.replace("_", " ").title(),
            metric: metric.replace("_", " ").title()
        }
    )

    # Improve layout
    fig.update_layout(
        height=700,
        title_x=0.5,
        template='plotly_white',
        xaxis_title=f"{economic_indicator.replace('_', ' ')}",
        yaxis_title=f"{metric.replace('_', ' ')}",
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial, sans-serif",
            bordercolor="#e5e5e5"
        )
    )

    return fig


def get_choropleth_layout(df):
    """
        Creates the main layout for the choropleth visualization dashboard.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing the full dataset used for creating filter options
            and initializing default values

        Returns
        -------
        dash.html.Div
            A Div component containing the complete dashboard layout with:
            - Title and subtitle
            - Filter dropdowns (region, year, metric, economic indicator, age group, gender)
            - Choropleth map
            - Economic indicator map (conditionally rendered)
            - Scatter plot (conditionally rendered)
            - Bar plot
            All components are responsive and include tooltips for user guidance.
        """
    starting_year = df['Year'].min()

    dropdown_style = {
        'className': 'responsive-dropdown fw-bold mb-2',
        'clearable': False
    }

    return html.Div([
            html.H3(
        [
            "Heart Disease Atlas ",
           
        ],
            className="text-center fw-semibold mb-3 p-3 rounded shadow-sm",
            style={
                "fontSize": "clamp(1.7rem, 4vw, 2.7rem)",
                "marginBottom": "1rem",
                "background": "linear-gradient(135deg, #17202A 0%, #2C3E50 100%)",
                "color": "white",
                "fontFamily": "'Segoe UI', system-ui, -apple-system, sans-serif",
                "lineHeight": "1.4"
            }
        ),

        # Subtitle with icons
        html.H5([
            "Exploring the Relationship Between Economic Factors and Heart Health Outcomes Worldwide ",
        ],
            className="text-center text-muted mb-3",
            style={
                "fontSize": "clamp(1rem, 2vw, 1.25rem)",
                "fontWeight": "normal",
                "lineHeight": "1.3"
            }
        ),

        dbc.Card(
            dbc.CardBody(
                dbc.Row([
                    # First Row: 3 Columns
                    dbc.Col([
                        html.Label("Select Region", className="fw-bold mb-2"),
                        html.Span("ⓘ", id="region-tooltip",
                                  style={"cursor": "pointer", "marginLeft": "8px", "fontSize": "18px",
                                         "color": "#0d6efd"}),
                        dbc.Tooltip("Choose a region to filter data geographically.", target="region-tooltip",
                                    placement="right", style=tooltip_style),
                        dcc.Dropdown(
                            id='continent-dropdown',
                            options=[{'label': 'All', 'value': 'All'}] +
                            [{'label': region, 'value': region}
                                for region in df['Region'].unique()],
                            value='All',
                            **dropdown_style
                        ),
                    ], xs=12, sm=12, md=4, lg=4, xl=4),

                    dbc.Col([
                        html.Label("Select Year", className="fw-bold mb-2"),
                        html.Span("ⓘ", id="year-tooltip",
                                  style={"cursor": "pointer", "marginLeft": "8px", "fontSize": "18px",
                                         "color": "#0d6efd"}),
                        dbc.Tooltip("Select the year of interest for the data.", target="year-tooltip",
                                    placement="right", style=tooltip_style),
                        dcc.Dropdown(
                            id='year-dropdown',
                            options=[{'label': str(year), 'value': year}
                                     for year in sorted(df['Year'].unique())],
                            value=starting_year,
                            **dropdown_style
                        ),
                    ], xs=12, sm=12, md=4, lg=4, xl=4),

                    dbc.Col([
                        html.Label("Select Health Metric",
                                   className="fw-bold mb-2"),
                        html.Span("ⓘ", id="metric-tooltip",
                                  style={"cursor": "pointer", "marginLeft": "8px", "fontSize": "18px",
                                         "color": "#0d6efd"}),
                        dbc.Tooltip("Select a health-related metric for visualization.", target="metric-tooltip",
                                    placement="right", style=tooltip_style),
                        dcc.Dropdown(
                            id='metric-dropdown',
                            options=[
                                {'label': 'Mortality Rate',
                                    'value': 'MortalityRate'},
                                {'label': 'Incidence Rate',
                                    'value': 'IncidenceRate'},
                                {'label': 'Prevalence Rate',
                                    'value': 'PrevalenceRate'}
                            ],
                            value='PrevalenceRate',
                            **dropdown_style
                        ),
                    ], xs=12, sm=12, md=4, lg=4, xl=4),

                    # Second Row: 3 Columns
                    dbc.Col([
                        html.Label("Select Economic Indicator",
                                   className="fw-bold mb-2"),
                        html.Span(
                            "ⓘ",
                            id="econ-tooltip",
                            style={"cursor": "pointer", "marginLeft": "8px",
                                   "fontSize": "18px", "color": "#0d6efd"}
                        ),
                        dbc.Tooltip(
                            "Selecting an economic indicator will replace the health metric map with the chosen economic data.",
                            target="econ-tooltip",
                            placement="right",
                            style=tooltip_style
                        ),
                        dcc.Dropdown(
                            id='economic-indicator-dropdown',
                            options=[
                                {'label': 'None', 'value': 'None'},
                                {'label': 'GDP per capita', 'value': 'GDP'},
                                {'label': 'Health Expenditure (% of GDP)',
                                 'value': 'Health_Expenditure (% of GDP)'}
                            ],
                            value='None',
                            **dropdown_style
                        ),
                    ], xs=12, sm=12, md=4, lg=4, xl=4),

                    dbc.Col([
                        html.Label("Select Age Group",
                                   className="fw-bold mb-2"),
                        html.Span(
                            "ⓘ",
                            id="age-group-tooltip",
                            style={"cursor": "pointer", "marginLeft": "8px",
                                   "fontSize": "18px", "color": "#0d6efd"}
                        ),
                        dbc.Tooltip(
                            "Select an age group to filter data accordingly. 'Age-standardized' includes all age groups.",
                            target="age-group-tooltip",
                            placement="right",
                            style=tooltip_style
                        ),
                        dcc.Dropdown(
                            id='age-group-dropdown',
                            options=[{'label': age, 'value': age} for age in sorted(df['Age_Group'].unique()) if
                                     age != 'No Age Group'],
                            value='Age-standardized',
                            **dropdown_style
                        ),
                    ], xs=12, sm=12, md=4, lg=4, xl=4),

                    dbc.Col([
                        html.Label("Select Gender", className="fw-bold mb-2"),
                        html.Span(
                            "ⓘ",
                            id="gender-tooltip",
                            style={"cursor": "pointer", "marginLeft": "8px",
                                   "fontSize": "18px", "color": "#0d6efd"}
                        ),
                        dbc.Tooltip(
                            "Choose 'All' for both genders or filter by 'Male' or 'Female'.",
                            target="gender-tooltip",
                            placement="right",
                            style=tooltip_style
                        ),
                        dcc.Dropdown(
                            id='gender-dropdown',
                            options=[
                                {'label': 'All', 'value': 'All'},
                                {'label': 'Female', 'value': 'Female'},
                                {'label': 'Male', 'value': 'Male'}
                            ],
                            value='All',
                            **dropdown_style
                        ),
                    ], xs=12, sm=12, md=4, lg=4, xl=4),
                ], className="g-3"),
            ),
            className='bg-light border rounded p-3 shadow-sm mb-4'
        ),

        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='choropleth-map',
                    style={
                        'width': '100%',
                        'min-height': '700px',
                        'max-height': '800px',
                        'height': 'clamp(700px, 50vh, 800px)',
                        'overflow': 'hidden',
                        'margin-bottom': '1.4rem'
                    }
                ),
                # Economic map container with conditional rendering
                html.Div(
                    [
                        html.H4("Economic Indicator Map",
                                className="text-center mb-3"),
                        dcc.Loading(
                            id="loading-economic-map",
                            type="default",
                            children=[
                                dcc.Graph(
                                    id='economic-choropleth-map',
                                    style={
                                        'width': '100%',
                                        'min-height': '700px',
                                        'height': '800px',
                                        'overflow': 'hidden'
                                    }
                                )
                            ]
                        )
                    ],
                    id='economic-map-container',
                    style={'display': 'none'}
                ),
                # SACTTER PLOT
                dcc.Graph(
                    id='scatter-plot',
                    style={
                        'width': '100%', 'height': 'clamp(700px, 50vh, 800px)', 'display': 'none'}
                ),
                html.Div(
                    [
                        html.Hr(),
                        html.H4("Scatter Plot", className="text-center mb-3"),
                        dcc.Loading(
                            id="loading-scatter-plot",
                            type="default",
                            children=[
                                dcc.Graph(
                                    id='scatter-plot',
                                    style={
                                        'width': '100%',
                                        'min-height': '500px',
                                        'height': '600px',
                                        'overflow': 'hidden'
                                    }
                                )
                            ]
                        )
                    ],
                    id='scatter-container',
                    style={'display': 'none'}
                )

            ], xs=12, sm=12, md=12, lg=12, xl=12)
        ], className="mb-2"),

        html.Hr(),

        # Bar plot with responsive sizing
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='bar-plot',
                    style={'width': '100%',
                           'height': 'clamp(700px, 50vh, 800px)'}
                )
            ], xs=12, sm=12, md=12, lg=12, xl=12)
        ])
    ])


# Supplementary CSS to enhance responsiveness
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    {
        'href': 'assets/custom-responsive.css',
        'rel': 'stylesheet'
    }
]


def register_choropleth_callbacks(app, df):
    """
    Registers callback functions for the choropleth dashboard's interactive elements.

    Parameters
    ----------
    app : dash.Dash
        The Dash application instance
    df : pandas.DataFrame
        DataFrame containing the full dataset used for creating visualizations

    Notes
    -----
    This function sets up callbacks that:
    - Update the choropleth map based on selected filters
    - Update the economic indicator map when an economic metric is selected
    - Update the bar plot based on selected filters
    - Update the scatter plot when comparing health and economic metrics
    - Control visibility of economic map and scatter plot containers
    All callbacks are triggered by changes to any dropdown selection.
    """
    @app.callback(
        [Output("choropleth-map", "figure"),
         Output("economic-choropleth-map", "figure"),
         Output("economic-map-container", "style"),
         Output("bar-plot", "figure"),
         Output('scatter-plot', 'figure'),
         Output("scatter-container", "style")],
        [Input("year-dropdown", "value"),
         Input("continent-dropdown", "value"),
         Input("metric-dropdown", "value"),
         Input("economic-indicator-dropdown", "value"),
         Input("age-group-dropdown", "value"),
         Input("gender-dropdown", "value")],
        prevent_initial_call=False
    )
    def update_plots(year, continent, metric, economic_indicator, age_group, gender):
        # Set default values
        year = year or df['Year'].min()
        continent = continent or 'All'
        metric = metric or 'PrevalenceRate'
        age_group = age_group or 'Age-standardized'
        gender = gender or 'Both'

        # Create the primary health metric choropleth and bar plot
        choropleth_fig = create_choropleth(
            df, year, continent, metric, age_group, gender)
        bar_fig = create_barplot(
            df, year, continent, metric, age_group, gender)

        # Default hidden styles for economic maps and scatter plot
        economic_map_style = {'display': 'none'}
        scatter_plot_style = {'display': 'none'}

        # Placeholder figures
        economic_choropleth_fig = px.choropleth(
            title='Select an Economic Indicator')
        scatter_fig = px.scatter(title="Select an Economic Indicator")

        # Show economic choropleth and scatter plot if an economic indicator is selected
        if economic_indicator and economic_indicator != 'None':
            economic_choropleth_fig = create_choropleth(
                df, year, continent, metric, age_group, gender, economic_indicator)
            economic_map_style = {'display': 'block'}
            scatter_plot_style = {'display': 'block'}

            scatter_fig = px.scatter(
                df[df['Year'] == year],
                x=economic_indicator,
                y=metric,
                color="Region",
                size="Population" if "Population" in df.columns else None,
                hover_name="Country",
                title=f"{metric} vs {economic_indicator} ({year})"
            )

        return choropleth_fig, economic_choropleth_fig, economic_map_style, bar_fig, scatter_fig, scatter_plot_style
