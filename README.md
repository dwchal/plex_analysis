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
