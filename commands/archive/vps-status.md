Check VPS service status and health.

Run this SSH command to get a full status overview:

```bash
ssh root@104.218.100.67 "echo '=== Services ===' && systemctl list-units --type=service --state=running --no-pager | grep -E 'nginx|oauth|marzban' && echo && echo '=== Ports ===' && ss -tlnp | grep -E '8443|9100|8000|7891|443' && echo && echo '=== Disk ===' && df -h / && echo && echo '=== Memory ===' && free -h && echo && echo '=== Docker ===' && docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null"
```

$ARGUMENTS may specify a service name to check specifically (e.g., "oauth-proxy", "nginx").
If a specific service is given, also show its recent logs: `journalctl -u <service> --no-pager -n 20`
