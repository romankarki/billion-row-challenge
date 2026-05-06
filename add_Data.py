#!/usr/bin/env python3
"""
Generate synthetic weather rows (city;temperature) for load testing.

Picks random cities from data/weather_stations.csv and random temperatures in [-40, 100].
Default: 1_000_000_000 rows -> data/weather_Stattion.csv

Expect tens of GB of disk space and long runtime for 1e9 rows in CPython; use --rows for a dry run.
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path


def load_cities(stations_path: Path) -> list[str]:
    cities: list[str] = []
    with stations_path.open(encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            semi = s.find(";")
            name = s[:semi] if semi != -1 else s
            if name:
                cities.append(name)
    if not cities:
        sys.exit(f"No cities found in {stations_path}")
    return cities


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--stations",
        type=Path,
        default=Path("data/weather_stations.csv"),
        help="Source CSV with city;temperature header lines (comments # allowed)",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("data/weather_Stattion.csv"),
        help="Output file (one row per line: City;temp)",
    )
    p.add_argument(
        "--rows",
        type=int,
        default=1_000_000_000,
        help="Number of rows to write",
    )
    p.add_argument("--temp-min", type=float, default=-40.0)
    p.add_argument("--temp-max", type=float, default=100.0)
    p.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility")
    p.add_argument(
        "--batch",
        type=int,
        default=50_000,
        help="Lines buffered before each write (tune for throughput)",
    )
    p.add_argument(
        "--progress-every",
        type=int,
        default=10_000_000,
        help="Print progress after this many rows completed",
    )
    args = p.parse_args()

    if args.rows < 0:
        sys.exit("--rows must be non-negative")
    if args.batch <= 0:
        sys.exit("--batch must be positive")
    if args.temp_min >= args.temp_max:
        sys.exit("--temp-min must be less than --temp-max")

    cities = load_cities(args.stations)
    n = len(cities)
    rng = random.Random(args.seed)
    lo, hi = float(args.temp_min), float(args.temp_max)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    rows_done = 0
    last_report_bucket = -1
    batch: list[str] = []
    append = batch.append
    randrange = rng.randrange
    uniform = rng.uniform

    # 8 MiB stdio buffer; batched writelines does the heavy lifting
    with args.output.open("w", encoding="utf-8", newline="\n", buffering=8 * 1024 * 1024) as out:
        for _ in range(args.rows):
            append(f"{cities[randrange(n)]};{uniform(lo, hi):.4f}\n")
            if len(batch) >= args.batch:
                out.writelines(batch)
                rows_done += len(batch)
                batch.clear()
                bucket = rows_done // args.progress_every
                if bucket > last_report_bucket:
                    last_report_bucket = bucket
                    elapsed = time.perf_counter() - t0
                    rate = rows_done / elapsed if elapsed > 0 else 0.0
                    print(
                        f"{rows_done:,} rows  {rate:,.0f} rows/s  elapsed {elapsed:,.1f}s",
                        flush=True,
                    )
        if batch:
            out.writelines(batch)
            rows_done += len(batch)

    elapsed = time.perf_counter() - t0
    rate = rows_done / elapsed if elapsed > 0 else 0.0
    print(
        f"Done: {rows_done:,} rows in {elapsed:,.1f}s ({rate:,.0f} rows/s) -> {args.output.resolve()}",
        flush=True,
    )


if __name__ == "__main__":
    main()
