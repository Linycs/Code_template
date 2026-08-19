# README

This a template repo for project initialization.

## Introduction

current code architecture:

```text
├── _linycs
│   └── docs
│       ├── architecture.md
│       ├── design.md
│       ├── doc-maintenance.md
│       ├── fsys_template.md
│       └── prompts.md
├── assets
├── code
│   ├── configs
│   │   └── default.yaml
│   ├── plan
│   │   └── planner.py
│   ├── execute
│   │   └── __init__.py
│   ├── scripts
│   │   └── main.py
│   ├── test_debug
│   │   └── .gitignore
│   ├── utils
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── statistics.py
│   │   └── visualization.py
│   └── __init__.py
├── data
│   └── data.md
├── env
│   ├── docker-compose.yml
│   ├── Dockerfile.template
│   ├── init_softwares.sh
│   └── requirements.txt
├── AGENTS.md
├── README.md
└── run_entrance.sh
```

`code/plan` and `code/execute` are just suggestion.

## Usage

1. clone this repo.
2. remove .git file to clean previous unnecessary commit history.
3. remove/clean this README.md for new content.
4. update `AGENTS.md` for repo settings, especially every `TODO`.
5. replace the TODO sections in `_linycs/docs/design.md`, and keep both maintained docs fresh according to `_linycs/docs/doc-maintenance.md`.
6. install packages in `env/requirements.txt`.

`code/test_debug/` is an ignored placeholder for disposable test/debug implementations. Keep reusable utilities and long-lived regression tests in tracked modules instead.

## TODO

1. gui connection between docker and pc.
2. a bash that automatically update all `TODO` region within this repo.
3. a bash that create necessary files in other cloned repo.
4. option to backup code or not.
