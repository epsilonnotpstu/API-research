#!/bin/bash
# R3b-এর বাকি কাজ এক command-এ শেষ করে (Codex-এর usage limit reset হওয়ার পর চালাবেন, ২০২৬-১১-২৪ রাত ১০:০৯-এর পরে)।
# ব্যবহার:  bash "R3_silent_breaking/collab/scripts/r3b_finish.sh"
# ধাপ:
#   1. GPT coder G5 আর G6 চালানো, অর্থাৎ আগের session resume। output না এলে নতুন run।
#   2. audit।
#   3. দুজনেই ৬০টি row লিখেছে কিনা যাচাই।
#   4. output freeze।
#   5. frozen scorer দিয়ে একবার scoring।
#   6. git commit আর push, co-author লাইন ছাড়া।
# কোনো ধাপ ব্যর্থ হলে script থেমে যায় এবং কারণ দেখায়। পরের কাজ (paper-এ যোগ করা) পরে Claude বা Codex-কে দিন।
set -uo pipefail
B="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$B" || exit 2
L="$B/collab/logs"; D="$B/packages/r3b_blind"
rows(){ [ -f "$D/codes_$1.csv" ] && /usr/bin/python3 -I -B -c "import csv,sys; print(len(list(csv.DictReader(open(sys.argv[1], encoding='utf-8-sig')))))" "$D/codes_$1.csv" || echo 0; }

echo "== 1. GPT coders (G5, G6)"
if [ "$(rows G5)" != 60 ] || [ "$(rows G6)" != 60 ]; then
  bash collab/scripts/r3b_launch_gpt.sh resume 1 G5 G6
fi
for g in G5 G6; do
  if [ "$(rows $g)" != 60 ]; then
    echo "   $g resume থেকে output আসেনি; নতুন run চালাচ্ছি"
    mv "$L/R3b_$g.log" "$L/R3b_${g}_first_limit.log" 2>/dev/null
    (cd "$D" && codex exec -m gpt-6.1-sol -c model_reasoning_effort=high -s workspace-write -C "$D" -o "$L/R3b_${g}_last.md" \
      "You are blind coder $g. YOUR_ID=$g. Your first command must be: cat TASK_R3b.md. Then follow TASK_R3b.md in this directory exactly. Do not read anything outside this directory." \
      > "$L/R3b_$g.log" 2>&1 < /dev/null)
  fi
done
for g in G5 G6; do
  n=$(rows $g); echo "   $g rows: $n"
  [ "$n" = 60 ] || { echo "থামলাম: $g-এর ৬০টি row নেই। Codex limit বা log দেখুন: $L/R3b_$g*.log"; exit 1; }
done

echo "== 2. audit"
/usr/bin/python3 -I -B collab/scripts/r3b_audit.py | head -4

echo "== 3. output freeze"
bash collab/scripts/r3b_freeze_outputs.sh || { echo "থামলাম: output freeze ব্যর্থ"; exit 1; }

echo "== 4. scoring (একবারই)"
if [ -e plan/r3b_score_output.txt ]; then echo "থামলাম: plan/r3b_score_output.txt আগে থেকেই আছে (score একবারই হবে)"; exit 1; fi
/usr/bin/python3 -I -B plan/score_r3b.py --out plan/r3b_scores.csv > plan/r3b_score_output.txt 2>&1
rc=$?; cat plan/r3b_score_output.txt
[ $rc = 0 ] || { echo "থামলাম: scorer error (সম্ভবত কোনো coder অবৈধ মান লিখেছে)। R4b-এর D1-এর মতো নথিভুক্ত normalisation লাগবে; Claude বা Codex-কে বলুন।"; exit 1; }

echo "== 5. commit"
cd "$B/.." && git add R3_silent_breaking/packages R3_silent_breaking/plan R3_silent_breaking/collab/scripts && \
  git commit -q -m "R3b scored once (full-contract specification coding): see plan/r3b_score_output.txt" && git push -q origin main && \
  git log -1 --format='commit %h by %an'
echo "R3b সম্পূর্ণ। এবার plan/r3b_score_output.txt-এর ফল R3 paper-এ (§4.4 আর §6) যোগ করতে হবে।"
