# Results figures

These figures summarize the seven-minute replicate series from the published
local GPT-6-sol traces. They are descriptive evidence for the writeup, not
results from the public OpenRouter reproduction route.

## Verifier pass rates

![Forest plot of verifier pass rates across the seven-minute conditions](../renders/pass-rate-forest.svg)

Dots show the fraction of scored trials with verifier reward `1`. Horizontal
lines are two-sided 95% Wilson score intervals. A reward of `1` is counted as
a pass even when Harbor also recorded a timeout, because both fields are present
in those trial records. The single infrastructure failure in the clean public
condition has no reward and is excluded from its denominator.

| Condition | Verifier passes | Scored trials |
| --- | ---: | ---: |
| Answer artifact, host-tool lane | 10 | 10 |
| URL artifact, host-tool lane | 7 | 10 |
| URL artifact, public container | 5 | 10 |
| Clean control, host-tool lane | 3 | 10 |
| Clean control, public container | 2 | 4 |
| FrontierMath named, URL, public container | 3 | 10 |
| Source cue, URL, public container | 1 | 5 |

The *host-tool lane* denotes the historical local setup in which host-side
web tools were available. It does not mean every trial used them, nor that the
container was fully offline. The *public container* label identifies task
variants with container network access. The earlier one-off pilot runs are
excluded from these replicate figures.

## Individual trials

![Grid of pass, fail, timeout, and setup-failure outcomes by replicate](../renders/trial-outcomes.svg)

Each symbol is one published trial. A diamond means the verifier passed while
Harbor also reported a timeout. The gray cross is the setup failure excluded
from the pass-rate denominator.

## Selected contrasts

![Exploratory differences in pass rates for selected condition pairs](../renders/condition-contrasts.svg)

Dots show the difference in observed pass rates, in percentage points. Lines
are 95% Newcombe hybrid-score intervals for two proportions. The comparisons
are exploratory: sample sizes are small, run conditions were developed over
time, and the plots do not establish a causal effect of artifact exposure or
instruction framing. Verifier success alone does not establish that an agent
used an artifact; the interaction logs support that separate analysis.

## Regenerate

From the repository root:

```bash
python -m pip install -e '.[plots]'
python scripts/plot_results.py
```

The script reads only `traces/local-gpt-6-sol/**/metadata.json` and writes
both SVG and PNG versions under `renders/`. The checked-in figures were rendered
with Matplotlib 3.10.8.

## Problem image

![Typeset BMO optimization problem](../renders/problem.png)

This PNG was typeset from the published
[`clean-control/environment/problem.tex`](../experiments/frontiermath/bmo-optimization/clean-control/environment/problem.tex)
fixture, with a smaller page size for viewing. The mathematical text is the
same in the artifact variants; LaTeX comments do not appear in the image.
