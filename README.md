# Plex Library Analyzer

A Python tool that analyzes your Plex movie library and provides personalized movie recommendations based on your viewing preferences.

## Features

- **Library Analysis**: Get detailed statistics about your movie collection
  - Genre distribution
  - Top directors and actors
  - Movies by decade
  - Average ratings

- **Smart Recommendations**: Get movie suggestions based on:
  - Your favorite genres
  - Directors you love
  - Actors frequently in your library
  - Your preferred time periods
  - Hidden gems matching your taste

## Quick Start Guide for Mac

Follow these steps to get up and running on macOS:

### Step 1: Open Terminal

Press `Cmd + Space` to open Spotlight, type "Terminal", and press Enter.

### Step 2: Check if Python is Installed

```bash
python3 --version
```

If you see a version number (e.g., `Python 3.11.4`), skip to Step 4.

If you get "command not found", proceed to Step 3.

### Step 3: Install Python (if needed)

**Option A: Using Homebrew (recommended)**

First, install Homebrew if you don't have it:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Python:
```bash
brew install python
```

**Option B: Direct Download**

Download Python from [python.org](https://www.python.org/downloads/macos/) and run the installer.

### Step 4: Download This Project

```bash
# Navigate to your home folder (or wherever you want to store the project)
cd ~

# Clone the repository
git clone https://github.com/dwchal/plex_analysis.git

# Enter the project directory
cd plex_analysis
```

Or download the ZIP from GitHub and extract it.

### Step 5: Create a Virtual Environment (Recommended)

This keeps the project dependencies isolated:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

You'll see `(venv)` appear at the start of your terminal prompt.

### Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 7: Get Your Plex Token

1. Open your browser and go to [app.plex.tv](https://app.plex.tv)
2. Sign in to your Plex account
3. Play any movie and click on the **"Get Info"** or **info icon**
4. Click **"View XML"** at the bottom of the info panel
5. Look at the URL in your browser - find `X-Plex-Token=XXXXXX`
6. Copy the token value (the part after the `=`)

### Step 8: Get Your TMDB API Key (for recommendations)

1. Go to [themoviedb.org](https://www.themoviedb.org/) and create a free account
2. Go to **Settings** (click your profile icon) > **API**
3. Click **"Create"** or **"Request an API Key"**
4. Choose "Developer" and fill out the form (for personal use, the details don't matter much)
5. Copy your **API Key** (not the "API Read Access Token")

### Step 9: Find Your Plex Server URL

- If Plex runs on your Mac: `http://localhost:32400`
- If Plex runs on another machine: `http://YOUR_SERVER_IP:32400`
  - Find the IP in Plex Settings > Network, or check your router

### Step 10: Run the Analyzer

**Basic analysis (no recommendations):**
```bash
python3 plex_analyzer.py \
    --plex-url http://localhost:32400 \
    --plex-token YOUR_PLEX_TOKEN
```

**With movie recommendations:**
```bash
python3 plex_analyzer.py \
    --plex-url http://localhost:32400 \
    --plex-token YOUR_PLEX_TOKEN \
    --tmdb-key YOUR_TMDB_API_KEY \
    --recommendations 20
```

**Save results to files:**
```bash
python3 plex_analyzer.py \
    --plex-url http://localhost:32400 \
    --plex-token YOUR_PLEX_TOKEN \
    --tmdb-key YOUR_TMDB_API_KEY \
    --recommendations 20 \
    --output ~/Desktop/my_library_analysis.json \
    --rec-output ~/Desktop/movie_recommendations.json
```

### Step 11: (Optional) Set Up Environment Variables

To avoid typing credentials every time, add them to your shell profile:

```bash
# Open your shell profile in a text editor
nano ~/.zshrc
```

Add these lines at the end:
```bash
export PLEX_URL="http://localhost:32400"
export PLEX_TOKEN="your-plex-token-here"
export TMDB_API_KEY="your-tmdb-api-key-here"
```

Save (`Ctrl+O`, Enter) and exit (`Ctrl+X`), then reload:
```bash
source ~/.zshrc
```

Now you can simply run:
```bash
python3 plex_analyzer.py --recommendations 20
```

### Troubleshooting

**"command not found: python3"**
- Make sure Python is installed (Step 3)
- Try `python` instead of `python3`

**"Connection refused" or "Unable to connect"**
- Verify your Plex server is running
- Check the URL and port are correct
- Make sure your firewall allows connections

**"Invalid token" or "Unauthorized"**
- Get a fresh token from Plex (tokens can expire)
- Make sure you copied the entire token

**"No movie libraries found"**
- Use `--list-libraries` to see available libraries
- Specify the correct library name with `--library "Library Name"`

---

## Installation

```bash
pip install -r requirements.txt
```

## Getting Your Credentials

### Plex Token

1. Sign in to Plex Web App
2. Browse to any media item and click "Get Info"
3. Click "View XML" in the modal
4. Look for `X-Plex-Token` in the URL

Or use the [Plex Token Guide](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

### TMDB API Key (for recommendations)

1. Create an account at [TMDB](https://www.themoviedb.org/)
2. Go to Settings > API
3. Request an API key (free for personal use)

## Usage

### Basic Analysis

```bash
# Using direct Plex connection
python plex_analyzer.py --plex-url http://localhost:32400 --plex-token YOUR_TOKEN

# Using MyPlex account
python plex_analyzer.py --username email@example.com --password yourpassword
```

### With Recommendations

```bash
# Get 20 movie recommendations
python plex_analyzer.py --plex-url http://localhost:32400 --plex-token YOUR_TOKEN \
    --tmdb-key YOUR_TMDB_KEY --recommendations 20
```

### Environment Variables

You can set credentials via environment variables:

```bash
export PLEX_URL="http://localhost:32400"
export PLEX_TOKEN="your-plex-token"
export TMDB_API_KEY="your-tmdb-api-key"

# Then just run:
python plex_analyzer.py --recommendations 20
```

### Command Line Options

```
Plex Connection:
  --plex-url URL       Plex server URL (e.g., http://localhost:32400)
  --plex-token TOKEN   Plex authentication token
  --username USER      MyPlex account username/email
  --password PASS      MyPlex account password
  --server-name NAME   Plex server name (for MyPlex accounts)

Analysis Options:
  --library, -l NAME   Name of movie library to analyze
  --output, -o FILE    Save analysis to JSON file
  --top N              Number of top items to show (default: 10)

Recommendation Options:
  --tmdb-key KEY       TMDB API key for recommendations
  --recommendations N  Number of recommendations to generate
  --rec-output FILE    Save recommendations to JSON file

Other:
  --list-libraries     List available movie libraries
  --quiet, -q          Minimal output
```

### Examples

```bash
# List all movie libraries
python plex_analyzer.py --plex-url http://localhost:32400 --plex-token TOKEN --list-libraries

# Analyze a specific library
python plex_analyzer.py --plex-url http://localhost:32400 --plex-token TOKEN --library "4K Movies"

# Save analysis and recommendations to files
python plex_analyzer.py --plex-url http://localhost:32400 --plex-token TOKEN \
    --tmdb-key TMDB_KEY \
    --output analysis.json \
    --recommendations 30 \
    --rec-output recommendations.json
```

## Sample Output

```
============================================================
PLEX LIBRARY ANALYSIS
============================================================

Total Movies: 487
Average Rating: 7.2/10

Top 10 Genres:
  Drama: 203 (41.7%)
  Action: 156 (32.0%)
  Thriller: 98 (20.1%)
  Comedy: 87 (17.9%)
  ...

Top 10 Directors:
  Christopher Nolan: 8 movies
  Denis Villeneuve: 6 movies
  ...

============================================================
MOVIE RECOMMENDATIONS
============================================================

1. Arrival (2016)
   Rating: 7.9/10
   Why: Directed by Denis Villeneuve (one of your favorites)
   A linguist is recruited by the military to communicate with...

2. Prisoners (2013)
   Rating: 8.1/10
   Why: Highly rated in your favorite genres: Drama, Thriller
   ...
```

## License

MIT License
