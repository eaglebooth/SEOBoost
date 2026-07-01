# SEOBoost

SEOBoost is a GenLayer-powered escrow for white-hat SEO work. A business locks a performance reward, the agency submits article and ranking evidence, and the Intelligent Contract audits whether the campaign reached durable Google ranking without black-hat manipulation before releasing payment.

## Why It Needs GenLayer

SEO performance is subjective, web-native, and money-bearing. A normal smart contract cannot read article pages, SERP evidence, rank tracking, backlink quality, and analytics sources, then decide whether the agency used durable white-hat SEO instead of short-lived spam. SEOBoost dies without GenLayer.

## Architecture

- `contracts/SEOBoost.py` stores campaign escrow, SEO evidence URLs, AI audit scores, status, and payout state.
- `audit_campaign` reads article, SERP, analytics, and backlink evidence with `gl.nondet.web.render`.
- AI scoring uses `gl.nondet.exec_prompt` and `gl.eq_principle.prompt_comparative` so validators compare the real audit decision and payout outcome, not exact wording.
- `frontend/` is a Next.js app using `genlayer-js` for wallet connection, contract writes, reads, status updates, and AI audit display.

## Flow

1. Create a campaign and lock reward.
2. Submit article, SERP, analytics, and backlink evidence.
3. Run the GenLayer white-hat SEO audit.
4. Release reward if the contract approves the agency.

## Local Setup

```bash
python -m unittest discover -s tests
cd frontend
npm install
npm run dev
```

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_CONTRACT_ADDRESS=0x8E2B3146eBd3d0FDa2b7D70C7ab0a4fa7Fa648eA
NEXT_PUBLIC_NETWORK=testnetAsimov
NEXT_PUBLIC_GENLAYER_RPC=
```

## Deploy

```bash
python -c "import ast; ast.parse(open('contracts/SEOBoost.py', encoding='utf-8').read())"
genlayer lint contracts/SEOBoost.py
genlayer deploy contracts/SEOBoost.py --name SEOBoost
```
