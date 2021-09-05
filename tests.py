import unittest
import pandas as pd

from pandas.testing import assert_frame_equal

from main import _fill_missing_date_rows, _calculate_missing_exchange_rates


def assert_frame_equal_with_sort(results, expected, keycolumns):
    results_sorted = results.sort_values(by=keycolumns).reset_index(drop=True)
    expected_sorted = expected.sort_values(by=keycolumns).reset_index(drop=True)
    assert_frame_equal(results_sorted, expected_sorted)


class SimpleTest(unittest.TestCase):
    def test_fill_missing_date_rows(self):
        data_to_process_df = pd.DataFrame({"CURRENCY": ['USD', 'USD', 'USD', 'EUR', 'EUR'],
                                           "OBS_VALUE": [0.753, 0.763, 0.783, 0.733, 0.763],
                                           "TIME_PERIOD": pd.Series(
                                               ['2017-09-10', '2017-09-11', '2017-09-13', '2017-09-10', '2017-09-13'],
                                               dtype='datetime64[ns]'),
                                           }).set_index('TIME_PERIOD')

        expected_df = pd.DataFrame({"CURRENCY": ['USD', 'USD', 'USD', 'USD', 'EUR', 'EUR', 'EUR', 'EUR'],
                                    "OBS_VALUE": [0.753, 0.763, 0.763, 0.783, 0.733, 0.733, 0.733, 0.763],
                                    "TIME_PERIOD": pd.Series(
                                        ['2017-09-10', '2017-09-11', '2017-09-12', '2017-09-13', '2017-09-10',
                                         '2017-09-11',
                                         '2017-09-12', '2017-09-13'],
                                        dtype='datetime64[ns]'),
                                    }).set_index('TIME_PERIOD')

        processed_df = _fill_missing_date_rows(data_to_process_df)
        assert_frame_equal_with_sort(
            processed_df,
            expected_df,
            'CURRENCY'
        )

    def test_calculate_missing_exchange_rates(self):
        data_to_process_df = pd.DataFrame({"CURRENCY": ['USD', 'USD', 'JPY', 'JPY'],
                                           "OBS_VALUE": [0.845, 0.855, 0.0077, 0.0079],
                                           "TIME_PERIOD": pd.Series(
                                               ['2017-09-10', '2017-09-11', '2017-09-10', '2017-09-11'],
                                               dtype='datetime64[ns]'),
                                           }).set_index('TIME_PERIOD')

        expected_df = pd.DataFrame({"EXCHANGE_PAIR": ['JPY/USD', 'JPY/USD'],
                                    "VALUE": [108.22785, 109.74026],
                                    "DATE": pd.Series(['2017-09-10', '2017-09-11'], dtype='datetime64[ns]'),
                                    }).set_index('DATE')

        processed_df = _calculate_missing_exchange_rates(data_to_process_df, ['JPY'], ['USD'])
        assert_frame_equal_with_sort(
            processed_df,
            expected_df,
            'VALUE'
        )
