import pandas as pd
import pycountry


def _clean_overweight_data(df):
    """Clean and preprocess the overweight dataset"""
    # Select and rename relevant columns
    df.columns = df.iloc[1]
    df = df.drop([0, 1], axis=0).reset_index(drop=True)
    df = df[['SpatialDimValueCode', 'Location', 'Period', 'FactValueNumeric']]
    df = df.rename(columns={
        'SpatialDimValueCode': 'Country_code',
        'Location': 'Country',
        'Period': 'Year',
        'FactValueNumeric': 'Overweight_Prevalence'
    })
    return df


def _clean_world_health_data(df):
    """Clean and preprocess the world health dataset"""
    # Drop specific years with incomplete data
    years_to_drop = [1999, 2022, 2023]
    df = df[~df['year'].isin(years_to_drop)]

    # Remove non-country territories and regions
    countries_to_remove = [
        "American Samoa", "Aruba", "Bermuda", "British Virgin Islands",
        "Cayman Islands", "Channel Islands", "Curacao", "Faroe Islands",
        "French Polynesia", "Gibraltar", "Greenland", "Guam",
        "Hong Kong SAR, China", "Isle of Man", "Korea, Dem. People's Rep.",
        "Kosovo", "Liechtenstein", "Macao SAR, China", "New Caledonia",
        "Northern Mariana Islands", "Not classified", "Puerto Rico",
        "Sint Maarten (Dutch part)", "Somalia", "St. Martin (French part)",
        "Turks and Caicos Islands", "Virgin Islands (U.S.)", "West Bank and Gaza"
    ]
    df = df[~df['country'].isin(countries_to_remove)]

    # Get valid ISO country codes
    valid_country_codes = {country.alpha_3 for country in pycountry.countries}
    df = df[df['country_code'].isin(valid_country_codes)]

    # Handle missing values
    df['health_exp'] = df.groupby('country_code')['health_exp'].ffill()
    df['health_exp'] = df.groupby('country_code')['health_exp'].bfill()
    df['life_expect'] = df.groupby('country_code')['life_expect'].ffill()
    df['life_expect'] = df.groupby('country_code')['life_expect'].bfill()

    # Select and rename columns
    df = df.iloc[:, :5]
    df = df.rename(columns={
        'country_code': 'Country_code',
        'country': 'Country',
        'year': 'Year',
        'health_exp': 'Health_Expenditure',
        'life_expect': 'Life_Expectancy'
    })

    return df


def _process_supplemental_life_expectancy(df):
    """Process supplemental life expectancy data from WHO"""
    # Select relevant columns and filter for total population
    df = df[['SpatialDimValueCode', 'Dim1ValueCode', 'FactValueNumeric', 'Period']]
    df = df[df['Dim1ValueCode'] == 'SEX_BTSX']
    df = df.drop(columns=['Dim1ValueCode'])

    # Rename columns
    df = df.rename(columns={
        'SpatialDimValueCode': 'Country_code',
        'Period': 'Year',
        'FactValueNumeric': 'Imputed_Life_Expectancy'
    })

    return df


def _merge_and_clean_datasets(overweight_df, world_df, life_expectancy_df):
    """Merge all datasets and perform final cleaning"""
    # Initial merge of overweight and world health data
    overweight_df['Year'] = overweight_df['Year'].astype(int)
    merged_df = pd.merge(
        overweight_df,
        world_df,
        on=['Country_code', 'Country', 'Year'],
        how='left'
    )

    # Convert year to numeric
    merged_df['Year'] = merged_df['Year'].astype(int)
    life_expectancy_df['Year'] = life_expectancy_df['Year']

    # Fill missing life expectancy values with supplemental data
    for index, row in life_expectancy_df.iterrows():
        mask = (
                (merged_df['Country_code'] == row['Country_code']) &
                (merged_df['Year'] == row['Year']) &
                (merged_df['Life_Expectancy'].isna())
        )
        merged_df.loc[mask, 'Life_Expectancy'] = row['Imputed_Life_Expectancy']

    # Final interpolation for remaining missing values
    merged_df['Life_Expectancy'] = merged_df['Life_Expectancy'].interpolate(
        method='linear')
    merged_df['Health_Expenditure'] = merged_df['Health_Expenditure'].interpolate(
        method='linear')

    return merged_df


def process_overweight_health(overweight_data, world_health_data, life_expectancy_data):
    """
    Process and merge overweight, health, and life expectancy datasets.
    """
    cleaned_overweight = _clean_overweight_data(overweight_data)
    cleaned_world_health = _clean_world_health_data(world_health_data)
    processed_life_expectancy = _process_supplemental_life_expectancy(life_expectancy_data)

    return _merge_and_clean_datasets(cleaned_overweight,
                                     cleaned_world_health,
                                     processed_life_expectancy)