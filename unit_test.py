import unittest
import pandas as pd
import json
from io import StringIO

from main import calculate_losses, filter_deals


class TestReinsuranceContract(unittest.TestCase):

    def setUp(self):
        # Mock data
        self.deals_data = """DealId,Company,Peril,Location
1,WestCoast,Earthquake,USA
2,WestCoast,Hailstone,Canada
3,AsianCo,Hurricane,Philippines
4,AsianCo,Earthquake,New Zealand
5,GeorgiaInsurance,Hurricane,USA
6,MidWestInc,Tornado,USA"""

        self.losses_data = """EventId,DealId,Loss
1,1,2000
2,1,1500
3,5,4000
4,6,1000"""

        self.contract_data = {
            "Coverage": [
                {"Attribute": "Location", "Include": ["USA", "Canada"]},
                {"Attribute": "Peril", "Exclude": ["Tornado"]}
            ],
            "MaxAmount": 3000
        }

        self.deals = pd.read_csv(StringIO(self.deals_data))
        self.losses = pd.read_csv(StringIO(self.losses_data))

    def test_filter_deals(self):
        filtered_deals = filter_deals(self.deals, self.contract_data)
        expected_deals = pd.DataFrame({
            'DealId': [1, 2, 5],
            'Company': ['WestCoast', 'WestCoast', 'GeorgiaInsurance'],
            'Peril': ['Earthquake', 'Hailstone', 'Hurricane'],
            'Location': ['USA', 'Canada', 'USA']
        })
        pd.testing.assert_frame_equal(filtered_deals.reset_index(drop=True), expected_deals)

    def test_calculate_losses(self):
        filtered_deals = pd.DataFrame({
            'DealId': [1, 5],
            'Company': ['WestCoast', 'GeorgiaInsurance'],
            'Peril': ['Earthquake', 'Hurricane'],
            'Location': ['USA', 'USA']
        })
        total_losses = calculate_losses(filtered_deals, self.losses, 3000)
        expected_losses = pd.DataFrame({
            'Peril': ['Earthquake', 'Hurricane'],
            'CappedLoss': [3500, 3000]
        })
        pd.testing.assert_frame_equal(total_losses, expected_losses)


if __name__ == '__main__':
    unittest.main()
