# SEOBoost V2

SEOBoost is a GenLayer-native performance escrow for white-hat SEO work. A client
locks native GEN, an agency submits constrained independent evidence, and a
comparative AI jury determines whether the campaign earned payment or should be
refunded.

## Why GenLayer

The payment decision depends on subjective web evidence: topical depth, durable
search ranking, natural backlinks, conversion value, and manipulation risk. A
normal deterministic contract cannot read those sources or fairly adjudicate the
result. Removing GenLayer removes the escrow's decision engine.

## Contract lifecycle

1. `create_campaign` is payable. `gl.message.sender_address` becomes the immutable
   client and `gl.message.value` becomes the exact escrow reward.
2. `submit_evidence` is agency-only. The article must match the locked target
   domain; SERP, analytics, and backlink URLs must use approved independent hosts.
3. `audit_campaign` reads every source with `web.render`, evaluates it with
   `exec_prompt`, and uses `prompt_comparative` to compare the substantive escrow
   outcome.
4. One seven-day evidence revision is available after an inconclusive first audit.
5. `release_reward` transfers approved native GEN to the recorded agency.
6. `refund_reward` transfers rejected escrow, expired evidence windows, or expired
   revision windows to the recorded client.

Invalid payable inputs raise `gl.vm.UserError`, preventing a rejected campaign from
silently retaining attached value.

## Frontend

The Next.js frontend uses `genlayer-js` on Studionet and separates each function
into a focused route:

- `/campaigns` - bounded live registry
- `/campaigns/new` - payable campaign creation
- `/campaigns/[id]` - live campaign and audit record
- `/campaigns/[id]/evidence` - agency evidence submission
- `/campaigns/[id]/audit` - AI audit
- `/campaigns/[id]/release` - approved payout
- `/campaigns/[id]/refund` - client refund
- `/contract` - runtime deployment selector and live connection proof

Before every write, the SDK switches the wallet to the configured GenLayer network
and treats only `FINISHED_WITH_RETURN` as successful execution.

## Local verification

```bash
python -m unittest discover -s tests -v
python -c "import ast, pathlib; ast.parse(pathlib.Path('contracts/SEOBoost.py').read_text())"
cd frontend
npm install
npm run lint
npm run build
npm run dev
```

Open `http://localhost:3042`.

## Deployment

Deploy `contracts/SEOBoost.py` to GenLayer Studio, then either configure
`NEXT_PUBLIC_CONTRACT_ADDRESS` or enter the address at runtime on `/contract`.

```env
NEXT_PUBLIC_CONTRACT_ADDRESS=0xD0EaC97F329FC2e633c0b98Aa237E7b1940a2e2A
NEXT_PUBLIC_NETWORK=studionet
NEXT_PUBLIC_GENLAYER_RPC=
```

Current SEOBoost V2 Studionet deployment:
`0xD0EaC97F329FC2e633c0b98Aa237E7b1940a2e2A`.
