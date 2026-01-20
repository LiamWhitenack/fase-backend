# Fantasy Athlete Stock Exchange

## Setup

### Python

#### Fedora

```
sudo dnf install python3.14
python3.14 -m venv .venv
source .venv/bin/activate
pip install uv
uv sync
```

#### Windows

Install Python 3.14 with the Windows store

```
python3.14 -m venv .venv
.venv/Scripts/python -m pip install uv
.venv/Scripts/python -m uv sync
```

#### Fedora

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
python3.14 -m venv .venv
source .venv/bin/activate
pip install uv
uv sync
```

### Docker

install docker compose, docker desktop, and other stuff. Requires more documentation

### Data

Download the database dump file from here:
https://drive.google.com/file/d/1N1hi1o8b_-PbdtoUtyDJd2noqnuBkWjH/view?usp=sharing
And use the scripts in the launch configuration to supplement any missing data. As of January 20th, there should be none.

Or run each script in the run and debug section of the debug menu and ask me for the contracts and player salary sections, as you'll need a spotrac login for that