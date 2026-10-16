"""Runs problem_1.py ... problem_7.py and checks each printed line against the
'# Expected:' comments in that file. Usage:  python run_all_tests.py"""
import re
import subprocess
import sys
from pathlib import Path

folder = Path(__file__).parent
failures = 0
for i in range(1, 8):
    path = folder / f"problem_{i}.py"
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
    if result.returncode:
        print(f"problem_{i}.py: ERROR\n{result.stderr}")
        failures += 1
        continue
    actual = result.stdout.splitlines()
    expected = [re.sub(r"^# Expected: ", "", line.strip())
                for line in path.read_text().splitlines()
                if line.strip().startswith("# Expected:")]
    status = "PASS" if actual == expected else "FAIL"
    failures += status == "FAIL"
    print(f"problem_{i}.py: {status} ({len(actual)} lines checked)")

print("\nAll good!" if not failures else f"\n{failures} problem(s) failed")
sys.exit(failures)
