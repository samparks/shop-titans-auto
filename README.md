# Shop Titans Automation

A Python automation tool for Shop Titans that extracts various in-game data and posts it to Discord.

## Features

- **Automated City Investment Scanning**: Automatically navigates through all city buildings and extracts investment progress
- **Claude Vision OCR**: Uses Claude's vision API for accurate text extraction from game screenshots
- **Discord Integration**: Posts formatted investment reports directly to your Discord channel
- **Hotkey Support**: Trigger workflows with keyboard shortcuts while the game is running

## Requirements

- macOS (currently macOS only due to window management)
- Python 3.9+
- Shop Titans running via Wine/CrossOver
- Anthropic API key (for Claude vision)
- Discord webhook URL (optional, for posting results)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/shop-titans-auto.git
cd shop-titans-auto
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .env
source .env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the Package

```bash
pip install -e .
```

### 5. Grant macOS Permissions

The tool needs two permissions to work:

#### Screen Recording Permission
1. Open **System Preferences** → **Privacy & Security** → **Screen Recording**
2. Add and enable your terminal app (Terminal, iTerm, VS Code, etc.)
3. Restart your terminal

#### Accessibility Permission
1. Open **System Preferences** → **Privacy & Security** → **Accessibility**
2. Add and enable your terminal app
3. Restart your terminal

### 6. Set Up API Keys

#### Anthropic API Key

1. Get your API key from [console.anthropic.com](https://console.anthropic.com/)
2. Export it in your terminal:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or add it to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### Discord Webhook (Optional)

To post results to Discord:

1. Open Discord and go to the channel where you want to post
2. Click the **gear icon** (Edit Channel) → **Integrations** → **Webhooks**
3. Click **New Webhook**
4. Give it a name (e.g., "Shop Titans Bot")
5. Click **Copy Webhook URL**
6. Export it in your terminal:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

Or add it to your shell profile:

```bash
echo 'export DISCORD_WEBHOOK_URL="your-webhook-url"' >> ~/.zshrc
source ~/.zshrc
```

## Usage

### Game Setup

1. Launch Shop Titans
2. Make sure the game is in **windowed mode** (not fullscreen)
3. Keep the game window visible on screen and make sure it's "active" before using your hotkeys. 
4. Make sure the game is in "portrait mode" by resizing the window horizontally. 

### Running Workflows

#### Option 1: Hotkey Mode (Recommended)

Start the hotkey listener:

```bash
game-automator hotkey
```

Then use these hotkeys:
- **F9** - Run the city investment scan
- **F12** - Exit the hotkey listener

You can keep the game focused and just press F9 when ready.

#### Option 2: Direct Command

```bash
game-automator run city-investment-scan
```

### Listing Available Workflows

```bash
game-automator list
```

## Workflows

### City Investment Scan

Scans all city buildings and extracts their investment progress.

**What it does:**
1. Navigates from the shop to the City screen
2. Clicks on a character building to open the investment panel
3. Captures screenshots while cycling through all buildings
4. Uses Claude vision to extract building names and investment values
5. Saves results to a CSV file in the `output/` folder
6. Posts a formatted report to Discord (if webhook is configured)

**Output CSV format:**
```csv
timestamp,building_name,current_investment,max_investment
2024-01-15T10:23:45,Academy,1800,2000
2024-01-15T10:23:46,Laboratory,1139,2000
...
```

**Discord output:**
```
🏰 City Investment Report
Building          | Current | Max 
----------------------------------
Temple            | 0       | 2000
Mausoleum         | 244     | 2000
Academy           | 1800    | 2000
...
```

## Troubleshooting

### Window Not Found

If you get "Could not find window 'Shop Titans'":
- Make sure the game is running
- Check that the window title contains "Shop Titans"
- Run `game-automator hotkey` and check the window detection output

### Clicks Not Registering

If clicks aren't working in the game:
- Make sure Accessibility permission is granted to your terminal
- Try clicking on the game window manually first, then run the workflow
- The first click may just activate the window; the workflow will retry automatically

### OCR Not Working

If text extraction fails:
- Make sure Screen Recording permission is granted
- Check that the game window is fully visible (not covered by other windows)
- Increase the sleep times in the workflow if the game is loading slowly

### Rate Limit Errors

If you see Claude API rate limit errors:
- The tool limits concurrent requests, but you may need to wait between runs
- Check your Anthropic API usage at console.anthropic.com
- Consider upgrading your API tier for higher limits

### Discord Post Failing

If Discord posting fails:
- Verify your webhook URL is correct
- Make sure the `DISCORD_WEBHOOK_URL` environment variable is set
- Check that the webhook hasn't been deleted in Discord

## Project Structure

```
shop-titans-auto/
├── src/
│   └── game_automator/
│       ├── core/
│       │   ├── capture.py      # Screenshot capture
│       │   ├── discord.py      # Discord webhook integration
│       │   ├── input.py        # Mouse/keyboard input
│       │   ├── ocr.py          # EasyOCR wrapper
│       │   ├── storage.py      # CSV output
│       │   ├── vision.py       # Claude vision API
│       │   └── window.py       # Window management
│       ├── engine/
│       │   ├── models.py       # Data models
│       │   ├── navigator.py    # Screen navigation
│       │   └── state.py        # State detection
│       ├── workflows/
│       │   ├── base.py         # Base workflow class
│       │   └── city_investment_scan.py
│       ├── cli.py              # Command line interface
│       └── hotkey.py           # Hotkey listener
├── output/                     # CSV output files
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Adding New Workflows

To create a new workflow:

1. Create a new file in `src/game_automator/workflows/`
2. Inherit from `BaseWorkflow`
3. Define `name`, `description`, and `csv_columns`
4. Implement the `run()` method

Example:

```python
from game_automator.workflows.base import BaseWorkflow

class MyNewWorkflow(BaseWorkflow):
    name = "my-workflow"
    description = "Description of what it does"
    csv_columns = ["column1", "column2"]
    
    def run(self):
        # Your automation logic here
        pass
```

The workflow will automatically be discovered and available via `game-automator list`.

## License

MIT License - feel free to use and modify as needed.

## Disclaimer

This tool is for personal use. Be aware that game automation may violate Shop Titans' Terms of Service. Use at your own risk.
