# Overview
- Front-end: A Next.js application deployed on Vercel.
- Backend: A FastAPI (Python) application deployed on Render, executed by uvicorn.
- Monorepo directory structure, with the front-end in ./frontend and the backend in ./backend
- Database: A PostgreSQL database managed by Neon. PostgreSQL driver: asyncpg. ORM layer: SQLModel. The database has a single table called “allowances”. Alembic is used for database migrations.
- Blockchain Interaction: Alchemy for node access, OpenZeppelin Defender for secure transactions.
- Secrets: Stored in Vercel and Render environment-variable dashboards. pydantic-settings loads strongly-typed settings from env vars. python-dotenv – reads your local .env file during development.
- Resend for sending email.
- Dependency and code quality: Poetry to create the project and add dependencies; Ruff for linting; Black for python code formatting; pre-commit for CI; pytest+httpx to smoke-test API endpoints and make sure I don’t break them at 2AM.

# Database overview
The database consists of a single table called "allowances" with the following columns:
- serial number (an alphanumeric string with at most 32 characters)
- status (either “available”, “reserved”, or “retired”)
- order (a string with an order id created at checkout)
- timestamp (the datetime of the order creation)
- wallet (the buyer’s wallet address)
- message (the buyer’s retirement message)

# Token overview
The $PR token is pre-mined and completely vanilla (OpenZeppelin ERC20.sol with ERC20Burnable.sol and ERC20Permit.sol), so the treasury only transfers.
It lives in the Sepolia testnet.

# Flow
## 0. User arrives to the landing page.

## 1. User fills a form
- User types in how many allowances they want (React Forms) and an optional message (React Textarea).
- An internal tester makes sure the input is an integer number between 1 and 99 inclusive and checks that the message field is 100 character long (include a character count).
- User selects either ETH or USDC.
- User sees the dollar price, e.g., “This will cost ~$72 + gas.”. The “~” symbol appears only if the user selects eth.
- User clicks on “Do it.” This action triggers Next.js + React code to blur the background by changing React state.

## 2. User connects their crypto wallet
A RainbowKit window asks the user to pick MetaMask, WalletConnect, etc., and to approve the connection.

RainbowKit gives the nice UI, and Wagmi hooks in the Next.js app manage the connection state, securely obtaining the user's wallet address (0x...) and chain details (e.g. Sepolia).

## 3. Front-end asks backend to reserve the allowances
The user’s connection approval triggers a call: POST /api/retirements with JSON { num_allowances, message, wallet }, a simple fetch().

The goal is to avoid having two people pay for the same allowance.

## 4.Backend locks rows in the database
The FastAPI application receives the request. Its built-in Pydantic models validate the incoming data.

It then:
- Uses SQLModel and the asyncpg driver to execute a SELECT ... FOR UPDATE SKIP LOCKED query on the Neon PostgreSQL database to find and lock N rows whose status is “available”, so no one else can touch them until the transaction ends.
- If it cannot lock N rows, it aborts and returns a helpful error message.
- It marks each as reserved, stores the user’s wallet address and message, stamps a timestamp, and creates a brand-new order_id (UUID v4).

Finally,
- PostgreSQL commits the transaction (which releases the locks).
- FastAPI then sends a 200 OK response to the front-end with { order_id }.

## 5. Wallet prompts the user to pay
The front-end receives the { order_id  }.
Then, the payment confirmation flow depends on whether the user selected ETH or USDC.

If the user selected ETH:
- The front-end asks 1inch’s public quote API: “How much ETH equals N × $24 right now?”
- The front-end receives a number in wei (the smallest ETH unit) and converts it to a user-friendly ETH value. ethers.js does the conversion (it's included in wagmi).

If the user selected USDC:
- The front-end uses a 1inch swap to get eth from usdc.

Then,
- The front-end uses wagmi’s useSendTransaction hook with the following transaction details:
to = Ultra Civic treasury address; value = ETH amount you got from 1inch; data = empty (just a plain ETH transfer).
- MetaMask pops up: “Send 0.052 ETH to Ultra Civic?” and the User click Confirm. The pop-up changes 0.052ETH for 72USDC if the user selected USDC.
- User clicks Confirm.

## 6. Front-end notifies backend that payment was sent
- Call: POST /api/retirements/confirm with { txHash, order_id }.
- Backend quickly replies “Accepted” so the front-end can show a “Processing your transaction…” spinner.

## 7. Backend watches the blockchain for that txHash
Every few seconds, the backend calls the Alchemy Sepolia RPC method eth_getTransactionReceipt.

Stop conditions:
- If the receipt shows status == 1, the payment is final.
- If a timeout (say 5 minutes) is reached or the tx fails, mark the order as failed and put the allowances back to available.

## 8. Backend marks the allowances as retired
SQLModel update: Changes each matching row from reserved to retired.
PostgreSQL: Commits status change.

## 9. Backend sends the user reward tokens ($PR)
REST call to thirdweb telling it to execute an ERC-20 transfer of N tokens from the treasury wallet to the user’s wallet. The treasury wallet pays gas.

## 10. Front-end polls for final status
- Endpoint: GET /api/retirements/status/{order_id} every two seconds.
- States returned: "pending", "paid_but_not_retired", "completed", "error".

When it sees "completed":
- The modal switches to a success screen: “Polluters will now emit N fewer tons of CO₂. Congratulations!”
- It also shows the serial numbers of the retired allowances.

## 11. Front-end updates the public history table
The front-end then prepends a row to the landing page's history table with the serial numbers of the retired allowances, the user's message, and the etherscan link to the $PR transaction from the Treasury to the user's wallet. Next.js re-renders history table component. React Query invalidates history query to refresh data.

# Additional Considerations
## Cron job to clean up expired reservations
A Cron job on Render runs every 20 minutes to reclaim allowances that were reserved but never paid.

Job query:
UPDATE allowances
SET status = 'available',
	order   = NULL,
	message = NULL,
	wallet  = NULL,
	timestamp = NULL
WHERE status = 'reserved' AND now() - timestamp > interval '15 minutes';

## Safety
- Rate limiting and CORS: A SlowAPI decorator limits how many times an IP can hit your /api/retirements* routes per minute (10 requests/minute per IP)
- FastAPI’s built-in CORS middleware restricts origins to your own front-end.
- Validation on the server: FastAPI + Pydantic double-checks the wallet address is EIP-55 checksummed, the message length is acceptable, and num_allowances is 1-99.
- Audit logging: Every checkout request writes one row to a log table with the user’s IP, user agent, request body hash, and timestamp.
- Alerting: If the thirdweb token transfer fails, the backend calls SendGrid to email you at paco@ultracivic.com so you can step in manually.



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
