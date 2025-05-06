import os
import pandas as pd
from process_activity_obesity_gdp import process_activity_obesity_gdp
from process_disease_metrics import process_disease_metrics
from process_diabetes_alcohol import process_diabetes_alcohol
from process_overweight_health import process_overweight_health


class DataProcessor:
    def __init__(self):
        pass

    def process_all_data(self, data_files):
        # Process activity, obesity, and GDP data
        print("Processing Activity, Obesity, and GDP data...")
        activity_obesity_gdp = process_activity_obesity_gdp()

        # Load disease-related datasets
        print("Processing Disease Metrics data...")
        incidence_data = pd.read_csv(data_files['incidence'])
        mortality_data = pd.read_csv(data_files['mortality'])
        prevalence_data = pd.read_csv(data_files['prevalence'])
        disease_metrics = process_disease_metrics(incidence_data, mortality_data, prevalence_data)

        # Load diabetes and alcohol data
        print("Processing Diabetes and Alcohol data...")
        diabetes_data = pd.read_csv(data_files['diabetes'])
        alcohol_data = pd.read_excel(data_files['alcohol'])
        diabetes_alcohol = process_diabetes_alcohol(diabetes_data, alcohol_data)

        # Load overweight and world health data
        print("Processing Overweight and World Health data...")
        overweight_data = pd.read_excel(data_files['overweight'])
        world_health_data = pd.read_csv(data_files['world_health'])
        life_expectancy_data = pd.read_csv(data_files['life_expectancy'])
        overweight_health = process_overweight_health(overweight_data, world_health_data, life_expectancy_data)

        return {
            'activity_obesity_gdp': activity_obesity_gdp,
            'disease_metrics': disease_metrics,
            'diabetes_alcohol': diabetes_alcohol,
            'overweight_health': overweight_health
        }


def main():
    data_files = {
        'incidence': 'data/GBD_INCIDENCE.csv',
        'mortality': 'data/GBD_MORTALITY-DEATHS.csv',
        'prevalence': 'data/GBD_PREVALENCE.csv',
        'diabetes': 'data/diabetes_data.csv',
        'alcohol': 'data/alcohol_consumption.xlsx',
        'overweight': 'data/overweight.xlsx',
        'world_health': 'data/world_health_data.csv',
        'life_expectancy': 'data/life_expectancy.csv'
    }

    # Create output directory if it doesn't exist
    os.makedirs('datasets', exist_ok=True)

    # Initialize processor
    processor = DataProcessor()

    try:
        # Process all datasets
        processed_data = processor.process_all_data(data_files)

        # Save processed datasets
        processed_data['activity_obesity_gdp'].to_csv('datasets/processed_activity_obesity_gdp.csv', index=False)
        processed_data['disease_metrics'].to_csv('datasets/processed_disease_metrics.csv', index=False)
        processed_data['diabetes_alcohol'].to_csv('datasets/processed_diabetes_alcohol.csv', index=False)
        processed_data['overweight_health'].to_csv('datasets/processed_health_data.csv', index=False)

        print("\nAll data processing completed successfully!")

    except Exception as e:
        print(f"An error occurred during processing: {str(e)}")
        raise


if __name__ == "__main__":
    main()
