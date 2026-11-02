# static/data — the status feeds the pages read

`testnet.json` is the testnet page's feed (`data-live` in `content/testnet.html`). The committed file
is the build-time configuration. A collector on the testnet cluster (the `status` service in
ycash-infra's `charts/ycash-testnet`) will replace it with live readings.

| Field | Meaning |
|---|---|
| `status` | `live` only when every value was just read from a node; anything else keeps the page's warning up |
| `generated` | when the values were read (ISO 8601) |
| `networks[].id` | `yb-fast` or `yb-slow`, matching `data-network` on the page |
| `state` | `up`, `degraded` or `not deployed` |
| `height`, `vault` | tip height and whether Vault is active at the next block; `null` shows "unavailable" |
| `faucet_url` | set only once the network's faucet is live and checked; the page shows its button then |

The page never infers a value it isn't given: missing values show "unavailable".
