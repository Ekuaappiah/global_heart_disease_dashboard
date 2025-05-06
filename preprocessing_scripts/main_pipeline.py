import pandas as pd
from sklearn.impute import KNNImputer
from numpy.polynomial.polynomial import Polynomial
import numpy as np
import pycountry
from dictionary import country_code_mapping

def get_country_code(country_name):
    """Returns the ISO Alpha-3 country code given a country name."""
    country_name_normalized = country_name.strip().title()
    if country_name_normalized in country_code_mapping:
        return country_code_mapping[country_name_normalized]
    try:
        return pycountry.countries.lookup(country_name_normalized).alpha_3
    except LookupError:
        return None

def add_missing_years(df):
    """Adds missing years (1960-1989) for each country."""
    years = list(range(1960, 1990))
    new_rows = [
        {**{col: np.nan for col in df.columns if col not in ['Country', 'Year', 'Country_Code']},
         'Country': country, 'Year': year, 'Country_Code': df[df['Country'] == country]['Country_Code'].iloc[0]}
        for country in df['Country'].unique() for year in years
    ]
    return pd.DataFrame(new_rows)

def impute_with_polynomial(df, target_col, degree=2):
    """Imputes missing values using polynomial regression."""
    known_data = df[df[target_col].notnull()]
    if known_data.empty:
        return df  # Skip if no data available
    poly = Polynomial.fit(known_data["Year"], known_data[target_col], degree)
    df[target_col] = poly(df["Year"])
    return df

def prep_gapminder_data(gp_df, iso_df):
    """Prepares the Gapminder dataset for merging."""
    iso_df.rename(columns={'English short name lower case': 'country', 'Alpha-3 code': 'Country_Code'}, inplace=True)
    gp_df = gp_df.merge(iso_df[['country', 'Country_Code']], on="country", how="left")
    gp_df["Country_Code"].fillna(gp_df["country"].map(country_code_mapping), inplace=True)
    gp_df.rename(columns={'year': 'Year', 'gdpPercap': 'GDP', 'lifeExp': 'Life_Expectancy'}, inplace=True)
    return gp_df

def impute_with_knn(df, target_col, n_neighbors=5):
    """Imputes missing values using KNN imputation."""
    feature_cols = df.columns.difference(['Country', 'Country_Code', 'Age_Group', 'Gender', target_col])
    impute_cols = feature_cols.append(pd.Index([target_col]))
    imputer = KNNImputer(n_neighbors=n_neighbors)
    df[target_col] = imputer.fit_transform(df[impute_cols])[..., -1]
    return df

# Load datasets
print("Loading datasets...")
weight_health_exp_df = pd.read_csv('datasets/processed_health_data.csv')
diabetes_alcohol_df = pd.read_csv('datasets/processed_diabetes_alcohol.csv')
gdp_obesity_physical_df = pd.read_csv('datasets/processed_activity_obesity_gdp.csv')
heart_disease_df = pd.read_csv('datasets/processed_disease_metrics.csv')
print("Datasets loaded successfully.")

# Standardizing column names
weight_health_exp_df.rename(columns={'Country_code': 'Country_Code'}, inplace=True)
diabetes_alcohol_df.rename(columns={'Code': 'Country_Code', 'Location': 'Country', 'Prevalence of diabetes (18+ years)': 'Diabetes_Prevalence_Rate'}, inplace=True)
gdp_obesity_physical_df.rename(columns={'Code': 'Country_Code'}, inplace=True)
heart_disease_df.rename(columns={'Sex': 'Gender', 'Country Code': 'Country_Code', 'age_name': 'Age_Group'}, inplace=True)

diabetes_alcohol_df['Gender'] = diabetes_alcohol_df['Gender'].map({0: 'Male', 1: 'Female'})
heart_disease_df['Gender'] = heart_disease_df['Gender'].map({0: 'Male', 1: 'Female'})

# Merge datasets
print("Merging datasets...")
merged_df = heart_disease_df.merge(diabetes_alcohol_df, on=['Country_Code', 'Country', 'Year', 'Gender'], how='outer')
merged_df = merged_df.merge(gdp_obesity_physical_df, on=['Country_Code', 'Country', 'Year'], how='outer')
merged_df = merged_df.merge(weight_health_exp_df, on=['Country_Code', 'Country', 'Year'], how='outer')
print("Datasets merged successfully.")

# List of columns to impute
columns_to_impute = ['Alcohol_Value', 'IncidenceRate', 'PrevalenceRate', 'MortalityRate',
                     'Diabetes_Prevalence_Rate', 'Activity_Prevalence_Rate', 'Obesity_Prevalence_Rate',
                     'GDP', 'Health_Expenditure (% of GDP)', 'Life_Expectancy']

# Apply KNN imputation
for col in columns_to_impute:
    merged_df = impute_with_knn(merged_df, target_col=col)

# Set negative GDP values to NaN
merged_df.loc[merged_df['GDP'] < 0, 'GDP'] = np.nan

# Drop unnecessary columns
if 'BMI' in merged_df.columns:
    merged_df.drop('BMI', axis=1, inplace=True)

# Save final cleaned data
merged_df.to_csv('cleaned_final_data.csv', index=False)
print("Data saved successfully as 'cleaned_final_data.csv'.")
