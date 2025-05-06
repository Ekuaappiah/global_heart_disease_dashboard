import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd 
import numpy as np
import pycountry_convert as pc
import orjson


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True


# Tooltip style
tooltip_style = {
    "color": "white",
    "backgroundColor": "#333",
    "borderRadius": "5px",
    "padding": "8px",
    "fontSize": "14px"
}


custom_continent_map = {

    "Asia": ["Democratic Republic of Timor-Leste", "Republic of Turkey",'Lao PDR'],
    "Africa": ["Cote d'Ivoire", 'Guinea Bissau', 'Republic of Rwanda',
       'Republic of Sudan'],
}


def get_correlation_layout(corr_data):
    """
        Creates the layout for the correlation analysis page of the dashboard.

        Returns:
            dbc.Container: A Bootstrap container containing the complete layout including:
                - Title and subtitle
                - Filter section (year and country selectors)
                - Correlation heatmap with feature selection
                - Scatter plot with x and y axis feature selection
                - Sankey diagram with target feature selection
        """
    return dbc.Container([
        html.H1(
    ["Heart Disease Risk Factor Explorer ",
        ],
            className="text-center fw-semibold mb-3 p-3 rounded shadow-sm",
            style={
                "fontSize": "clamp(1.7rem, 4vw, 2.7rem)",
                "marginBottom": "1rem",
                "background": "linear-gradient(135deg, #17202A 0%, #2C3E50 100%)",
                "color": "white",
                "fontFamily": "'Segoe UI', system-ui, -apple-system, sans-serif",
                "lineHeight": "1.4"
            }),
        # Subtitle with icons
        html.H5([
            "Unveiling Correlations in Global Health Metrics ",
        ],
            className="text-center mb-3 p-2 bg-light rounded shadow-sm",
            style={"fontSize": "clamp(1.6rem, 2vw, 1.8rem)", 'border': '1px solid #dee2e6',}),
        
        dbc.Col([

            dbc.Row([

                # Left Column: Filters
                dbc.Col([
                    html.H5("Filters", style={'textAlign': 'center'}),

                    # Year Selector
                    html.Label("Select Year:", className="mb-2 fw-medium"),
                    dcc.Dropdown(
                        id='year-dropdown-corr',
                        options=[{'label': 'All', 'value': 'All'}] +
                                [{'label': year, 'value': year} for year in sorted(corr_data['Year'].unique())],
                        value='All',
                        placeholder="Select year",
                        className="mb-4"
                    ),

                    # Country Selector
                    html.Label("Select Countries:", className="mb-2 fw-medium"),
                    dcc.Dropdown(
                        id='country-dropdown-corr',
                        options=[{'label': 'All', 'value': 'All'}] +
                                [{'label': country, 'value': country} for country in
                                 sorted(corr_data['Country'].unique())],
                        value='All',
                        placeholder="Select one or more countries"
                    ),

                ], width=3, style={
                    'padding': '20px',
                    'borderRadius': '12px',
                    'border': '1px solid #dee2e6',
                    'backgroundColor': '#f8f9fa',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'  ,
                    "marginBottom": "30px"
                }),

                # Right Column: Visualizations
                dbc.Col([
                    html.H5("Feature Correlation Heatmap", style={'textAlign': 'left', 'marginBottom': '10px'}),
                    html.Label("Select Features "),
                    html.Span("ⓘ", id="metric-tooltip",
                                  style={"cursor": "pointer", "marginLeft": "5px", "fontSize": "18px",
                                         "color": "#0d6efd"}),
                        dbc.Tooltip("Select two or more features for the heatmap.", target="metric-tooltip",
                                    placement="right", style=tooltip_style),
                    dcc.Dropdown(
                        id='heatmap-dropdown',
                        options=[{"label": "Select All", "value": "All"}] +[{'label': col, 'value': col} for col in corr_data.columns if col not in ['Country', 'Year', 'Age_Group', 'Gender', 'Region']] ,
                        value=[corr_data.columns[2], corr_data.columns[3]],  # Default selection
                        multi=True,
                        placeholder="Select features for heatmap"
                    ),
                    dcc.Loading(
                            id="loading-heatmap",
                            type="default",
                            children=[
                                dcc.Graph(id='heatmap'),
                            ]),
                        
                    html.H5("Feature Scatterplot", style={'textAlign': 'left', 'marginBottom': '10px'}),
                    dcc.Dropdown(
                        id='scatter-dropdown-x',
                        options=[{'label': col, 'value': col} for col in corr_data.columns if col not in ['Country', 'Year', 'Age_Group', 'Gender', 'Region']],
                        placeholder="Select X-axis feature"
                    ),
                    dcc.Dropdown(
                        id='scatter-dropdown-y',
                        options=[{'label': col, 'value': col} for col in corr_data.columns if col not in ['Country', 'Year', 'Age_Group', 'Gender', 'Region']],
                        placeholder="Select Y-axis feature"
                    ),
                    dcc.Loading(
                            id="loading-scatterplot",
                            type="default",
                            children=[

                                dcc.Graph(id='scatterplot-corr'),
                            ])
                
                    
                ], width=9)
            ]),
            
            html.H5("Feature Sankey Diagram", style={'textAlign': 'left', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='sankey-dropdown',
                options=[{'label': col, 'value': col} for col in corr_data.columns if col in ['PrevalenceRate', 'MortalityRate', 'IncidenceRate']],
                value="PrevalenceRate",
                placeholder="Select target feature"
            ),
            dcc.Loading(
                            id="loading-sankey",
                            type="default",
                            children=[

                                dcc.Graph(id="sankey-diagram", style={'height': '600px'}),
                            ]),
            
        ])
    ], fluid=True)



def register_callbacks_corr(app, data, corr_data, cache):
    """
       Registers all callbacks for the correlation analysis page.

       Args:
           app (dash.Dash): The Dash application instance
           cache (Cache): Flask-Cache instance for memoizing computations

       Note:
           This function sets up the interactive functionality for:
           - Heatmap feature selection and visualization
           - Scatter plot feature selection and visualization
           - Sankey diagram updates
           - Filter applications
       """
    @cache.memoize()
    def sankey_data_prep(data):
        """
        Prepares data for the Sankey diagram by adding region information to the dataset.

        Args:
            data (pd.DataFrame): Input DataFrame containing country information

        Returns:
            pd.DataFrame: DataFrame with added 'Region' column mapping countries to their continental regions
        """
        def get_region(country_name):
            """
                   Maps a country name to its continental region using pycountry_convert.

                   Args:
                       country_name (str): Name of the country

                   Returns:
                       str: Continent name or np.nan if mapping fails
            """
            try:
                country_code = pc.country_name_to_country_alpha2(country_name, cn_name_format="default")
                continent_code = pc.country_alpha2_to_continent_code(country_code)

                #separating Americas if needed:
                if continent_code == 'NA':
                    return 'North America'
                elif continent_code == 'SA':
                    return 'South America'
                else:
                    return pc.convert_continent_code_to_continent_name(continent_code)

            except KeyError:
                return np.nan #handling cases where country code is not found
            
        def get_custom_region(country_name):
            """
                    Maps countries to regions using custom mapping for cases not covered by pycountry_convert.

                    Args:
                        country_name (str): Name of the country

                    Returns:
                        str: Region name from custom mapping or np.nan if not found
            """
            for region, countries in custom_continent_map.items():
                if country_name in countries:
                    return region
            return np.nan  # Keep existing values unchanged

        data['Region'] = data['Country'].apply(get_region)
        # Only replace NaN values in the 'Region' column
        data["Region"] = data["Region"].fillna(data["Country"].map(get_custom_region))
        return data

    @cache.memoize()
    def create_sankey(trgt):
        """
           Creates a Sankey diagram showing relationships between risk factors, regions, and target health metric.

           Args:
               trgt (str): Target variable name ('PrevalenceRate', 'MortalityRate', or 'IncidenceRate')

           Returns:
               go.Figure: Plotly figure object containing the Sankey diagram
           """
        df = sankey_data_prep(data)

        # Pre-calculate all quartiles at once using a dictionary comprehension
        columns_to_categorize = {
            'Alcohol_Value': 'Alcohol Level',
            'Obesity_Prevalence_Rate': 'Obesity Level',
            'Diabetes_Prevalence_Rate': 'Diabetes Level',
            'Activity_Prevalence_Rate': 'Physical Activity Level',
            trgt: f'{trgt} Level'
        }
        
        quartiles = {
            col: df[col].quantile([0.25, 0.75]) 
            for col in columns_to_categorize.keys()
        }
        
        # Vectorized categorization function
        def categorize_column(series, col_name):
            conditions = [
                series <= quartiles[col_name][0.25],
                series <= quartiles[col_name][0.75]
            ]
            choices = [
                f"Low {columns_to_categorize[col_name].replace(' Level', '')}",
                f"Moderate {columns_to_categorize[col_name].replace(' Level', '')}",
                f"High {columns_to_categorize[col_name].replace(' Level', '')}"
            ]
            return np.select(conditions, choices[:2], default=choices[2])
        
        # Apply categorization using vectorized operations
        for col, new_col in columns_to_categorize.items():
            df[new_col] = categorize_column(df[col], col)
        
        # Optimize groupby operations by pre-selecting only necessary columns
        pairs = []
        for source_col in ['Alcohol Level', 'Obesity Level', 'Diabetes Level', 'Physical Activity Level']:
            pairs.append(
                df[[source_col, 'Region']]
                .groupby([source_col, 'Region'])
                .size()
                .reset_index(name="Count")
            )
        
        # Add the target pairs
        pairs.append(
            df[['Region', f"{trgt} Level"]]
            .groupby(['Region', f"{trgt} Level"])
            .size()
            .reset_index(name="Count")
        )
        
        # Create node mapping more efficiently
        all_nodes = pd.unique(np.concatenate([
            pair[[pair.columns[0], pair.columns[1]]].values.ravel()
            for pair in pairs
        ]))
        node_map = dict(zip(all_nodes, range(len(all_nodes))))
        
        # Create source, target, and values arrays more efficiently
        source = []
        target = []
        values = []
        
        # Process first four pairs (source -> Region)
        for pair in pairs[:-1]:
            source.extend(pair.iloc[:, 0].map(node_map))
            target.extend(pair.iloc[:, 1].map(node_map))
            values.extend(pair['Count'])
        
        # Process last pair (Region -> target)
        source.extend(pairs[-1].iloc[:, 0].map(node_map))
        target.extend(pairs[-1].iloc[:, 1].map(node_map))
        values.extend(pairs[-1]['Count'])
        
        # Create figure with optimized settings
        fig = go.Figure(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                label=all_nodes,
                # color='lightgray'  # Adding a light color can improve rendering speed
            ),
            link=dict(
                source=source,
                target=target,
                value=values
            )
        ))
        
        fig.update_layout(
            title_text="Risk Factor Influence on Heart Disease per Continent",
            font_size=12,
            showlegend=False,  # Disable legend if not needed
            height=600,  # Set fixed height
            width=800,   # Set fixed width
        )
        
        return fig
    
    @cache.memoize(timeout=3600) 
    def filter_scatter_data(year, countries, x_feature, y_feature):
        """
           Filters the dataset based on selected year and countries for scatter plot visualization.

           Args:
               year (str or int): Selected year or 'All'
               countries (str): Selected country or 'All'
               x_feature (str): Feature name for x-axis
               y_feature (str): Feature name for y-axis

           Returns:
               pd.DataFrame: Filtered DataFrame containing only the selected data
           """
        try:
            # Only selecting the columns we need
            needed_columns = ['Year', 'Country', x_feature, y_feature]
            filtered_df = corr_data[needed_columns].copy()
            
            if year != 'All':
                filtered_df = filtered_df[filtered_df['Year'] == year]
            if countries == 'All':
                filtered_df = filtered_df.groupby(['Country', 'Year'], as_index=False).mean()
            if countries != 'All':
                filtered_df = filtered_df[filtered_df['Country'] == countries]
                
            # Remove any rows with NaN values in the features we're plotting
            filtered_df = filtered_df.dropna(subset=[x_feature, y_feature])
            # aggregated_data = filtered_df.groupby(['Country', 'Year'], as_index=False).mean()

            
            return filtered_df
        except Exception as e:
            print(f"Error in filter_scatter_data: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error

    @cache.memoize()
    def filter_heatmap_data(year, countries):
        """
          Filters the dataset based on selected year and countries for heatmap visualization.

          Args:
              year (str or int): Selected year or 'All'
              countries (str): Selected country or 'All'

          Returns:
              pd.DataFrame: Filtered DataFrame containing only the selected data
          """
        filtered_df = corr_data.copy()
        if year != 'All':
            filtered_df = filtered_df[filtered_df['Year'] == year]
        if countries != 'All':
            filtered_df = filtered_df[filtered_df['Country'] == countries]
        return filtered_df

    #callbacks for correlation page
    
    @app.callback(
        Output("heatmap-dropdown", "value"),
        Input("heatmap-dropdown", "value"),
        prevent_initial_call=True
    )
    def update_dropdown(selected_values):
        if selected_values:
            if "All" in selected_values:
                return [opt for opt in corr_data.columns if opt not in ['Gender', 'Age_Group', 'Country', 'Year']]
        return selected_values

    # Filter dataset and update heatmap
    @app.callback(
    Output('heatmap', 'figure'),
    Input('year-dropdown-corr', 'value'),
    Input('country-dropdown-corr', 'value'),
    Input('heatmap-dropdown', 'value'),
    prevent_initial_call=True
        )
        
    @cache.memoize()
    def update_heatmap(year, countries, selected_features):
        """
           Updates the heatmap feature selection dropdown values.

           Args:
               selected_values (list): List of currently selected feature values

           Returns:
               list: Updated list of selected values, returns all features if 'All' is selected
           """
        #creating a check for when year or countries is none
        if year is None or countries is None or not selected_features:
            return go.Figure()
    
        # Use cached filtered data
        filtered_df = filter_heatmap_data(year, countries)
        
        # Additional check in case filtering returns empty DataFrame
        if filtered_df.empty:
            return go.Figure()
        else:
            # Use cached filtered data
            filtered_df = filter_heatmap_data(year, countries)

            # Compute correlation matrix
            correlation_matrix = filtered_df[selected_features].corr()

            fig = px.imshow(correlation_matrix,
                            labels=dict(color="Correlation"),
                            x=selected_features,
                            y=selected_features,
                            color_continuous_scale="RdBu_r",
                            zmin=-1, zmax=1)

        
        return fig


    # Update scatterplot based on filters
    @app.callback(
    Output('scatterplot-corr', 'figure'),
    Input('year-dropdown-corr', 'value'),
    Input('country-dropdown-corr', 'value'),
    Input('scatter-dropdown-x', 'value'),
    Input('scatter-dropdown-y', 'value')
    )
    @cache.memoize()
    def update_scatter(year, countries, x_feature, y_feature):
        """
           Updates the scatter plot based on selected filters and features.

           Args:
               year (str or int): Selected year or 'All'
               countries (str): Selected country or 'All'
               x_feature (str): Feature name for x-axis
               y_feature (str): Feature name for y-axis

           Returns:
               go.Figure: Updated scatter plot figure
           """
        if not x_feature or not y_feature:
            return go.Figure()

        # Use cached filtered data
        filtered_df = filter_scatter_data(year, countries, x_feature, y_feature)

        # If the user selects the same feature for both axes, create a temporary copy
        if x_feature == y_feature:
            filtered_df = filtered_df.copy()  # avoid SettingWithCopyWarning
            filtered_df[f"{y_feature}_y"] = filtered_df[y_feature]
            filtered_df[f"{x_feature}_x"] = filtered_df[x_feature]
            y_to_plot = f"{y_feature}_y"
            x_to_plot = f"{x_feature}_x"
        else:
            y_to_plot = y_feature
            x_to_plot = x_feature

        fig = px.scatter(filtered_df, x=x_to_plot, y=y_to_plot, color='Country',
                        title=f"{x_feature} vs {y_feature}", hover_data=['Country'], trendline="ols")
        fig.update_layout(height=500)
        return fig

    #callback to update sankey diagram with filter
    @app.callback(
            Output('sankey-diagram', 'figure'),
            Input('sankey-dropdown', 'value')
    )
    @cache.memoize()
    def update_sankey(target):
        """
        Updates the Sankey diagram based on selected target variable.

        Args:
            target (str): Selected target variable ('PrevalenceRate', 'MortalityRate', or 'IncidenceRate')

        Returns:
            go.Figure: Updated Sankey diagram figure
        """
        return create_sankey(target)


