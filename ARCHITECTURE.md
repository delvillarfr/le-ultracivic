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

# Landing Page Appearance
It is a very simple webpage with no navbar.
The top of the site says "Ultra Civic"
The hero line says: "Buy + Retire Polluters' Rights to Emit __ Tons of CO2", with __ equal to 1 by default. User sets the number (1-99).
A subtitle explains what happens:
"Pay $24x USD; Earn x $PR (ERC-20)"
"Improve the world by $230x USD."

Below this is a textbox for users to input a custom 1-100 character message.
"Your message for the Public History"
The message that appears in gray and disappears when the user clicks on the message box is:
"they will say, 'This land that was laid waste has become like the garden of Eden'" Ezequiel 36:35

Below are two buttons.
One button says: "Do It"
The other button says: "What?"
"Do it" initiates the flow.
"What?" opens a modal with an explanation of the project.

Below is a table titled History.
It has three columns: the serial numbers of retired allowances, the users' messages, and the link to the transaction from Ultra Civic's Treasury to the user's wallet.

At the bottom is:
"You POC: paco@ultracivic.com"

## Under the "What?" button

Back in January 10, 2014, Vitalik mentioned a blueprint for a new kind of "economic democracy":
... it is possible to set up currencies whose seigniorage, or issuance, goes to support certain causes, and people can vote for those causes by accepting certain currencies at their businesses.

This economic system hasn't taken off. The reason: it's hard to find a public good that is easy to deliver and has well-understood benefits.

Ultra Civic found one: clean air, or the stopping of CO2 emissions. One ton of CO2 is well-known to cost society in the hundreds of dollars ($230 according to the EPA), and we found how to stop a ton in the dozens.

In the Northeastern U.S., coal, oil, or gas power plants must buy pollution rights to emit CO₂.
(pollution right and arrow to power plant emitting 1tco2)

Each year, states issue a fixed number of pollution rights—enough for about 20% of France + Monaco’s total CO₂ emissions (similar to the U.K.’s).
(many happy power plants jointly emitting 80Mtco2)

This matters because you can also buy pollution rights. Yes, you!
(individual looking puzzled)

Power plants will use every last one to emit exactly one ton of CO₂, unless you buy and permanently retire them first!
(sad power plant that pollutes little. Happy you moving allowances to black no exit door.)

Ultra Civic lets you retire pollution rights in one click and mints you 1 $PR (ERC-20 token) per retirement. Stopping one ton of CO₂ saves society $230 in damages (U.S. EPA). That's your social impact, U.S. state-enforced. Start here.
