"""Utilities for connecting Moon Dev AI agents to the Jesse trading framework.

This module keeps Moon Dev code and Jesse codebases separate while allowing you
to sync strategies and launch backtests without leaving this repository.
"""

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


DEFAULT_JESSE_ENV_VAR = "JESSE_PROJECT_PATH"


def resolve_jesse_path(cli_value: Optional[str]) -> Path:
    """Return the path to the Jesse project, preferring CLI over env vars."""
    if cli_value:
        path = Path(cli_value).expanduser().resolve()
    else:
        env_value = os.getenv(DEFAULT_JESSE_ENV_VAR)
        if not env_value:
            raise ValueError(
                "Jesse project path not provided. Set JESSE_PROJECT_PATH or pass --jesse-path."
            )
        path = Path(env_value).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Jesse project not found at {path}")

    expected_files = {"config.py", "routes.py", "strategies"}
    missing = [name for name in expected_files if not (path / name).exists()]
    if missing:
        raise FileNotFoundError(
            f"Path {path} is missing Jesse project files: {', '.join(missing)}"
        )

    return path


def ensure_jesse_cli_available() -> None:
    """Ensure the Jesse CLI is available on the PATH.

    Raises:
        FileNotFoundError: If the ``jesse`` executable cannot be located.
    """

    if shutil.which("jesse") is None:
        raise FileNotFoundError(
            "Jesse CLI not found. Activate your Jesse virtual environment or install Jesse."
        )


def copy_strategy(strategy_name: str, jesse_path: Path, *, force: bool = False) -> Path:
    """Copy a strategy from src/strategies into the Jesse project's strategies folder.

    Args:
        strategy_name: File name of the strategy (without .py) in this repo's
            ``src/strategies`` directory.
        jesse_path: Path to the root of the Jesse project.
        force: When ``True``, overwrite an existing strategy file in the Jesse
            project. When ``False``, raise ``FileExistsError`` if the target
            already exists.
    """
    source = Path(__file__).resolve().parents[1] / "strategies" / f"{strategy_name}.py"
    if not source.exists():
        raise FileNotFoundError(f"Strategy not found: {source}")

    destination_dir = jesse_path / "strategies"
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / source.name

    if destination.exists() and not force:
        raise FileExistsError(
            f"Destination {destination} already exists. Re-run with --force to overwrite."
        )

    shutil.copy2(source, destination)
    return destination


def run_backtest(jesse_path: Path, route_name: str, start_date: str, finish_date: str) -> None:
    """Invoke Jesse's backtest CLI from this repository."""
    command = [
        "jesse",
        "backtest",
        route_name,
        start_date,
        finish_date,
    ]
    subprocess.run(command, cwd=jesse_path, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bridge utilities for the Jesse framework")
    parser.add_argument(
        "--jesse-path",
        dest="jesse_path",
        help=f"Path to Jesse project (defaults to ${DEFAULT_JESSE_ENV_VAR})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser(
        "sync-strategy", help="Copy a strategy from this repo into the Jesse project"
    )
    sync_parser.add_argument("--name", required=True, help="Strategy filename without .py")
    sync_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the destination strategy file if it already exists",
    )

    backtest_parser = subparsers.add_parser("backtest", help="Run Jesse backtest")
    backtest_parser.add_argument("--route-name", required=True, help="Route alias from routes.py")
    backtest_parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    backtest_parser.add_argument("--finish", required=True, help="Finish date (YYYY-MM-DD)")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    jesse_path = resolve_jesse_path(args.jesse_path)

    if args.command == "sync-strategy":
        destination = copy_strategy(args.name, jesse_path, force=args.force)
        print(f"Synced strategy to {destination}")
    elif args.command == "backtest":
        ensure_jesse_cli_available()
        run_backtest(jesse_path, args.route_name, args.start, args.finish)
        print("Backtest completed via Jesse CLI")


if __name__ == "__main__":
    main()
