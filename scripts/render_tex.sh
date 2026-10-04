#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: scripts/render_tex.sh [--open] [--png] INPUT.tex [OUTPUT_DIR]

Compile INPUT.tex with Tectonic. The PDF is written to OUTPUT_DIR (default:
renders/<input-basename>). --png creates a Quick Look PNG preview when the
macOS qlmanage utility is available. --open opens the resulting PDF.
EOF
  exit 2
}

open_pdf=0
make_png=0
while (($#)); do
  case "$1" in
    --open) open_pdf=1; shift ;;
    --png) make_png=1; shift ;;
    -h|--help) usage ;;
    -*) echo "unknown option: $1" >&2; usage ;;
    *) break ;;
  esac
done

[[ $# -ge 1 && $# -le 2 ]] || usage
input=$1
[[ -f "$input" ]] || { echo "TeX source not found: $input" >&2; exit 1; }
command -v tectonic >/dev/null 2>&1 || {
  echo "tectonic is required; install it with: brew install tectonic" >&2
  exit 1
}

input_abs=$(cd "$(dirname "$input")" && pwd)/$(basename "$input")
stem=$(basename "${input_abs%.tex}")
if (($# == 2)); then
  output_dir=$2
else
  repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
  if [[ "$input_abs" == "$repo_root/"* ]]; then
    output_key="${input_abs#"$repo_root/"}"
    output_key="${output_key%.tex}"
    output_key="${output_key//\//__}"
  else
    output_key="$stem"
  fi
  output_dir="$repo_root/renders/$output_key"
fi
mkdir -p "$output_dir"

tectonic --color never --synctex --outdir "$output_dir" "$input_abs"
pdf="$output_dir/$stem.pdf"
[[ -f "$pdf" ]] || { echo "Tectonic did not produce $pdf" >&2; exit 1; }

if ((make_png)); then
  if command -v qlmanage >/dev/null 2>&1; then
    qlmanage -t -s 1800 -o "$output_dir" "$pdf" >/dev/null 2>&1 || true
    preview=$(find "$output_dir" -maxdepth 1 -name "$stem.pdf.png" -print -quit)
    if [[ -n "$preview" ]]; then
      mv "$preview" "$output_dir/$stem.png"
    fi
  else
    echo "qlmanage is unavailable; PDF was still created" >&2
  fi
fi

if ((open_pdf)); then
  open "$pdf"
fi
printf '%s\n' "$pdf"
