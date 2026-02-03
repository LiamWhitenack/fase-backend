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

#### MacOS

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

upload the latest data by running the backup-upload-db.sh script:
```
chmod +x backup-upload-db.sh
backup-upload-db.sh
```

Or run each script in the run and debug section of the debug menu and ask me for the contracts and player salary sections, as you'll need a spotrac login for that