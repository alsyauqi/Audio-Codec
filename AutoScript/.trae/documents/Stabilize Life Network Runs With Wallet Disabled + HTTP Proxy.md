## Outcome
- Run tasks reliably with wallets disabled, using a stable residential HTTP proxy.
- Remove intermittent writer/token issues and avoid proxy-related failures.

## Config Changes
1) a:\Bawaan\MeoMunDep\LN\configs.json
- Set: `proxyMode: "static"`, `rotateProxy: false`, `skipInvalidProxy: true`
- Keep: `doTasks: true`, `howManyAccountsRunInOneTime: 1`, `timeToRestartAllAccounts: 300`
- Ensure: `connectWallets: false`
- Optional softening: `delayEachAccount: [3,6]` to reduce rate-limits

2) a:\Bawaan\MeoMunDep\LN\proxies.txt
- Require 1–3 lines, HTTP only, one per line, e.g.: `http://user:pass@host:port`
- Remove SOCKS entries; they produced `HostUnreachable` in your logs

## Token Handling
- Keep valid `datas.txt` tokens (one per line)
- Keep `tokens.json` present; do not clear between runs so caching works
- Create `a:\Bawaan\MeoMunDep\LN\logs` to satisfy internal writer and eliminate `writeQueue` errors

## Environment Hygiene
- Ensure we run from `a:\Bawaan\MeoMunDep\LN` (run.bat already does `cd /d %~dp0`)
- Optional: rename `A:\Bawaan\node_modules` (Admin) to prevent npm prefix confusion; or set `npm config set prefix "C:\Users\Administrator\AppData\Roaming\npm"`

## Verification Steps
1) Update configs as above and normalize `proxies.txt`
2) Create `logs` folder (if missing)
3) Run `node meomundep.js` from `LN`
4) Confirm in logs:
   - `Proxy: ACTIVE` with proxy IP shown
   - No new `writeQueue` errors after the first run
   - Wallet steps are skipped (since `connectWallets: false`)
   - Task lines proceed; “Not in time to Check-in!” can remain (server time-gated)
5) If tasks still error, swap to a different residential HTTP proxy and rerun

## Rollback
- All changes are local file edits; we can restore previous configs and proxies with one click.

## Notes
- Check-in is server time-gated; failing that line does not block other tasks
- If later you want wallets, paste keys in the exact format expected by the bot, then set `connectWallets: true`