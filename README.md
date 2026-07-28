# README

This a template repo for project initialization.

## Introduction

current code architecture:

```text
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
│   ├── utils
│   │   ├── config.py
│   │   └── logger.py
│   └── __init__.py
├── data
│   └── data.md
├── docs
│   └── architecture.md
├── env
│   └── requirements.txt
├── CLAUDE.md
├── README.md
└── run.sh
```

`code/plan` and `code/execute` are just suggestion.

## Usage

1. clone this repo.
2. remove .git file to clean previous unnecessary commit history.
3. remove/clean this README.md for new content.
4. update CLAUDE.md for repo setting.(especially `TODO`)
5. install packages in env/requirements.txt

## TODO

1. gui connection between docker and pc.
2. a bash that automatically update all `TODO` region within this repo.
3. a bash that install necessary softwares/packages on a new linux pc.
4. option to backup code or not.
