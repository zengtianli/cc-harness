Manage Cloudflare DNS records for tianlizeng.cloud.

Read `~/.personal_env` to get CF_API_TOKEN, CF_ZONE_ID, and CF_ACCOUNT_ID.
Use the CF API v4 (https://api.cloudflare.com/client/v4/).

Auth headers: `-H "Authorization: Bearer $CF_API_TOKEN"`

Common operations based on $ARGUMENTS:

**list** — List all DNS records:
```bash
curl -s -H "Authorization: Bearer $CF_API_TOKEN" "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" | python3 -c "import json,sys; [print(f'{r[\"name\"]:40s} {r[\"type\"]:5s} {r[\"content\"]:20s} proxied={r[\"proxied\"]}') for r in json.load(sys.stdin)['result']]"
```

**add <subdomain>** — Add A record pointing to VPS (104.218.100.67), proxied, then add to Origin Rule (port 8443):
1. POST dns_records with type=A, name=subdomain, content=VPS_IP, proxied=true
2. GET the origin rules ruleset, append the new hostname to the existing expression
3. PATCH the ruleset rule

**delete <subdomain>** — Find and DELETE the DNS record by name.

Always confirm before destructive operations (delete).
