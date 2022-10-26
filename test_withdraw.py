import pytest
import responses
from responses import matchers
from withdraw import withdraw_crypto_from_kraken


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.mark.parametrize(
    "current_time, expected_nonce, asset_to_withdraw, withdrawal_address_key",
    [
        (111.111, "111111", "XXBTZ", "btc_hardwallet"),
        (222.222, "222222", "ETH", "eth_hardwallet"),
    ],
)
def test_calls_to_kraken_balance_and_withdraw_endpoints_are_made(
    mocked_responses,
    mocker,
    current_time,
    expected_nonce,
    asset_to_withdraw,
    withdrawal_address_key,
):
    mocked_responses.post(
        url="https://api.kraken.com/0/private/Balance",
        match=[matchers.urlencoded_params_matcher({"nonce": expected_nonce})],
        json={"result": {"ZUSD": "2970172.7962"}, "error": []},
    )

    mocked_responses.post(
        url="https://api.kraken.com/0/private/Withdraw",
        match=[
            matchers.urlencoded_params_matcher(
                {
                    "nonce": expected_nonce,
                    "asset": asset_to_withdraw,
                    "key": withdrawal_address_key,
                    "amount": '0.123'
                }
            )
        ],
    )
    mocker.patch("time.time", return_value=current_time)

    withdraw_crypto_from_kraken(
        asset_to_withdraw=asset_to_withdraw,
        withdrawal_address_key=withdrawal_address_key,
    )


def test_calls_to_kraken_balance_and_withdraw_endpoints_are_made_with_different_nonces(
    mocked_responses,
):
    # FIGURE OUT HOW TO TEST THIS LATER, CURRENTLY USING SAME NONCE FOR BOTH CALLS
    pass
