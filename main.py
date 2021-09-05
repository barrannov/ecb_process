import requests
import pandas as pd
import io
import argparse

ENTRYPOINT = 'https://sdw-wsrest.ecb.europa.eu/service/'
RESOURCE = 'data'
FLOW_REF = 'EXR'


def add_arguments():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--from_currencies', nargs='+', help='From currencies', required=True)
    parser.add_argument('--to_currencies', nargs='+', help='To currencies', required=True)
    parser.add_argument('--from_date', help='From date', required=True)
    parser.add_argument('--to_date', help='To date', required=True)
    return parser.parse_args()


def get_data_from_ecb(from_currencies, to_currencies, from_date, to_date):
    key = f'D.{"+".join(set(from_currencies + to_currencies))}.EUR.SP00.A'

    parameters = {
        'startPeriod': from_date,
        'endPeriod': to_date
    }

    request_url = f'{ENTRYPOINT + RESOURCE}/{FLOW_REF}/{key}'

    response = requests.get(request_url, params=parameters, headers={'Accept': 'text/csv'})
    if response.status_code != 200:
        raise Exception(response.text)
    return response.text


def _get_pandas_df(data_to_process):
    return pd.read_csv(
        io.StringIO(data_to_process),
        parse_dates=['TIME_PERIOD'],
        index_col=['TIME_PERIOD']
    )


def _fill_missing_date_rows(ecb_df):
    """
    generate rows that are missing due to holidays or weekends
    """
    processed_df = ecb_df.groupby('CURRENCY').resample('D').ffill().reset_index('CURRENCY', drop=True)
    return processed_df


def _calculate_missing_exchange_rates(grouped_df, from_currencies, to_currencies):
    """
    calculate any to any currency exchange rates
    """

    calculated_rates_df = pd.DataFrame()

    for from_currency in from_currencies:
        for to_currency in to_currencies:
            from_currency_rate = grouped_df[grouped_df['CURRENCY'] == from_currency.upper()]
            to_currency_rate = grouped_df[grouped_df['CURRENCY'] == to_currency.upper()]

            calculated_rate = pd.DataFrame({
                "EXCHANGE_PAIR": f"{from_currency}/{to_currency}",
                "VALUE": round(to_currency_rate['OBS_VALUE'] / from_currency_rate['OBS_VALUE'], 5),
                "DATE": from_currency_rate.index
            })

            calculated_rates_df = calculated_rates_df.append(calculated_rate, ignore_index=True)

    return calculated_rates_df.set_index('DATE')


if __name__ == '__main__':
    parsed_args = add_arguments()

    from_currencies = [curr.upper() for curr in parsed_args.from_currencies]
    to_currencies = [curr.upper() for curr in parsed_args.to_currencies]
    from_date = parsed_args.from_date
    to_date = parsed_args.to_date

    ecb_data = get_data_from_ecb(
        from_currencies,
        to_currencies,
        from_date,
        to_date
    )

    pandas_df = _get_pandas_df(ecb_data)
    all_rows_df = _fill_missing_date_rows(pandas_df)

    calculated_df = _calculate_missing_exchange_rates(
        all_rows_df,
        from_currencies,
        to_currencies
    )

    result_filename = f'{"+".join(from_currencies)}_{"+".join(to_currencies)}' \
                      f'_{from_date}_{to_date}.csv'

    calculated_df.to_csv(result_filename, header=True)
