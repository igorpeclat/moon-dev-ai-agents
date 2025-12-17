# Jesse Integration Guide

This guide explains how to connect the Moon Dev AI Agents repository to the [Jesse](https://github.com/jesse-ai/jesse) trading framework for research, backtesting, and live execution.

## Why Jesse?
- Mature Python framework with routing, risk controls, and vectorized backtesting
- Plug-and-play data pipelines and exchange connectors
- Lets you keep AI signal generation in this repo while delegating order lifecycle to Jesse

## Prerequisites
- Python 3.10+ and `pip`
- A clone of this repository
- A clone of [`jesse-ai/jesse`](https://github.com/jesse-ai/jesse) (referred to as the **Jesse project**)
- Optional: separate virtual environments for this repo and the Jesse project

## Setup Steps
1. **Clone Jesse next to this repo (recommended layout)**
   ```bash
   cd /workspace
   git clone https://github.com/jesse-ai/jesse
   ```

2. **Install Jesse dependencies**
   ```bash
   cd /workspace/jesse
   pip install -r requirements.txt
   ```

3. **Point Moon Dev agents to the Jesse project**
   - Set an environment variable so helper scripts know where your Jesse clone lives:
     ```bash
     export JESSE_PROJECT_PATH=/workspace/jesse
     ```

4. **Copy strategy files into Jesse**
   - Use the helper below to sync any strategy from `src/strategies/` into Jesse's `strategies/` directory while keeping the original source of truth in this repo.

5. **Run a Jesse backtest**
   - The helper also wraps `jesse backtest` so you can trigger runs without leaving this repo (see examples below).

## Helper Script
The script at `src/scripts/jesse_bridge.py` provides two workflows:

### 1) Sync a strategy into Jesse
```bash
python src/scripts/jesse_bridge.py sync-strategy --name moving_average --jesse-path $JESSE_PROJECT_PATH
```
- Copies `src/strategies/moving_average.py` into `<JESSE_PROJECT_PATH>/strategies/moving_average.py`
- Prevents overwriting Jesse routes or config files
- Use `--force` if you intentionally want to overwrite an existing strategy file in the Jesse project

### 2) Launch a Jesse backtest
```bash
python src/scripts/jesse_bridge.py backtest \
  --jesse-path $JESSE_PROJECT_PATH \
  --route-name BTC-USDT \
  --start 2023-01-01 \
  --finish 2023-12-31
```
- Wraps `jesse backtest` so you can trigger runs from this repository
- Uses your Jesse project's `routes.py` and data settings

## Best Practices
- Keep strategy logic in `src/strategies/` and use the sync helper to mirror into Jesse
- Version control both repositories independently; do **not** vendor the Jesse codebase into this repo
- Store API keys only in your Jesse project's environment files—never commit them
- Backtest first, then promote the same synced strategy to live trading via Jesse once results are validated

## Troubleshooting
- `JESSE_PROJECT_PATH` not set: export it or pass `--jesse-path` to the helper commands
- Missing data: follow Jesse's docs to import candles for your exchange before backtesting
- CLI errors: run the same `jesse backtest ...` command directly inside the Jesse project to confirm your environment
- "jesse: command not found": activate the virtual environment where you installed Jesse so the CLI is on your PATH

Happy trading—let Jesse handle execution while these agents handle research and signal generation!
