# static/data — the status feeds the pages read

`dashboard.json` feeds the vault dashboard (`data-live` in `content/vault.html`). The committed file
is a fixed, dated testnet snapshot (`"status": "configured"`, read by hand from a testnet node; the
Yellowback lead architect's decision: no live feed for now). The testnet status service
(ycash-infra `charts/ycash-testnet`, `status`) may later publish a live one at the same path.

```json
{ "status": "live | configured | stale",
  "generated": "ISO 8601 time the values were read",
  "networks": { "yb-fast": { ... }, "yb-slow": { ... } } }
```

Per network: `testnet_state`, `testnet_height` (rollout stage), `height`, `best_hash`,
`header_age`, `median_interval`, `interval_note`, `vaults`, `vaults_note`, `yed_supply`, `yed_note`,
`seats`, `seats_note`,
`activation`, `faucet_url`, `viz_url`, and `blocks` (newest first: `{height, hash, time}`).

Rules the page follows: only `"status": "live"` clears the warning and enables the faucet and
visualizer buttons; any other status keeps the "Not live" warning and labels the page "Testnet
snapshot of `generated`, not a live feed" (`"live"` shows "Updated `generated`"); `testnet_state`
`"Active"` marks the rollout's testnet stage done; a `null` value leaves the build-time placeholder
in place; nothing is inferred.
