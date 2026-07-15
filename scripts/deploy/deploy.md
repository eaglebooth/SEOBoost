# SEOBoost V2 deployment

1. Run the local gates from the repository root:

```bash
python -m unittest discover -s tests -v
python -c "import ast, pathlib; ast.parse(pathlib.Path('contracts/SEOBoost.py').read_text())"
```

2. Deploy `contracts/SEOBoost.py` in GenLayer Studio on Studionet.
3. Verify `get_escrow_state` returns JSON from the new address.
4. Open `/contract` in the local frontend, enter the address, and sync it.
5. Test with separate client and agency wallets:
   create payable campaign, submit trusted evidence, audit, then payout or refund.
6. Only after those writes succeed, set the production environment:

```env
NEXT_PUBLIC_CONTRACT_ADDRESS=0xD0EaC97F329FC2e633c0b98Aa237E7b1940a2e2A
NEXT_PUBLIC_NETWORK=studionet
NEXT_PUBLIC_GENLAYER_RPC=
```
