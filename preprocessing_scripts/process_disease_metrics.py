import pandas as pd
import numpy as np
import pycountry
from sklearn.preprocessing import LabelEncoder, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from dictionary import country_code_dict


def encode_categorical_columns(df, columns):
    """Encode categorical columns using LabelEncoder"""
    encoder = LabelEncoder()
    for col in columns:
        df[col] = encoder.fit_transform(df[col].astype(str))
    return df


def _impute_with_polynomial_fit(df, target_column, predictor_columns, degree=2):
    """Imputes missing values in the target column using polynomial regression."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected a DataFrame, but got {type(df)} instead.")

    if target_column not in df.columns:
        raise ValueError(f"Column '{target_column}' not found in DataFrame.")

    if df[target_column].isnull().sum() == 0:
        print(f"No missing values in '{target_column}'. Skipping imputation.")
        return df

    if any(col not in df.columns for col in predictor_columns):
        raise ValueError(f"Predictor columns {predictor_columns} not found in DataFrame.")

    # Separate rows with missing and non-missing values
    missing_mask = df[target_column].isnull()
    df_valid = df.dropna(subset=predictor_columns)

    if df_valid.empty:
        print(f"Skipping imputation for '{target_column}' due to missing predictors.")
        return df

    # Train polynomial regression model
    X_train = df_valid.loc[~missing_mask, predictor_columns]
    y_train = df_valid.loc[~missing_mask, target_column]

    poly = PolynomialFeatures(degree=degree)
    X_train_poly = poly.fit_transform(X_train)

    model = LinearRegression()
    model.fit(X_train_poly, y_train)

    # Predict missing values
    X_missing_poly = poly.transform(df.loc[missing_mask, predictor_columns])
    df.loc[missing_mask, target_column] = np.maximum(model.predict(X_missing_poly), 0)

    return df


def get_country_code(country_name):
    """Returns the ISO Alpha-3 country code given a country name"""
    country_name_normalized = country_name.strip().title()

    if country_name_normalized in country_code_dict:
        return country_code_dict[country_name_normalized]

    try:
        country = pycountry.countries.lookup(country_name_normalized)
        return country.alpha_3
    except LookupError:
        return None


def process_disease_metrics(incidence_data, mortality_data, prevalence_data):
    """Process disease metrics including incidence, mortality, and prevalence."""
    dfs = {
        'incidence': (incidence_data, 'IncidenceRate'),
        'mortality': (mortality_data, 'MortalityRate'),
        'prevalence': (prevalence_data, 'PrevalenceRate')
    }

    processed_dfs = []
    for name, (df, rate_col) in dfs.items():
        processed_df = df.rename(columns={
            'location_name': 'Country',
            'sex_name': 'Gender',
            'age_name': 'Age_Group',
            'year': 'Year',
            'val': rate_col
        })
        processed_df = processed_df[['Country', 'Gender', 'Year', 'Age_Group', rate_col]]
        processed_dfs.append(processed_df)

    # Merge datasets
    df_combined = pd.merge(processed_dfs[0], processed_dfs[1],
                           on=['Country', 'Year', 'Gender', 'Age_Group'],
                           how='outer')
    df_combined = pd.merge(df_combined, processed_dfs[2],
                           on=['Country', 'Year', 'Gender', 'Age_Group'],
                           how='outer')

    df_combined = encode_categorical_columns(df_combined, ['Gender', 'Age_Group'])

    # Impute missing values
    for rate in ['IncidenceRate', 'PrevalenceRate', 'MortalityRate']:
        df_combined = _impute_with_polynomial_fit(df_combined, rate, ['Year'])

    # Add country codes
    df_combined['Country'] = df_combined['Country'].astype(str).str.strip()
    df_combined['Country_Code'] = df_combined['Country'].apply(get_country_code)

    return df_combined