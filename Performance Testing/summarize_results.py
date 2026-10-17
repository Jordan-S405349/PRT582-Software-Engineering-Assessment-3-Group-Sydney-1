"""
summarize_results.py - turns your Locust CSV files into the numbers for Form E.

Run it from the same folder as locustfile.py AFTER you have run the tests:
    python summarize_results.py

It reads the files in the 'results' folder:
    baseline_stats.csv, load10_stats.csv, load25_stats.csv,
    load50_stats.csv, stress100_stats.csv, spike_stats.csv (optional)
and prints one line per scenario in the same order as Table 1 in the report,
plus the page-by-page numbers for the 25-user run (Table 2).
Copy each value into the yellow cell with the same column heading.
"""
import csv
import os

RESULTS = "results"
SCENARIOS = [  # (label, users, file prefix)
    ("P1 Baseline", 1, "baseline"),
    ("P2 Normal load", 10, "load10"),
    ("P3 Peak load", 25, "load25"),
    ("P4 Heavy load", 50, "load50"),
    ("P5 Stress", 100, "stress100"),
    ("P6 Spike", 100, "spike"),
]
# pass criteria used in the report (section A1)
MAX_AVG_MS, MAX_P95_MS, MAX_FAIL_PCT = 1000, 3000, 1.0


def read_stats(prefix):
    path = os.path.join(RESULTS, prefix + "_stats.csv")
    if not os.path.exists(path):
        return None
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(row, key):
    try:
        return float(row[key])
    except (KeyError, ValueError, TypeError):
        return 0.0


def verdict(avg, p95, fail_pct, label):
    if label.startswith("P5"):  # stress: finding the limit, not a pass/fail target
        return "Limit test (see analysis)"
    ok = avg <= MAX_AVG_MS and p95 <= MAX_P95_MS and fail_pct < MAX_FAIL_PCT
    return "Pass" if ok else "Fail"


print("TABLE 1 - overall results (paste into the yellow cells, left to right)")
print("Scenario | Users | Total requests | Avg (ms) | 95th pct (ms) | Max (ms) | Req/s | Failures % | Verdict")
print("-" * 100)
for label, users, prefix in SCENARIOS:
    rows = read_stats(prefix)
    if rows is None:
        print(f"{label} | {users} | (no file results/{prefix}_stats.csv - run this scenario first)")
        continue
    agg = next((r for r in rows if r["Name"] == "Aggregated"), rows[-1])
    total, fails = num(agg, "Request Count"), num(agg, "Failure Count")
    avg, p95 = num(agg, "Average Response Time"), num(agg, "95%")
    mx, rps = num(agg, "Max Response Time"), num(agg, "Requests/s")
    fail_pct = (fails / total * 100) if total else 0.0
    print(f"{label} | {users} | {total:.0f} | {avg:.0f} | {p95:.0f} | {mx:.0f} | {rps:.1f} | {fail_pct:.2f} | "
          f"{verdict(avg, p95, fail_pct, label)}")

print("\nTABLE 2 - page by page at 25 users (load25)")
print("Page / request | Requests | Avg (ms) | 95th pct (ms) | Failures %")
print("-" * 100)
rows = read_stats("load25")
if rows is None:
    print("(no file results/load25_stats.csv - run the 25-user scenario first)")
else:
    for r in rows:
        if r["Name"] == "Aggregated":
            continue
        total, fails = num(r, "Request Count"), num(r, "Failure Count")
        pct = (fails / total * 100) if total else 0.0
        print(f"{r['Name']} | {total:.0f} | {num(r, 'Average Response Time'):.0f} | {num(r, '95%'):.0f} | {pct:.2f}")

print("\nHINTS FOR THE ANALYSIS PARAGRAPH")
prev = None
for label, users, prefix in SCENARIOS[:5]:
    rows = read_stats(prefix)
    if not rows:
        continue
    agg = next((r for r in rows if r["Name"] == "Aggregated"), rows[-1])
    avg = num(agg, "Average Response Time")
    note = ""
    if prev is not None and prev > 0 and avg > 2 * prev:
        note = "  <-- average more than doubled: possible slow-down point"
    print(f"{users:>4} users: avg {avg:.0f} ms{note}")
    prev = avg
