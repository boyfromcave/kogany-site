# static/data — the status feeds the pages read

`dashboard.json` feeds the vault dashboard (`data-live` in `content/vault.html`). The committed file
is the build-time placeholder. The testnet status service (ycash-infra `charts/ycash-testnet`,
`status`) will publish the live one at the same path.

```json
{ "status": "live | configured | stale",
  "generated": "ISO 8601 time the values were read",
  "networks": { "yb-fast": { ... }, "yb-slow": { ... } } }
```

Per network: `testnet_state`, `testnet_height` (rollout stage), `height`, `best_hash`,
`header_age`, `median_interval`, `interval_note`, `vaults`, `yed_supply`, `seats`, `seats_note`,
`activation`, `faucet_url`, `viz_url`, and `blocks` (newest first: `{height, hash, time}`).

Rules the page follows: only `"status": "live"` clears the warning and enables the faucet and
visualizer buttons; a `null` value leaves the build-time placeholder in place; nothing is inferred.
