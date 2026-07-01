# SEOBoost Deployment Notes

Validate:

```bash
python -c "import ast; ast.parse(open('contracts/SEOBoost.py', encoding='utf-8').read())"
genlayer lint contracts/SEOBoost.py
```

Deploy:

```bash
genlayer deploy contracts/SEOBoost.py --name SEOBoost
```

Wire the returned address into the frontend:

```bash
NEXT_PUBLIC_CONTRACT_ADDRESS=0x...
NEXT_PUBLIC_NETWORK=testnetAsimov
```
