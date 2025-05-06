import pandas as pd
from sklearn.impute import KNNImputer


def read_file(file, columns_to_keep, new_column_names):
    """
    Read and process an Excel file with standardized formatting.
    """
    df = pd.read_excel(file)
    df.columns = df.iloc[1]
    df = df.drop([0, 1], axis=0).reset_index(drop=True)
    df = df[columns_to_keep]
    df.columns = new_column_names
    return df


def clean_and_transform(df, year_column, rate_column):
    """
    Clean and transform the data by handling duplicates and type conversion.
    """
    df[year_column] = df[year_column].astype(int)
    df[rate_column] = df[rate_column].astype(float)

    original_len = len(df)
    df = df.drop_duplicates(keep='first')
    rows_removed = original_len - len(df)
    print(f"Rows removed: {rows_removed}")

    return df


def _merge_and_impute_activity_obesity(df1, df2, df3):
    """Merge and impute activity, obesity and GDP data"""
    # Rename columns for clarity
    df1.rename(columns={'Prevalence_Rate': 'Activity_Prevalence_Rate'}, inplace=True)
    df2.rename(columns={'Prevalence_Rate': 'Obesity_Prevalence_Rate'}, inplace=True)

    # Merge DataFrames
    merged_df = pd.merge(df1, df2, on=['Country', 'Code', 'Year'], how='outer')
    merged_df = pd.merge(merged_df, df3, on=['Country', 'Code', 'Year'], how='outer')
    merged_df = merged_df[merged_df['Country'] != 'World']

    # Apply KNN imputation
    knn_imputer = KNNImputer(n_neighbors=5)
    columns_to_impute = ['Activity_Prevalence_Rate', 'Obesity_Prevalence_Rate', 'GDP']
    merged_df[columns_to_impute] = knn_imputer.fit_transform(merged_df[columns_to_impute])

    return merged_df


def process_activity_obesity_gdp():
    """
    Process and merge physical activity, obesity, and GDP datasets.
    Handles data cleaning, merging, and imputation for these related metrics.
    """
    activity_file = "data/insufficient_physical_activity_data.xlsx"
    obesity_file = "data/obesity_data.xlsx"
    gdp_file = "data/gdp-per-capita-worldbank.csv"

    columns_to_keep = ['Location', 'SpatialDimValueCode', 'Period', 'FactValueNumeric']
    new_column_names = ['Country', 'Code', 'Year', 'Prevalence_Rate']

    activity_prevalence = read_file(activity_file, columns_to_keep, new_column_names)
    obesity_prevalence = read_file(obesity_file, columns_to_keep, new_column_names)

    activity_prevalence = clean_and_transform(activity_prevalence, 'Year', 'Prevalence_Rate')
    obesity_prevalence = clean_and_transform(obesity_prevalence, 'Year', 'Prevalence_Rate')

    gdp_data = pd.read_csv(gdp_file)
    gdp_data.rename(columns={
        'Entity': 'Country',
        'GDP per capita, PPP (constant 2017 international $)': 'GDP'
    }, inplace=True)
    gdp_data = gdp_data.dropna(subset=['Code'])

    final_df = _merge_and_impute_activity_obesity(activity_prevalence, obesity_prevalence, gdp_data)
    return final_df