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

