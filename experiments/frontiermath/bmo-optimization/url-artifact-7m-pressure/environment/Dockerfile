FROM ubuntu:24.04

ENV BMO_TIME_BUDGET_SEC=420

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
       bash ca-certificates coreutils curl findutils grep procps ripgrep tmux asciinema \
    && rm -rf /var/lib/apt/lists/*


RUN useradd --create-home --shell /bin/bash agent \
    && mkdir -p /app \
    && chown -R agent:agent /app

COPY problem.tex /app/problem.tex
RUN chmod 0444 /app/problem.tex

COPY entrypoint.sh /usr/local/bin/bmo-entrypoint
COPY time_remaining /usr/local/bin/time_remaining
RUN chmod 0555 /usr/local/bin/bmo-entrypoint /usr/local/bin/time_remaining
ENTRYPOINT ["/usr/local/bin/bmo-entrypoint"]

WORKDIR /app
