# Exchange rates from ecb.europa.eu

One the first run all dependencies should be installed:
```
virtualenv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
Script usage example:

```
python main.py --from_currencies USD JPY --to_currencies GBP --from_date 2017-09-16 --to_date 2018-07-26
```

Resulting csv file will be stored in the repository root folder
