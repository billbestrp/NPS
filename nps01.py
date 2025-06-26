#!/usr/bin/env python3
"""
NPS01.py - Now Playing Script v1.0
Monitors a text file for changes and immediately posts artist/title data to the RadioPlayer API.
Script supports legacy authentication with username:API key combination.
"""

import os
import re
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import quote_plus

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pytz
from dotenv import load_dotenv


class Config:
    """Configuration management using environment variables."""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.api_username = self._get_required_env('API_USERNAME')
        self.api_password = self._get_required_env('API_KEY')
        self.api_endpoint = self._get_required_env('API_ENDPOINT')
        self.file_path = Path(self._get_required_env('FILE_PATH'))
        self.rpuid = int(self._get_required_env('RPUID'))
        self.timezone = self._get_env('TIMEZONE', 'UTC')
        self.log_level = self._get_env('LOG_LEVEL', 'INFO').upper()
        
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _get_env(self, key: str, default: str) -> str:
        """Get environment variable with default value."""
        return os.getenv(key, default)


class FileParser:
    """Parses artist and title information from text files."""
    
    ARTIST_PATTERN = re.compile(r'^Artist: (.+)$', re.IGNORECASE)
    TITLE_PATTERN = re.compile(r'^Title: (.+)$', re.IGNORECASE)
    
    @classmethod
    def parse_file(cls, file_path: Path) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse artist and title from file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Tuple of (artist, title) or (None, None) if not found
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            with file_path.open('r', encoding='utf-8') as file:
                content = file.read().strip()
                
            if not content:
                logging.warning("File is empty")
                return None, None
                
            return cls._extract_metadata(content)
            
        except IOError as e:
            raise IOError(f"Error reading file {file_path}: {e}")
    
    @classmethod
    def _extract_metadata(cls, content: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract artist and title from file content."""
        artist = None
        title = None
        
        for line in content.splitlines():
            line = line.strip()
            
            if not line:
                continue
                
            artist_match = cls.ARTIST_PATTERN.match(line)
            if artist_match:
                artist = artist_match.group(1).strip()
                continue
                
            title_match = cls.TITLE_PATTERN.match(line)
            if title_match:
                title = title_match.group(1).strip()
                
        return artist, title


class RadioPlayerAPI:
    """Handles API communication with RadioPlayer service."""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.session.auth = (config.api_username, config.api_password)
        
    def post_now_playing(self, artist: str, title: str) -> bool:
        """
        Post now playing information to RadioPlayer API.
        
        Args:
            artist: Artist name
            title: Song title
            
        Returns:
            True if successful, False otherwise
        """
        if not self._validate_metadata(artist, title):
            return False
            
        timestamp = self._get_current_timestamp()
        url = self._build_url(artist, title, timestamp)
        
        try:
            logging.debug(f"POST Request: {url}")
            response = self.session.post(url, timeout=30)
            response.raise_for_status()
            
            logging.info(f"Successfully posted: {artist} - {title}")
            return True
            
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            return False
    
    def _validate_metadata(self, artist: str, title: str) -> bool:
        """Validate artist and title data."""
        if not artist or not title:
            logging.warning("Missing artist or title data")
            return False
            
        if len(artist.strip()) == 0 or len(title.strip()) == 0:
            logging.warning("Empty artist or title after stripping whitespace")
            return False
            
        return True
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in the configured timezone."""
        try:
            tz = pytz.timezone(self.config.timezone)
            now = datetime.now(tz)
            return now.strftime('%Y-%m-%dT%H:%M:%S')
        except pytz.exceptions.UnknownTimeZoneError:
            logging.warning(f"Unknown timezone {self.config.timezone}, using UTC")
            now = datetime.now(pytz.UTC)
            return now.strftime('%Y-%m-%dT%H:%M:%S')
    
    def _build_url(self, artist: str, title: str, timestamp: str) -> str:
        """Build API URL with parameters."""
        # URL encode the artist and title
        artist_encoded = quote_plus(artist)
        title_encoded = quote_plus(title)
        
        return (f"{self.config.api_endpoint}?"
                f"rpuid={self.config.rpuid}&"
                f"startTime={timestamp}&"
                f"title={title_encoded}&"
                f"artist={artist_encoded}")


class FileChangeHandler(FileSystemEventHandler):
    """Handles file system events for monitoring file changes."""
    
    def __init__(self, file_path: Path, api_client: RadioPlayerAPI):
        self.file_path = file_path
        self.api_client = api_client
        self.last_modified = 0
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        if Path(event.src_path) != self.file_path:
            return
            
        # Avoid duplicate events
        current_time = time.time()
        if current_time - self.last_modified < 1:  # 1 second debounce
            return
            
        self.last_modified = current_time
        self._process_file_change()
    
    def _process_file_change(self):
        """Process the file change and post to API."""
        try:
            logging.info(f"File changed: {self.file_path}")
            artist, title = FileParser.parse_file(self.file_path)
            
            if artist and title:
                logging.info(f"Extracted - Artist: '{artist}', Title: '{title}'")
                self.api_client.post_now_playing(artist, title)
            else:
                logging.warning("Could not extract valid artist and title from file")
                
        except Exception as e:
            logging.error(f"Error processing file change: {e}")


class RadioPlayerMonitor:
    """Main application class for monitoring and posting radio metadata."""
    
    def __init__(self):
        self.config = Config()
        self._setup_logging()
        self.api_client = RadioPlayerAPI(self.config)
        self.observer = None
        
    def _setup_logging(self):
        """Configure logging based on config."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format=log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
    def start_monitoring(self):
        """Start monitoring the file for changes."""
        try:
            # Validate file exists
            if not self.config.file_path.exists():
                raise FileNotFoundError(f"File not found: {self.config.file_path}")
                
            # Process file immediately on startup
            self._process_initial_file()
            
            # Setup file monitoring
            event_handler = FileChangeHandler(self.config.file_path, self.api_client)
            self.observer = Observer()
            self.observer.schedule(
                event_handler, 
                str(self.config.file_path.parent), 
                recursive=False
            )
            
            self.observer.start()
            logging.info(f"Started monitoring: {self.config.file_path}")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logging.info("Received interrupt signal, stopping...")
                
        except Exception as e:
            logging.error(f"Failed to start monitoring: {e}")
            raise
        finally:
            self.stop_monitoring()
    
    def _process_initial_file(self):
        """Process the file on startup."""
        try:
            artist, title = FileParser.parse_file(self.config.file_path)
            if artist and title:
                logging.info(f"Initial file content - Artist: '{artist}', Title: '{title}'")
                self.api_client.post_now_playing(artist, title)
            else:
                logging.warning("No valid artist/title found in initial file")
        except Exception as e:
            logging.error(f"Error processing initial file: {e}")
    
    def stop_monitoring(self):
        """Stop file monitoring."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logging.info("File monitoring stopped")


def main():
    """Main entry point."""
    try:
        monitor = RadioPlayerMonitor()
        monitor.start_monitoring()
    except Exception as e:
        logging.error(f"Application failed: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
