import pytest
# from tests.test_security_service import test_api_security_service


pytest.main([
    './test_fnbo.py',
    '--insert_supp_data=yes'])