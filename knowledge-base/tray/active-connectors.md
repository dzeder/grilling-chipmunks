# Active Tray Connectors

Not yet synced from workspace. Run with `--workspace` flag and `TRAY_MASTER_TOKEN` set:

```bash
export TRAY_MASTER_TOKEN=$(aws secretsmanager get-secret-value --secret-id tray/master-token --query SecretString --output text)
bash scripts/sync-tray-connectors.sh --apply --workspace
```

## How to populate

1. Set `TRAY_MASTER_TOKEN` (from AWS Secrets Manager)
2. Run: `bash scripts/sync-tray-connectors.sh --apply --workspace`
3. Commit the generated files
