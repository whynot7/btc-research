# btc-research

Joint crypto strategy research between two humans and their AI agents.
Research only, no trading, no keys. Not investment advice.

| | |
|---|---|
| **Results** | [LEADERBOARD.md](LEADERBOARD.md) and the per-strategy reports in `results/<name>/report.md` |
| **How it works** | [harness/README.md](harness/README.md), the shared test bench |
| **Rules for the agents** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **Discussion** | GitHub Issues: one issue per idea (`Proposal: …`) |

## Strategies on the bench
- `v3`: BTC daily, long above SMA200 and EMA50, otherwise cash (Agent B / friend)
- `trendvol`: BTC+ETH 4h, EMA200 ±1 % band, long/short, vol-target 60 %, max 3x (Agent A / Gianluca)
- `ensemble_trend`: BTC daily, average of 6 SMA trend votes (20–250 days) (Agent A, proposal)

## For the humans
- Read the reports and issues. The agents propose and critique each other, you decide.
- A run starts automatically after every change. Commenting `/bench` in any issue starts one by hand.
- Nothing here trades. Moving a strategy to a live bot is a separate decision outside this repo.
