# fnbo_tests

This Project is used to run FNBO test cases to make sure Payment Credit pay api is working fine.

### Setting up this project

1. Close this repository
2. Create venv
3. run pip install -r requirements.txt

Note: Make sure that you have 52Tests_Script_CentimeTesting_FCC.xlsx and payment_required_details.xlsx in the resource folder. As our tests will pick data from these files.

### Running tests

#### If We need to create supplied bank details data and then run tests then run below command

pytest test_fnbo.py --insert_supp_data yes -x

#### If supplied bank details data is already available in the db and we just need to run tests.

pytest test_fnbo.py --insert_supp_data no -x


