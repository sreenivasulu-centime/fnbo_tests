import pandas as pd
import os
import json

import pytest


df = pd.DataFrame()


def get_supplier_data():
    global df
    df = pd.read_excel('resources/52Tests_Script_CentimeTesting_FCC.xlsx', header=1)
    supplier_details = df[
        ['Source Account(PL Card)', 'Payment Amount', 'Vendor Name (counter party)', 'Receiving Account Number',
         'Receiving Routing Number', 'Transaction Description']]
    supplier_details = supplier_details.drop([1], axis=0)
    return supplier_details


def updated_config(vendor_name, account_number, routing_number,payee_client_id):
    sample_curl = """curl --location --request POST 'https://internal.ds.services.stg.centime.com/payments-data-service/1.0/bank-accounts/' --header 'clientid: 1' --header 'loginid: admin@centime.com' --header 'Content-Type: application/json' --data-raw '{"clientId": "client_id",
    "clientType": "SUPPLIER",
    "accountNumber": "account_number",
    "routingNumber": "routing_number",
    "ownerLastName": "vendor_name",
    "accountType": "CHECKING",
    "accountProductType": "DDA",
    "currencyCode": "USD"}'"""
    updated_curl = sample_curl.replace('client_id',str(payee_client_id)).replace('account_number', str(account_number)).replace('routing_number',
                                                                                      str(routing_number)).replace(
        'vendor_name', vendor_name)
    return updated_curl


def get_account_uid(vendor_name, account_number, routing_number,payee_client_id):
    # response = os.system(f"{config['supplier_details']['curl_command']} > result.json")
    curl = updated_config(vendor_name, account_number, routing_number, payee_client_id)
    response = os.system(f'{curl} > result.json')
    response = json.load(open("result.json"))
    print(response)
    supplier_uid = response['data']['uid']
    return supplier_uid


def trigger_pay_api(source_account, amount, payee_uid, payee_cient_id, payment_description):
    sample_dict = {
        "amount": "excel_amount",
        "currencyCode": "USD",
        "payeeDetails": {
            "bankDetails": {
                "uid": "excel_payee_uid",
                "clientType": "SUPPLIER"
            },
            "id": "excel_payee_id"
        },
        "payerDetails": {
            "cardDetails": {
                "clientType": "CLIENT",
                "uid": "excel_payer_uid"
            },
            "id": "payer_client_id"
        },
        "paymentDesc": "excel_payment_description",
        "paymentStartDate": "2021-09-17 23:22:38"
    }
    curl_command = f"curl --location --request POST 'https://internal.fs.services.stg.centime.com/payments-processing" \
                   f"-service/1.0/payments/pay/CENTIME_CREDIT?isDrawCash=false' --header 'clientid: 2' --header " \
                   f"'loginid: admin@centime.com' --header 'Content-Type: application/json' --data-raw '" \
                   f"{json.dumps(sample_dict)}' "
    payer_client_id = {"4988 6562 0455 0401": "2",
                       "4988 6562 4617 0259": "3",
                       "4988 6562 0671 6844 ": "3"}

    payer_uid = {"4988 6562 0455 0401": "u2vfotBU",
                 "4988 6562 4617 0259": "Zrjo4NCk",
                 "4988 6562 0671 6844 ": "Yyw6qwff"}

    updated_curl_command = curl_command.replace('excel_amount', str(amount)).replace('excel_payee_uid', str(payee_uid)). \
        replace('excel_payee_id', str(payee_cient_id)).replace('excel_payer_uid', str(payer_uid[source_account])). \
        replace('payer_client_id', str(payer_client_id[source_account])).replace('excel_payment_description',
                                                                                 payment_description)
    with open('request_response.txt','a+') as file:
        file.write(f"request: {updated_curl_command} \n")
        file.close()

    response = os.system(f'{updated_curl_command} > result.json')
    response = json.load(open("result.json"))
    with open('request_response.txt','a+') as file:
        file.write(f"request: {response} \n")
        file.close()
    return response


def setup_supp_data():
    payment_details = get_supplier_data()
    supplier_bank_account_uid = []
    payee_client_id = []
    _ = [payee_client_id.append(i) for i in range(400, 400 + len(payment_details))]
    for i in range(0, len(payment_details)):
        supplier_bank_account_uid.append(
            get_account_uid(payment_details.iat[i, 2], payment_details.iat[i, 3], payment_details.iat[i, 4],payee_client_id[i]))
    payment_details['supplier_bank_account_uid'] = supplier_bank_account_uid
    payment_details['payee_client_id'] = payee_client_id
    payment_details.to_excel('resources/updated_sheet_with_supp_id.xlsx')
    payment_required_details = pd.DataFrame(payment_details[['Source Account(PL Card)', 'Payment Amount',
                                                             'supplier_bank_account_uid', 'payee_client_id',
                                                             'Transaction Description']])
    payment_required_details.to_excel('resources/payment_required_details.xlsx')


payment_required_details = pd.read_excel('resources/payment_required_details.xlsx', header=0)
if 'Unnamed: 0' in payment_required_details.columns:
    del payment_required_details['Unnamed: 0']


@pytest.mark.parametrize("source_account,amount,payee_uid,payee_client_id,payment_description",
                         payment_required_details.values.tolist())
def test_api(source_account, amount, payee_uid, payee_client_id, payment_description):
    response = trigger_pay_api(source_account, amount, payee_uid, payee_client_id, payment_description)
    assert response['status'] == 'SUCCESS'
