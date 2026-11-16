#!/bin/bash
# metadata-only check: no commit content is read
while read src repo; do
  case "$src" in \#*|"") continue;; esac
  m=$(gh api "repos/$repo" --jq '[.full_name,.stargazers_count,.language,(.license.spdx_id//"NONE"),.archived,.fork,.size,.default_branch,.created_at[:7],.pushed_at[:7]]|@tsv' 2>/dev/null) || { echo -e "$src\t$repo\tERROR"; continue; }
  br=$(echo "$m" | cut -f8)
  specs=$(gh api "repos/$repo/git/trees/$br?recursive=1" --jq '.tree[].path' 2>/dev/null | grep -iE '(^|/)[^/]*(openapi|swagger)[^/]*\.(ya?ml|json)$|(^|/)(openapi|swagger)/[^/]*\.(ya?ml|json)$' | grep -viE '(^|/)(test|tests|testdata|example|examples|sample|samples|fixture|fixtures|vendor|node_modules|third_party|e2e|mock|mocks)(/|$)' | wc -l)
  commits=$(gh api -i "repos/$repo/commits?per_page=1&sha=$br" 2>/dev/null | grep -i '^link:' | grep -oE 'page=[0-9]+>; rel="last"' | grep -oE '[0-9]+')
  echo -e "$src\t$m\t$specs\t${commits:-?}"
done < seed.txt
