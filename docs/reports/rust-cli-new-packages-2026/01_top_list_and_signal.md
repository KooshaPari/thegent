# Rust CLI Libraries: Top Picks and Adoption Signals (2026)

Source: [libs.tech Rust CLI Libraries](https://libs.tech/rust/cli-libraries)

- **[atuinsh/atuin](https://github.com/atuinsh/atuin)** — 28K stars, last commit 11 hours ago, MIT license, 449 open issues, 779 forks, added 11 months ago. ([Source](https://libs.tech/rust/cli-libraries))\
  **Signal:** very high adoption with actively maintained shell-history platform.\
  **2026 guidance:** strong candidate for teams already using shell-history tooling; budget review of feature complexity before onboarding because issue queue is large.
- **[clap-rs/clap](https://github.com/clap-rs/clap)** — 16K stars, last commit 6 days ago, Apache 2.0 or MIT, 413 open issues, 1157 forks, added 11 months ago. ([Source](https://libs.tech/rust/cli-libraries))\
  **Signal:** industry-standard parser with high contributor activity and dual licensing.\
  **2026 guidance:** safest baseline for production Rust CLI parsing unless you need deep custom argument UX work.
- **[skim-rs/skim](https://github.com/lotabout/skim)** — 6K stars, last commit 20 hours ago, MIT, 20 open issues, 241 forks, added 11 months ago. ([Source](https://libs.tech/rust/cli-libraries))\
  **Signal:** active development + very low issue load and strong fork support.\
  **2026 guidance:** best fit for interactive file/line navigation workflows with fast iteration.
- **[bootandy/dust](https://github.com/bootandy/dust)** — 11K stars, last commit 4 days ago, Apache 2.0, 5 open issues, 254 forks, added 11 months ago. ([Source](https://libs.tech/rust/cli-libraries))\
  **Signal:** mature maintenance profile for a utility tool with a tight issue backlog.\
  **2026 guidance:** low-friction replacement for `du`-style tooling in developer environments.
- **[svenstaro/miniserve](https://github.com/svenstaro/miniserve)** — 7K stars, last commit 3 days ago, MIT, 78 open issues, 366 forks, added 11 months ago. ([Source](https://libs.tech/rust/cli-libraries))\
  **Signal:** rapidly maintained and broadly forked, but issue volume suggests active feature use and configuration trade-offs.\
  **2026 guidance:** suitable for lightweight HTTP sharing/file serving; validate auth/TLS defaults in your threat model.
- **[ducaale/xh](https://github.com/ducaale/xh)** — 7K stars, last commit 2 days ago, MIT, 36 open issues, 121 forks, added 11 months ago. ([Source](https://libs.tech/rust/cli-libraries))\
  **Signal:** recent, well-maintained API-testing utility replacing ad-hoc shell scripts.\
  **2026 guidance:** good for internal CLI HTTP workflows; pair with scripting standards for reproducibility.
- **[imsnif/bandwhich](https://github.com/imsnif/bandwhich)** — 11K stars, last commit 2 weeks ago, MIT, 45 open issues, 338 forks, added 11 months ago. ([Source](https://libs.tech/rust/cli-libraries))\
  **Signal:** useful utility but explicitly in passive maintenance mode with funding-driven bandwidth constraints.\
  **2026 guidance:** adopt for observability tooling only if your team can tolerate slower feature roadmap.
- **[phiresky/ripgrep-all](https://github.com/phiresky/ripgrep-all)** — 9K stars, last commit 3 months ago, Other license, 69 open issues, 206 forks, added 11 months ago. ([Source](https://libs.tech/rust/cli-libraries))\
  **Signal:** strong feature niche (multiformat search) but license classification and slower commit cadence should be reviewed for enterprise policy.\
  **2026 guidance:** adopt selectively for investigator-grade search, then run legal/license review early.
- **[y2z/monolith](https://github.com/Y2Z/monolith)** — 14K stars, last commit 8 months ago, CC0-1.0, 75 open issues, 442 forks, added 11 months ago. ([Source](https://libs.tech/rust/cli-libraries))\
  **Signal:** highly adopted project with permissive legal profile and substantial fork adoption.\
  **2026 guidance:** strong for reproducible web-archiving use cases; verify maintenance expectations for long retention pipelines.
