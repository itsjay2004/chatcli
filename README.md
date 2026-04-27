# ChatCLI - Modern Terminal AI Chat for Linux

A production-ready, terminal-based AI chat client built in Python. ChatCLI offers a smooth and modern CLI user experience with rich formatting, multi-provider model support, persistent chat history, command shortcuts, and interactive configuration.

---

## Features

- Beautiful terminal interface using **Rich** panels, colors, markdown rendering, and syntax-highlighted code blocks.
- Smooth multi-line input with history and keyboard shortcuts via **Prompt Toolkit**.
- Multi-turn conversation memory (session context maintained in memory).
- Persistent chat history saved as JSON files (`chats/`).
- Slash command system (`/help`, `/save`, `/history`, `/load`, etc.).
- Interactive `/config` menu for provider/model/API settings.
- Modular provider abstraction for easy extension.
- Friendly error handling for invalid keys, network failures, and bad commands.
- Auto-save on safe exit.

---

## Supported Providers

- OpenAI
- Anthropic
- Google (Gemini)
- OpenRouter
- Custom OpenAI-compatible endpoint
- Custom Anthropic-compatible endpoint

Each provider uses a unified interface (`get_response(messages, config)`) under `providers/`.

---

## Project Structure

```text
project/
│
├── main.py
├── ui/
│   ├── display.py
│   ├── input.py
│
├── core/
│   ├── chat.py
│   ├── commands.py
│   ├── history.py
│   ├── config.py
│
├── providers/
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── google_provider.py
│   ├── openrouter_provider.py
│   ├── custom_provider.py
│
├── chats/
├── README.md
└── requirements.txt
```

---

## Installation

### 1) Clone and enter project directory

```bash
git clone <your-repo-url>
cd chatcli
```

### 2) Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

---

## Dependencies

- `rich`
- `prompt_toolkit`
- `httpx`

Minimal and lightweight terminal-focused stack (no GUI frameworks).

---

## Run the Application

```bash
python main.py
```

On first run, create settings with:

```text
/config
```

---

## Configuration

Configuration is stored locally at:

```text
~/.config.json
```

Stored settings include:

- Active provider
- Model name
- Temperature
- Provider API key
- Base URL

> Note: API keys are stored locally in plain JSON on your machine. Protect file permissions if needed.

---

## Command Reference

| Command | Description |
|---|---|
| `/help` | Show all commands |
| `/clear` | Clear terminal screen only (keeps session context) |
| `/exit` | Save current session and exit safely |
| `/save` | Save current chat manually |
| `/history` | List last 10 saved chats |
| `/load <id>` | Load a chat from history index |
| `/delete <id>` | Delete a saved chat |
| `/config` | Open interactive configuration menu |

---

## Chat History Behavior

- Chats are stored as one JSON file per session in `chats/`.
- Each file includes:
  - `timestamp`
  - `title` (optional / auto-generated)
  - `messages` list with `{role, content}`
- Retention policy implemented:
  - Tracks up to 15 recent chats
  - If history exceeds 15 files, older files are pruned down to the latest 10

---

## Example Usage

1. Launch app: `python main.py`
2. Run `/config` and set provider + API key + model.
3. Ask a question:

```text
Explain async IO in Python with a simple example.
```

4. Save with `/save`.
5. See previous chats with `/history`.
6. Reload one with `/load 2`.

---

## Keyboard UX Notes

- Multi-line input enabled.
- Press **Enter** to submit.
- Press **Ctrl+J** to submit explicitly.
- Input history and suggestions are enabled.

---

## Error Handling

ChatCLI gracefully handles:

- Missing API keys
- HTTP/API errors (status displayed)
- Network failures
- Empty input
- Unknown commands

Errors are rendered in readable styled panels.

---

## Screenshots

_Terminal UI screenshot placeholder (optional):_

```text
[ Add screenshot here if desired ]
```

---

## Extend with New Providers

1. Add a new file in `providers/`.
2. Implement `Provider.get_response(messages, config)`.
3. Register provider in `core/chat.py` and config defaults in `core/config.py`.

---

## License

Use, modify, and distribute as needed.
