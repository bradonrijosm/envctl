# envctl

A CLI tool for managing and switching between named environment variable profiles across projects.

---

## Installation

```bash
pip install envctl
```

Or install from source:

```bash
git clone https://github.com/yourname/envctl.git && cd envctl && pip install .
```

---

## Usage

```bash
# Create a new profile
envctl create myproject/staging

# Set variables in a profile
envctl set myproject/staging DATABASE_URL=postgres://localhost/mydb API_KEY=abc123

# Activate a profile (exports vars into your shell session)
eval $(envctl activate myproject/staging)

# List all profiles
envctl list

# Show variables in a profile
envctl show myproject/staging

# Delete a profile
envctl delete myproject/staging
```

Profiles are stored locally in `~/.envctl/profiles/` and are never committed to version control.

---

## Why envctl?

- Keep separate environment configs for `dev`, `staging`, and `production`
- Switch contexts instantly without editing `.env` files manually
- Works across projects without polluting your shell profile

---

## License

MIT © 2024 [yourname](https://github.com/yourname)