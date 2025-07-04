# User Flow

1. User lands, selects a number of pollution rights to retire, picks ETH or USDC as payment currency and clicks on “Do it”.
2. User is prompted to connect their wallet.
3. The front-end sends a retirement request to the backend.
4. The backend goes to the database, finds N available pollution rights and sets their status from "available" to "reserved".
5. Allowances cost $24USD. If User picked ETH, the frontend fetches an exchange rate, computes the total price and prompts the user to transact.
6. If User approves, the wallet returns a tx hash. The front-end sends it to the backend for validation.
7. The backend polls an Ethereum node for the status of tx hash.
8. On Payment Success, the backend updates the pollution rights' status from "reserved" to "retired".
9. The backend transfers N $PR tokens from Ultra Civic’s Treasury wallet to User's wallet.
10. The front-end displays the success message "Polluters will now emit N less tons of CO2. Congratulations!" and refreshes a public history table.

## Notes:
The $PR token is pre-mined and completely vanilla (OpenZeppelin ERC20.sol with ERC20Burnable.sol and ERC20Permit.sol).
A cron job queries the database every 20 mins and reverts "reserved" pollution rights back to "available" for pollution rights that have been reserved for more than 20 mins.
