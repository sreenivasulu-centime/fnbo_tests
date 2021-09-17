import pandas as pd
import pytest
from pytest import fixture

import test_fnbo


def pytest_addoption(parser):
    parser.addoption("--insert_supp_data", action="store", default="no", help="Please select yes if you "
                                                                                           "want to insert data")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    insert_data = config.getoption("--insert_supp_data")
    if insert_data == 'yes':
        test_fnbo. setup_supp_data()
    payment_required_details = pd.read_excel('resources/payment_required_details.xlsx', header=0)
    if 'Unnamed: 0' in payment_required_details.columns:
        del payment_required_details['Unnamed: 0']