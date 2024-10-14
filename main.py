import pandas as pd
import json


def load_data(deals_file, contract_file, losses_file):
    # Load data from files
    deals = pd.read_csv(deals_file)
    with open(contract_file, 'r') as f:
        contract = json.load(f)
    losses = pd.read_csv(losses_file)
    return deals, contract, losses


def filter_deals(deals, contract):
    # Filter based on Location and Peril coverage
    location_filter = deals['Location'].isin(contract['Coverage'][0]['Include'])
    peril_filter = ~deals['Peril'].isin(contract['Coverage'][1]['Exclude'])
    return deals[location_filter & peril_filter]


def calculate_losses(filtered_deals, losses, max_amount):
    # Merge deals and losses based on DealId
    merged_data = pd.merge(filtered_deals, losses, on='DealId')
    # Cap the losses to the max amount per event
    merged_data['CappedLoss'] = merged_data['Loss'].apply(lambda x: min(x, max_amount))
    # Group by Peril to calculate total loss per peril
    total_losses = merged_data.groupby('Peril').agg({'CappedLoss': 'sum'}).reset_index()
    return total_losses


if __name__ == "__main__":
    deals_file = 'deals.csv'
    contract_file = 'contract.json'
    losses_file = 'losses.csv'

    deals, contract, losses = load_data(deals_file, contract_file, losses_file)
    filtered_deals = filter_deals(deals, contract)
    total_losses = calculate_losses(filtered_deals, losses, contract['MaxAmount'])

    print("Filtered Deals:")
    print(filtered_deals)

    print("\nTotal Losses:")
    print(total_losses)
