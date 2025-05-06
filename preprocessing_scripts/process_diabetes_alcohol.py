import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
from numpy.polynomial import Polynomial
from dictionary import wrong_countries, region_mapping


def _diabetes_column_processing(df):
    """Process diabetes-specific columns and encode categorical variables."""
    df = df.rename(columns={
        'Country/Region/World': 'Location',
        'ISO': 'Code',
        'Sex': 'Gender'
    })
    df["Gender"] = df["Gender"].map({"Men": 0, "Women": 1})
    columns_to_drop = [
        'Age',
        'Prevalence of diabetes (18+ years) lower 95% uncertainty interval',
        'Prevalence of diabetes (18+ years) upper 95% uncertainty interval',
        'Proportion of people with diabetes who were treated (30+ years)',
        'Proportion of people with diabetes who were treated (30+ years) lower 95% uncertainty interval',
        'Proportion of people with diabetes who were treated (30+ years) upper 95% uncertainty interval'
    ]
    df = df.drop(columns_to_drop, axis=1)
    return df


def _adding_missing_years(df):
    """Add missing years to dataset with placeholder values."""
    years_1980_to_1989 = list(range(1960, 1990))
    countries = df['Location'].unique()
    new_rows = []

    for country in countries:
        for year in years_1980_to_1989:
            new_row = {
                'Location': country,
                'Year': year,
                'Code': df[df['Location'] == country]['Code'].iloc[0]
            }

            for col in df.columns:
                if col not in ['Location', 'Year', 'Code']:
                    new_row[col] = float('nan')

            new_rows.append(new_row)

    new_data = pd.DataFrame(new_rows)
    df = pd.concat([df, new_data], ignore_index=True)
    df = df.sort_values(by=['Location', 'Year']).reset_index(drop=True)
    return df


def _impute_diabetes_data(df):
    """Impute missing diabetes prevalence data using polynomial fitting."""
    known_data = df[df["Prevalence of diabetes (18+ years)"].notnull()]
    known_years = known_data["Year"]
    known_prevalence = known_data["Prevalence of diabetes (18+ years)"]

    poly = Polynomial.fit(known_years, known_prevalence, deg=2)
    df["Prevalence of diabetes (18+ years)"] = poly(df["Year"])

    return df


def _convert_year_to_int(df, column_name='Year'):
    """Convert year column to integer type."""
    df[column_name] = df[column_name].astype(int)
    return df


def _impute_alcohol_data(alcohol_data):
    """Impute missing alcohol data using KNN"""
    location_mapping = {loc: i for i, loc in enumerate(alcohol_data['Location'].unique())}
    code_mapping = {code: i for i, code in enumerate(alcohol_data['Code'].unique())}

    alcohol_data['Location_Num'] = alcohol_data['Location'].map(location_mapping)
    alcohol_data['Code_Num'] = alcohol_data['Code'].map(code_mapping)

    features = ['Location_Num', 'Code_Num', 'Year', 'Alcohol_Value']
    data_for_imputation = alcohol_data[features]

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data_for_imputation)

    imputer = KNNImputer(n_neighbors=5)
    imputed_data = imputer.fit_transform(scaled_data)

    imputed_data_original_scale = scaler.inverse_transform(imputed_data)
    alcohol_data['Alcohol_Value'] = imputed_data_original_scale[:, 3]

    alcohol_data.drop(['Location_Num', 'Code_Num'], axis=1, inplace=True)

    return alcohol_data


def impute_with_polynomial( df, year_col, target_col, degree=2):
    """
    Impute missing values using polynomial regression on time series.
    """
    known_data = df[df[target_col].notnull()]
    known_years = known_data[year_col]
    known_values = known_data[target_col]

    missing_data = df[df[target_col].isnull()]
    missing_years = missing_data[year_col]

    # Fit a polynomial to the known data
    poly = Polynomial.fit(known_years, known_values, deg=degree)

    # Predict missing values
    predicted_values = poly(missing_years)

    # Fill in the missing values
    df.loc[df[target_col].isnull(), target_col] = predicted_values
    return df


def _fill_missing_values_with_regional(df, region_mapping, value_column='Alcohol_Value',
                                       location_column='Location', year_column='Year'):
    """Fill missing values using regional data"""
    df_filled = df.copy()

    for country, region in region_mapping.items():
        if country in df_filled[location_column].values:
            country_data = df_filled[df_filled[location_column] == country]
            missing_years = country_data[country_data[value_column].isnull()][year_column].unique()

            if len(missing_years) > 0:
                regional_data = df_filled[df_filled[location_column] == region]
                regional_values = \
                    regional_data[regional_data[year_column].isin(missing_years)].set_index(year_column)[
                        value_column]

                for year in missing_years:
                    df_filled.loc[
                        (df_filled[location_column] == country) &
                        (df_filled[year_column] == year),
                        value_column
                    ] = regional_values.get(year)

    return df_filled

def _remove_wrong_countries(df, column_name='Location'):
    """Remove non-country entries from the dataset"""
    df = df[~df[column_name].isin(wrong_countries)]
    df.reset_index(drop=True, inplace=True)
    return df


def process_diabetes_alcohol(diabetes_data, alcohol_data):
    """
    Process and merge diabetes and alcohol consumption datasets.
    Includes data cleaning, imputation, and regional value filling.
    """
    diabetes_processed = _diabetes_column_processing(diabetes_data)
    diabetes_processed = _adding_missing_years(diabetes_processed)
    diabetes_processed = _impute_diabetes_data(diabetes_processed)

    # Process alcohol data
    alcohol_processed = alcohol_data.melt(id_vars=['Location', 'Code'], var_name='Year', value_name='Alcohol_Value')
    alcohol_processed = _convert_year_to_int(alcohol_processed)
    alcohol_processed = _remove_wrong_countries(alcohol_processed)
    alcohol_processed = _fill_missing_values_with_regional(alcohol_processed, region_mapping)
    alcohol_processed = _impute_alcohol_data(alcohol_processed)
    merged_data = diabetes_processed.merge(alcohol_processed, on=['Location', 'Year', 'Code'], how='outer')
    merged_data = impute_with_polynomial(merged_data, year_col="Year",
                                                           target_col="Alcohol_Value", degree=2)
    merged_data = impute_with_polynomial(merged_data, year_col="Year",
                                                           target_col="Prevalence of diabetes (18+ years)",
                                                           degree=2)
    return merged_data


