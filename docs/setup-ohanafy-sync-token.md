# Setting Up OHANAFY_SYNC_TOKEN

The `sync-ohanafy-index.yml` workflow needs read access to private repos in the Ohanafy GitHub org to generate source indexes for the 10 SKU expert skills.

## 1. Create a Fine-Grained PAT

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Click **Generate new token**
3. **Token name:** `lyon-sync-readonly`
4. **Expiration:** 90 days (set a calendar reminder to rotate)
5. **Resource owner:** Select the **Ohanafy** organization
6. **Repository access:** All repositories (or select the 20 OHFY-* repos listed in `docs/upstream-dependencies.md`)
7. **Permissions:**
   - Contents: **Read-only**
   - Metadata: **Read-only**
8. Click **Generate token** and copy it immediately

## 2. Add as Repo Secret

1. Go to `github.com/dzeder/daniels-ohanafy` → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. **Name:** `OHANAFY_SYNC_TOKEN`
4. **Value:** Paste the PAT from step 1
5. Click **Add secret**

## 3. Verify

Manually trigger the sync workflow:

```bash
gh workflow run sync-ohanafy-index.yml
```

Check the workflow run — it should no longer show the "OHANAFY_SYNC_TOKEN secret is not set" warning.

## 4. Rotation

Fine-grained tokens expire. Before expiry:

1. Generate a new token following step 1
2. Update the repo secret following step 2
3. Verify following step 3
4. Set the next rotation reminder

## Referenced By

- `.github/workflows/sync-ohanafy-index.yml` (line 27)
- `docs/roadmap.md` (near-term item)
- `scripts/sync-ohanafy-index.sh` (uses `GH_TOKEN` env var)
