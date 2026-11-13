
"""
measure.py - measures workload statements in BigQuery with the cache OFF.

Usage (run from the folder holding the .sql files):
  python3 measure.py workload workload.sql before
  python3 measure.py tuning tuning.sql
  python3 measure.py workload workload_after.sql after

workload mode: for each "-- Question N" statement it reports the dry-run
  estimate, then RUNS real runs: bytes processed, bytes billed, and the
  median elapsed time. Statements that change data are followed by the
  undo statement found under "-- Put it back before the next measurement:"
  so every run measures the same data.
tuning mode: runs each statement in tuning.sql once and reports the
  one-time rebuild cost (bytes processed and elapsed time).

Uses the project set with: gcloud config set project YOUR_PROJECT_ID
Results are printed as a table and saved to results_<label>.csv.
"""
import csv
import os
import re
import statistics
import sys

from google.cloud import bigquery

RUNS = 3
MAX_BYTES_BILLED = 1_000_000_000  # safety cap per real run (1 GB)

client = bigquery.Client(location="US")


def mb(n):
    return round((n or 0) / 1_000_000, 2)


def estimate(sql):
    cfg = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    return client.query(sql, job_config=cfg).total_bytes_processed


def run_once(sql):
    cfg = bigquery.QueryJobConfig(
        use_query_cache=False, maximum_bytes_billed=MAX_BYTES_BILLED
    )
    job = client.query(sql, job_config=cfg)
    job.result()
    if job.cache_hit:
        print("  WARNING: cache hit, this is not a measurement")
    elapsed = (job.ended - job.started).total_seconds()
    return job.total_bytes_processed, job.total_bytes_billed, elapsed, job.job_id


def strip_comments(text):
    return re.sub(r"--[^\n]*", "", text)


def split_statements(text):
    return [s.strip() for s in strip_comments(text).split(";") if s.strip()]


def find_undo(body):
    m = re.search(
        r"-- Put it back before the next measurement:\n((?:--[^\n]*\n?)+)", body
    )
    if not m:
        return None
    lines = [re.sub(r"^--\s?", "", l) for l in m.group(1).strip().splitlines()]
    return "\n".join(lines).strip().rstrip(";")


def measure_workload(path, label):
    text = open(path).read()
    parts = re.split(r"^-- Question (\d+)[^\n]*$", text, flags=re.M)
    rows = []
    for i in range(1, len(parts), 2):
        q = int(parts[i])
        body = parts[i + 1]
        stmts = split_statements(body)
        if not stmts:
            continue  # empty stub (e.g. unfilled Question 7-9 headings)
        sql = stmts[0]
        undo = find_undo(body)
        print(f"Q{q}: estimating...")
        est = estimate(sql)
        times, processed, billed, job_id = [], 0, 0, ""
        for r in range(RUNS):
            processed, billed, elapsed, job_id = run_once(sql)
            times.append(elapsed)
            print(f"  run {r + 1}: {mb(processed)} MB processed, {elapsed:.2f} s")
            if undo:
                client.query(undo).result()
        rows.append(
            {
                "question": q,
                "estimate_MB": mb(est),
                "processed_MB": mb(processed),
                "billed_MB": mb(billed),
                "median_elapsed_s": round(statistics.median(times), 2),
                "runs_s": "/".join(f"{t:.2f}" for t in times),
                "last_job_id": job_id,
            }
        )
    return rows


def measure_tuning(path):
    text = open(path).read()
    rows = []
    for sql in split_statements(text):
        m = re.search(r"TABLE\s+(\S+)", sql)
        name = m.group(1) if m else sql[:40]
        print(f"{name}: estimating...")
        est = estimate(sql)
        processed, billed, elapsed, job_id = run_once(sql)
        print(f"  {mb(processed)} MB processed, {elapsed:.2f} s")
        rows.append(
            {
                "statement": name,
                "estimate_MB": mb(est),
                "processed_MB": mb(processed),
                "billed_MB": mb(billed),
                "elapsed_s": round(elapsed, 2),
                "job_id": job_id,
            }
        )
    return rows


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    mode, path = sys.argv[1], sys.argv[2]
    label = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(path)[0]
    rows = measure_tuning(path) if mode == "tuning" else measure_workload(path, label)
    if not rows:
        print("No statements found.")
        return
    out = f"results_{label}.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print()
    print(" | ".join(rows[0].keys()))
    for r in rows:
        print(" | ".join(str(v) for v in r.values()))
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()