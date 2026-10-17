"""
run_all_tests.py - runs EVERY performance scenario for Form E one after another,
then prints the summary. Takes about 15 minutes. Start the app first, keep it
running, and avoid heavy use of the computer until it finishes.

    python run_all_tests.py

Needs locustfile.py and summarize_results.py in the same folder, and the
virtual environment with Locust active (prompt shows (venv)).
It also runs Bandit on the app's source if Bandit is installed (pip install bandit).
"""
import os
import subprocess
import sys

HOST = "http://127.0.0.1:8000"
RUNS = [  # (users, spawn rate per second, run time, file prefix)
    (1, 1, "2m", "baseline"),
    (10, 2, "3m", "load10"),
    (25, 5, "3m", "load25"),
    (50, 10, "3m", "load50"),
    (100, 20, "3m", "stress100"),
    (100, 100, "2m", "spike"),
]

os.makedirs("results", exist_ok=True)
for users, rate, t, prefix in RUNS:
    print(f"\n=== Running {prefix}: {users} users, {t} ===", flush=True)
    subprocess.run(
        [sys.executable, "-m", "locust", "-f", "locustfile.py", "--host", HOST, "--headless",
         "-u", str(users), "-r", str(rate), "-t", t,
         "--csv", f"results/{prefix}", "--html", f"results/{prefix}.html"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print("done", flush=True)

print("\n=== Performance summary ===")
subprocess.run([sys.executable, "summarize_results.py"])

print("\n=== Bandit (static analysis of the app source in the parent folder) ===")
try:
    subprocess.run([sys.executable, "-m", "bandit", "-r", "..", "-x", "../venv,../env,../Performance Testing",
                    "-f", "txt", "-o", "results/bandit.txt"], check=False)
    print("Bandit report saved to results/bandit.txt - open it and send the 'Run metrics' section.")
except Exception as e:
    print("Bandit not run:", e)