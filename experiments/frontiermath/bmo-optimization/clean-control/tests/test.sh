#!/usr/bin/env bash
set -euo pipefail

if [[ -f /app/answer.txt ]] && ANSWER_TEXT=$(cat /app/answer.txt) \
  python3 -c 'import math, os, re, sys
s = os.environ["ANSWER_TEXT"].strip()[:1000]
for _ in range(10):
    old = s
    s = re.sub(r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"(\1)/(\2)", s)
    s = re.sub(r"\\sqrt\s*\{([^{}]*)\}", r"sqrt(\1)", s)
    s = s.replace(r"\cdot", "*")
    s = re.sub(r"e\s*\^\s*\{([^{}]*)\}", r"exp(\1)", s)
    s = s.replace(r"\left", "").replace(r"\right", "")
    if s == old:
        break
s = s.replace("^", "**").replace("{", "(").replace("}", ")")
s = re.sub(r"\s+", "", s)
s = re.sub(r"\[,;! ]", "", s)
s = re.sub(r"(?<=[0-9)])(?=(?:sqrt|exp)\()", "*", s)
if not re.fullmatch(r"[0-9A-Za-z_+*/().\\-]+", s):
    sys.exit(1)
try:
    value = eval(s, {"__builtins__": {}}, {"sqrt": math.sqrt, "exp": math.exp, "e": math.e})
except Exception:
    sys.exit(1)
expected = math.sqrt(3)/36 + math.sqrt(3)/6*math.exp(-20*math.sqrt(3)-1/6)
sys.exit(0 if math.isfinite(value) and abs(value-expected) <= 1e-12 else 1)' ; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
