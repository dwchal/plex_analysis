#!/usr/bin/env python3
"""
Plex Library Analyzer and Movie Recommender

Analyzes your Plex movie library and provides recommendations for new movies
based on your viewing preferences, favorite genres, directors, and actors.
"""

import argparse
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

try:
    from plexapi.server import PlexServer
    from plexapi.myplex import MyPlexAccount
except ImportError:
    print("Error: plexapi is required. Install with: pip install plexapi")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: requests is required. Install with: pip install requests")
    sys.exit(1)


@dataclass
class LibraryAnalysis:
    """Container for library analysis results."""
    total_movies: int = 0
    genres: Counter = field(default_factory=Counter)
    directors: Counter = field(default_factory=Counter)
    actors: Counter = field(default_factory=Counter)
    years: Counter = field(default_factory=Counter)
    decades: Counter = field(default_factory=Counter)
    studios: Counter = field(default_factory=Counter)
    average_rating: float = 0.0
    ratings: list = field(default_factory=list)
    movie_ids: set = field(default_factory=set)  # TMDB IDs if available
    movie_titles: set = field(default_factory=set)


class PlexAnalyzer:
    """Analyzes a Plex movie library."""

    def __init__(self, plex_url: str = None, plex_token: str = None,
                 username: str = None, password: str = None, server_name: str = None):
        """
        Initialize the Plex connection.

        Can connect either via direct URL + token or via MyPlex account credentials.

        Args:
            plex_url: Direct URL to Plex server (e.g., http://localhost:32400)
            plex_token: Plex authentication token
            username: MyPlex account username/email
            password: MyPlex account password
            server_name: Name of the server to connect to (for MyPlex)
        """
        self.plex = None
        self._connect(plex_url, plex_token, username, password, server_name)

    def _connect(self, plex_url: str, plex_token: str,
                 username: str, password: str, server_name: str):
        """Establish connection to Plex server."""
        # Try environment variables if not provided
        plex_url = plex_url or os.environ.get('PLEX_URL')
        plex_token = plex_token or os.environ.get('PLEX_TOKEN')
        username = username or os.environ.get('PLEX_USERNAME')
        password = password or os.environ.get('PLEX_PASSWORD')
        server_name = server_name or os.environ.get('PLEX_SERVER_NAME')

        if plex_url and plex_token:
            print(f"Connecting to Plex server at {plex_url}...")
            self.plex = PlexServer(plex_url, plex_token)
        elif username and password:
            print(f"Connecting via MyPlex account...")
            account = MyPlexAccount(username, password)
            if server_name:
                self.plex = account.resource(server_name).connect()
            else:
                # Connect to first available server
                resources = [r for r in account.resources() if r.product == 'Plex Media Server']
                if not resources:
                    raise ValueError("No Plex Media Servers found on account")
                print(f"Connecting to server: {resources[0].name}")
                self.plex = resources[0].connect()
        else:
            raise ValueError(
                "Must provide either (plex_url and plex_token) or "
                "(username and password). Can also use environment variables: "
                "PLEX_URL, PLEX_TOKEN, PLEX_USERNAME, PLEX_PASSWORD, PLEX_SERVER_NAME"
            )

        print(f"Connected to: {self.plex.friendlyName}")

    def get_movie_libraries(self) -> list:
        """Get all movie libraries from the Plex server."""
        return [lib for lib in self.plex.library.sections() if lib.type == 'movie']

    def analyze_library(self, library_name: str = None) -> LibraryAnalysis:
        """
        Analyze a movie library and extract statistics.

        Args:
            library_name: Name of the library to analyze. If None, uses first movie library.

        Returns:
            LibraryAnalysis object with statistics
        """
        libraries = self.get_movie_libraries()
        if not libraries:
            raise ValueError("No movie libraries found on server")

        if library_name:
            library = next((lib for lib in libraries if lib.title == library_name), None)
            if not library:
                available = [lib.title for lib in libraries]
                raise ValueError(f"Library '{library_name}' not found. Available: {available}")
        else:
            library = libraries[0]

        print(f"Analyzing library: {library.title}")
        print("Fetching all movies (this may take a moment)...")

        movies = library.all()
        analysis = LibraryAnalysis()
        analysis.total_movies = len(movies)

        for movie in movies:
            analysis.movie_titles.add(movie.title.lower())

            # Genres
            for genre in movie.genres:
                analysis.genres[genre.tag] += 1

            # Directors
            for director in movie.directors:
                analysis.directors[director.tag] += 1

            # Actors (top 5 billed)
            for actor in movie.roles[:5]:
                analysis.actors[actor.tag] += 1

            # Year and decade
            if movie.year:
                analysis.years[movie.year] += 1
                decade = (movie.year // 10) * 10
                analysis.decades[decade] += 1

            # Studios
            for studio in movie.studio if hasattr(movie, 'studio') and movie.studio else []:
                if isinstance(studio, str):
                    analysis.studios[studio] += 1

            # Ratings
            if movie.audienceRating:
                analysis.ratings.append(movie.audienceRating)

            # Try to get TMDB ID from guids
            for guid in movie.guids:
                if 'tmdb://' in guid.id:
                    tmdb_id = guid.id.replace('tmdb://', '')
                    analysis.movie_ids.add(tmdb_id)

        if analysis.ratings:
            analysis.average_rating = sum(analysis.ratings) / len(analysis.ratings)

        return analysis

    def print_analysis(self, analysis: LibraryAnalysis, top_n: int = 10):
        """Print a formatted analysis report."""
        print("\n" + "=" * 60)
        print("PLEX LIBRARY ANALYSIS")
        print("=" * 60)

        print(f"\nTotal Movies: {analysis.total_movies}")
        print(f"Average Rating: {analysis.average_rating:.1f}/10")

        print(f"\nTop {top_n} Genres:")
        for genre, count in analysis.genres.most_common(top_n):
            pct = (count / analysis.total_movies) * 100
            print(f"  {genre}: {count} ({pct:.1f}%)")

        print(f"\nTop {top_n} Directors:")
        for director, count in analysis.directors.most_common(top_n):
            print(f"  {director}: {count} movies")

        print(f"\nTop {top_n} Actors:")
        for actor, count in analysis.actors.most_common(top_n):
            print(f"  {actor}: {count} movies")

        print(f"\nMovies by Decade:")
        for decade, count in sorted(analysis.decades.items()):
            pct = (count / analysis.total_movies) * 100
            print(f"  {decade}s: {count} ({pct:.1f}%)")

        print("=" * 60)


class TMDBRecommender:
    """Generates movie recommendations using TMDB API."""

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key: str = None):
        """
        Initialize TMDB recommender.

        Args:
            api_key: TMDB API key. Can also use TMDB_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get('TMDB_API_KEY')
        if not self.api_key:
            raise ValueError(
                "TMDB API key required. Get one at https://www.themoviedb.org/settings/api "
                "and pass it via --tmdb-key or TMDB_API_KEY environment variable."
            )
        self._genre_map = None

    def _request(self, endpoint: str, params: dict = None) -> dict:
        """Make a request to TMDB API."""
        params = params or {}
        params['api_key'] = self.api_key
        response = requests.get(f"{self.BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    @property
    def genre_map(self) -> dict:
        """Get mapping of genre names to TMDB genre IDs."""
        if self._genre_map is None:
            data = self._request("/genre/movie/list")
            self._genre_map = {g['name'].lower(): g['id'] for g in data['genres']}
        return self._genre_map

    def search_movie(self, title: str, year: int = None) -> Optional[dict]:
        """Search for a movie by title."""
        params = {'query': title}
        if year:
            params['year'] = year
        data = self._request("/search/movie", params)
        if data['results']:
            return data['results'][0]
        return None

    def get_recommendations_for_movie(self, movie_id: int) -> list:
        """Get recommendations based on a specific movie."""
        data = self._request(f"/movie/{movie_id}/recommendations")
        return data['results']

    def get_similar_movies(self, movie_id: int) -> list:
        """Get similar movies based on a specific movie."""
        data = self._request(f"/movie/{movie_id}/similar")
        return data['results']

    def discover_movies(self, genres: list = None, min_rating: float = None,
                        min_year: int = None, max_year: int = None,
                        sort_by: str = "vote_average.desc",
                        min_votes: int = 100) -> list:
        """
        Discover movies based on criteria.

        Args:
            genres: List of genre names to filter by
            min_rating: Minimum rating (0-10)
            min_year: Minimum release year
            max_year: Maximum release year
            sort_by: Sort order (vote_average.desc, popularity.desc, etc.)
            min_votes: Minimum number of votes (for quality filtering)

        Returns:
            List of movie results
        """
        params = {
            'sort_by': sort_by,
            'vote_count.gte': min_votes,
            'include_adult': 'false',
            'include_video': 'false',
        }

        if genres:
            genre_ids = []
            for genre in genres:
                genre_lower = genre.lower()
                if genre_lower in self.genre_map:
                    genre_ids.append(str(self.genre_map[genre_lower]))
            if genre_ids:
                params['with_genres'] = ','.join(genre_ids)

        if min_rating:
            params['vote_average.gte'] = min_rating

        if min_year:
            params['primary_release_date.gte'] = f"{min_year}-01-01"

        if max_year:
            params['primary_release_date.lte'] = f"{max_year}-12-31"

        data = self._request("/discover/movie", params)
        return data['results']

    def get_person_movies(self, person_name: str) -> list:
        """Get movies by a specific person (actor/director)."""
        # Search for person
        data = self._request("/search/person", {'query': person_name})
        if not data['results']:
            return []

        person_id = data['results'][0]['id']

        # Get their movie credits
        credits = self._request(f"/person/{person_id}/movie_credits")
        movies = credits.get('cast', []) + credits.get('crew', [])

        # Remove duplicates and sort by popularity
        seen = set()
        unique_movies = []
        for movie in movies:
            if movie['id'] not in seen:
                seen.add(movie['id'])
                unique_movies.append(movie)

        return sorted(unique_movies, key=lambda x: x.get('popularity', 0), reverse=True)

    def generate_recommendations(self, analysis: LibraryAnalysis,
                                  num_recommendations: int = 20) -> list:
        """
        Generate movie recommendations based on library analysis.

        Args:
            analysis: LibraryAnalysis from Plex library
            num_recommendations: Number of recommendations to generate

        Returns:
            List of recommended movies with reasons
        """
        recommendations = []
        seen_ids = set()

        print("\nGenerating recommendations based on your library...")

        # Strategy 1: Movies from favorite genres with high ratings
        top_genres = [g[0] for g in analysis.genres.most_common(3)]
        if top_genres:
            print(f"  Finding highly-rated {', '.join(top_genres)} movies...")
            genre_movies = self.discover_movies(
                genres=top_genres,
                min_rating=7.0,
                min_votes=500,
                sort_by="vote_average.desc"
            )
            for movie in genre_movies[:10]:
                if movie['id'] not in seen_ids and movie['title'].lower() not in analysis.movie_titles:
                    seen_ids.add(movie['id'])
                    recommendations.append({
                        'movie': movie,
                        'reason': f"Highly rated in your favorite genres: {', '.join(top_genres)}"
                    })

        # Strategy 2: Movies from favorite directors
        top_directors = [d[0] for d in analysis.directors.most_common(3)]
        for director in top_directors:
            print(f"  Finding more movies by {director}...")
            director_movies = self.get_person_movies(director)
            for movie in director_movies[:5]:
                if movie['id'] not in seen_ids and movie.get('title', '').lower() not in analysis.movie_titles:
                    seen_ids.add(movie['id'])
                    recommendations.append({
                        'movie': movie,
                        'reason': f"Directed by {director} (one of your favorites)"
                    })

        # Strategy 3: Movies featuring favorite actors
        top_actors = [a[0] for a in analysis.actors.most_common(5)]
        for actor in top_actors[:3]:
            print(f"  Finding more movies with {actor}...")
            actor_movies = self.get_person_movies(actor)
            for movie in actor_movies[:3]:
                if movie['id'] not in seen_ids and movie.get('title', '').lower() not in analysis.movie_titles:
                    seen_ids.add(movie['id'])
                    recommendations.append({
                        'movie': movie,
                        'reason': f"Starring {actor} (frequently in your library)"
                    })

        # Strategy 4: Popular movies from your preferred decades
        top_decade = analysis.decades.most_common(1)
        if top_decade:
            decade = top_decade[0][0]
            print(f"  Finding popular movies from the {decade}s...")
            decade_movies = self.discover_movies(
                min_year=decade,
                max_year=decade + 9,
                min_rating=7.5,
                min_votes=1000,
                sort_by="popularity.desc"
            )
            for movie in decade_movies[:5]:
                if movie['id'] not in seen_ids and movie['title'].lower() not in analysis.movie_titles:
                    seen_ids.add(movie['id'])
                    recommendations.append({
                        'movie': movie,
                        'reason': f"Popular classic from the {decade}s (your most common decade)"
                    })

        # Strategy 5: Hidden gems in favorite genres
        if top_genres:
            print(f"  Finding hidden gems...")
            hidden_gems = self.discover_movies(
                genres=top_genres[:2],
                min_rating=7.0,
                min_votes=100,
                sort_by="vote_average.desc"
            )
            for movie in hidden_gems[10:20]:  # Skip the most popular ones
                if movie['id'] not in seen_ids and movie['title'].lower() not in analysis.movie_titles:
                    seen_ids.add(movie['id'])
                    recommendations.append({
                        'movie': movie,
                        'reason': f"Hidden gem in {top_genres[0]}"
                    })

        # Sort by rating and return top N
        recommendations.sort(
            key=lambda x: x['movie'].get('vote_average', 0),
            reverse=True
        )

        return recommendations[:num_recommendations]

    def print_recommendations(self, recommendations: list):
        """Print formatted recommendations."""
        print("\n" + "=" * 60)
        print("MOVIE RECOMMENDATIONS")
        print("=" * 60)

        for i, rec in enumerate(recommendations, 1):
            movie = rec['movie']
            title = movie.get('title', 'Unknown')
            year = movie.get('release_date', '')[:4]
            rating = movie.get('vote_average', 0)
            overview = movie.get('overview', 'No description available.')

            print(f"\n{i}. {title} ({year})")
            print(f"   Rating: {rating}/10")
            print(f"   Why: {rec['reason']}")
            print(f"   {overview[:150]}{'...' if len(overview) > 150 else ''}")

        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze your Plex library and get movie recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  PLEX_URL          Direct URL to Plex server (e.g., http://localhost:32400)
  PLEX_TOKEN        Plex authentication token
  PLEX_USERNAME     MyPlex account email
  PLEX_PASSWORD     MyPlex account password
  PLEX_SERVER_NAME  Name of server to connect to (optional)
  TMDB_API_KEY      TMDB API key for recommendations

Examples:
  # Using direct connection
  %(prog)s --plex-url http://localhost:32400 --plex-token YOUR_TOKEN

  # Using MyPlex account
  %(prog)s --username email@example.com --password yourpassword

  # With TMDB recommendations
  %(prog)s --tmdb-key YOUR_TMDB_KEY --recommendations 20

  # Analyze specific library
  %(prog)s --library "4K Movies" --output analysis.json
        """
    )

    # Plex connection options
    plex_group = parser.add_argument_group('Plex Connection')
    plex_group.add_argument('--plex-url', help='Plex server URL')
    plex_group.add_argument('--plex-token', help='Plex authentication token')
    plex_group.add_argument('--username', help='MyPlex account username')
    plex_group.add_argument('--password', help='MyPlex account password')
    plex_group.add_argument('--server-name', help='Plex server name (for MyPlex)')

    # Analysis options
    analysis_group = parser.add_argument_group('Analysis Options')
    analysis_group.add_argument('--library', '-l', help='Name of movie library to analyze')
    analysis_group.add_argument('--output', '-o', help='Save analysis to JSON file')
    analysis_group.add_argument('--top', type=int, default=10,
                                 help='Number of top items to show (default: 10)')

    # Recommendation options
    rec_group = parser.add_argument_group('Recommendation Options')
    rec_group.add_argument('--tmdb-key', help='TMDB API key for recommendations')
    rec_group.add_argument('--recommendations', '-r', type=int, default=0,
                           help='Number of recommendations to generate (requires TMDB key)')
    rec_group.add_argument('--rec-output', help='Save recommendations to JSON file')

    # Other options
    parser.add_argument('--list-libraries', action='store_true',
                        help='List available movie libraries and exit')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Minimal output')

    args = parser.parse_args()

    try:
        # Connect to Plex
        analyzer = PlexAnalyzer(
            plex_url=args.plex_url,
            plex_token=args.plex_token,
            username=args.username,
            password=args.password,
            server_name=args.server_name
        )

        # List libraries if requested
        if args.list_libraries:
            libraries = analyzer.get_movie_libraries()
            print("\nAvailable movie libraries:")
            for lib in libraries:
                print(f"  - {lib.title}")
            return

        # Analyze library
        analysis = analyzer.analyze_library(args.library)

        # Print analysis
        if not args.quiet:
            analyzer.print_analysis(analysis, args.top)

        # Save analysis to file
        if args.output:
            output_data = {
                'total_movies': analysis.total_movies,
                'average_rating': analysis.average_rating,
                'genres': dict(analysis.genres.most_common()),
                'directors': dict(analysis.directors.most_common(50)),
                'actors': dict(analysis.actors.most_common(100)),
                'years': dict(analysis.years),
                'decades': dict(analysis.decades),
            }
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\nAnalysis saved to: {args.output}")

        # Generate recommendations
        if args.recommendations > 0:
            try:
                recommender = TMDBRecommender(args.tmdb_key)
                recommendations = recommender.generate_recommendations(
                    analysis,
                    args.recommendations
                )

                if not args.quiet:
                    recommender.print_recommendations(recommendations)

                # Save recommendations to file
                if args.rec_output:
                    rec_data = [{
                        'title': r['movie'].get('title'),
                        'year': r['movie'].get('release_date', '')[:4],
                        'rating': r['movie'].get('vote_average'),
                        'overview': r['movie'].get('overview'),
                        'reason': r['reason'],
                        'tmdb_id': r['movie'].get('id')
                    } for r in recommendations]
                    with open(args.rec_output, 'w') as f:
                        json.dump(rec_data, f, indent=2)
                    print(f"\nRecommendations saved to: {args.rec_output}")

            except ValueError as e:
                print(f"\nWarning: {e}")
                print("Skipping recommendations. Use --tmdb-key to provide API key.")

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
