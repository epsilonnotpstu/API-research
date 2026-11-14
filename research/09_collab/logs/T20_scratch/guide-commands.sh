E5="$PWD/08_experiments/E5_codemut"
MUT="$E5/work/market-drop-null_20261114T113144Z"
# External execution: control then mutant for each seed; default seeds 1 2 3.
"$E5/run_pair.sh" "$MUT"
# Alternatively select canonical nonnegative seeds explicitly, e.g. 1 3.
# "$E5/run_pair.sh" "$MUT" 1 3
# Own saved-evidence analysis, both oracles, after pair validation:
"$E5/analyse_pair.sh" "$MUT"
# All directories with work/*/runs.tsv; creates/replaces only this top-level CSV.
/usr/bin/python3 -I -B "$E5/summarise_e5.py"
# Or summarise named pairs to a chosen output:
# /usr/bin/python3 -I -B "$E5/summarise_e5.py" "$MUT" --out "$E5/e5_summary.csv"

/usr/bin/python3 -I -B "$E5/validate_pair.py" "$CONTROL_RUN" "$MUTANT_RUN" "$MUT"

/usr/bin/python3 -I -B -m unittest discover \
  -s 08_experiments/E5_codemut -p 'test_*.py' -v
bash -n 08_experiments/E5_codemut/run_pair.sh
bash -n 08_experiments/E5_codemut/analyse_pair.sh
