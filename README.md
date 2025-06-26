NPS01.py - Now Playing Script #01\
NPS02.py - Now Playing Script #02

A real-time file monitoring system that automatically posts artist and track information to the RadioPlayer API whenever your "now playing" file changes.

🎵 Overview\
The NPS01.py and NPS02.py scripts will monitor a local text file for changes and immediately posts the artist and track information to the RadioPlayer API. This eliminates the need for scheduled polling and provides instant updates whenever your broadcast system updates the now-playing information.

- NPS01/py supports legacy authentication with username:API key combination.
- NPS02.py uses X-API-KEY header authentication instead of basic authentication.

✨ Features

🔄 Real-time File Monitoring: Uses filesystem events for instant change detection\
⚡ Event-Driven: Posts to API immediately when file content changes (no polling delays)\
🛡️ Secure Configuration: All sensitive data managed through environment variables\
🌍 Timezone Support: Configurable timezone handling with proper DST support\
📝 Comprehensive Logging: Configurable log levels with structured output\
🔧 Error Handling: Robust error handling for files, network, and API issues\
⏱️ Debounced Events: Prevents duplicate API calls from rapid file changes\
🚀 Startup Processing: Processes existing file content on script startup

🔧 Requirements

- Python 3.7+
- Internet connection for API calls
- Read access to the monitored file

📦 Installation

Clone or download the script\
Download either NPS01.py or NPS02.py to your desired directory

Install Python dependencies\
`pip install requests watchdog pytz python-dotenv`

Or use requirements.txt:\
`pip install -r requirements.txt`


⚙️ Configuration
### Environment Variables
Create a .env file in the same directory as NPS01.py or NPS02.py:

### Required API credentials
API_USERNAME is only required for NPS01.py\
`API_USERNAME=your-api-username`\
`API_PASSWORD=your-api-password`

### Required API configuration  
`API_ENDPOINT=https://np-ingest.radioplayer.cloud`\
`RPUID=your-station-id`

### Required file path (use forward slashes or escaped backslashes)
`FILE_PATH=C:/path/to/your/now_playing.txt`

### Optional configuration
`TIMEZONE=UTC`\
`LOG_LEVEL=INFO`

## Configuration Options

|   Variable   | Required |           Description          |              Example                   | 
|:-------------|:--------:|:-------------------------------|:---------------------------------------|
| API_USERNAME |    ✅    | RadioPlayer API username       | apiuser@example.com                    | 
| API_PASSWORD |    ✅    | RadioPlayer API password/token | abc123-def456-ghi789                   |
| API_ENDPOINT |    ✅    | RadioPlayer API endpoint URL   | `https://np-ingest.radioplayer.cloud`  |
| RPUID        |    ✅    | Your RadioPlayer station ID    | 999999                                 | 
| FILE_PATH    |    ✅    | Path to your now playing file  | `C:/broadcast/nowplaying.txt`          |
| TIMEZONE     |    ❌    | Timezone for timestamps        | UTC, America/New_York, Europe/London   |
| LOG_LEVEL    |    ❌    | Logging verbosity              | DEBUG, INFO, WARNING, ERROR            |

🚀 Usage\
Basic Usage

- Set up your .env file with the required configuration
- Ensure your now playing file exists and contains the expected format

Run the script:\
`python NPS01.py`\
or
`python NPS01.py`


### Running as a Service
For production use, consider running NPS01.py as a system service:

## Windows (using NSSM)
Install NSSM (Non-Sucking Service Manager)\
Download from: https://nssm.cc/download

### Install the service
`nssm install NPS01 "C:\Python\python.exe" "C:\path\to\NPS01.py"`
`nssm set NPS01 AppDirectory "C:\path\to\script\directory"`
`nssm start NPS01`

## Linux (using systemd)
Create /etc/systemd/system/nps01.service:\
`ini[Unit]`\
`Description=Now Playing Script v1.0`\
`After=network.target`

`[Service]`\
`Type=simple`\
`User=your-user`\
`WorkingDirectory=/path/to/script`\
`ExecStart=/usr/bin/python3 /path/to/NPS01.py`\
`Restart=always`\
`RestartSec=10`

`[Install]`\
`WantedBy=multi-user.target`

Enable and start:

`sudo systemctl enable nps01.service`\
`sudo systemctl start nps01.service`

📄 File Format
Your now playing file should contain artist and title information in this format:\
`Artist: The Beatles`\
`Title: Hey Jude`

### Format Rules

- Each line should start with either Artist: or Title:
- Case-insensitive matching (artist:, ARTIST:, etc. all work)
- Leading/trailing whitespace is automatically trimmed
- Empty lines are ignored
- Additional content in the file is ignored

### Example Files

`Simple format:`\
`Artist: Queen`\
`Title: Bohemian Rhapsody`

With additional data (ignored):\
`Station: Example FM`\
`Artist: Pink Floyd`\
`Title: Comfortably Numb`\
`Duration: 6:23`\
Album: The Wall`

📊 Logging\
NPS01.py / NPS02.py provides comprehensive logging with configurable levels:

### Log Levels

- DEBUG: Detailed information for debugging (API URLs, file content, etc.)
- INFO: General operational information (file changes, successful posts)
- WARNING: Warning messages (missing data, file issues)
- ERROR: Error conditions (API failures, file access errors)

### Example Log Output

2025-06-10 14:30:15 - INFO - Started monitoring: C:\Users\BillBest\test.txt\
2025-06-10 14:30:15 - INFO - Initial file content - Artist: 'Queen', Title: 'Bohemian Rhapsody'\
2025-06-10 14:30:15 - INFO - Successfully posted: Queen - Bohemian Rhapsody\
2025-06-10 14:32:45 - INFO - File changed: C:\Users\BillBest\test.txt\
2025-06-10 14:32:45 - INFO - Extracted - Artist: 'The Beatles', Title: 'Hey Jude'\
2025-06-10 14:32:45 - INFO - Successfully posted: The Beatles - Hey Jude

🔍 Troubleshooting

## Common Issues
"Required environment variable X is not set"

Solution: Ensure your .env file is in the same directory as NPS01.py and contains all required variables\

### "File not found" error

Solution: Check that the FILE_PATH in your .env file is correct and the file exists\
Note: Use forward slashes (/) or escaped backslashes (\\) in Windows paths\

### "API request failed" errors

Solution: Verify your API credentials and network connectivity\
Check: Ensure API_USERNAME, API_PASSWORD, and API_ENDPOINT are correct\

### No API calls being made

Solution: Check that your file contains the correct format (Artist: and Title: lines)\
Debug: Set LOG_LEVEL=DEBUG to see detailed parsing information

### File Path Issues (Windows)
Windows users should use one of these path formats in their .env file:

### Forward slashes (recommended)
`FILE_PATH=C:/path/to/file/test.txt\`

### Escaped backslashes
`FILE_PATH=C:\\path\\to\\file\\test.txt`

### Raw string (if setting via Python)
`FILE_PATH=r"C:\path\to\file\test.txt"`

🏗️ Architecture\
NPS01.py / NPS02.py follows SOLID principles with a clean, modular architecture:

## Core Components

- Config: Environment variable management and validation
- FileParser: File parsing and metadata extraction logic
- RadioPlayerAPI: API communication and HTTP handling
- FileChangeHandler: Filesystem event handling and debouncing
- RadioPlayerMonitor: Main application orchestration

## Design Principles

- Single Responsibility: Each class has one clear purpose
- Dependency Injection: Clean separation of concerns
- Error Isolation: Comprehensive error handling at each layer
- Configurability: All behaviour controlled through environment variables

🔒 Security Considerations

- Environment Variables: All sensitive data stored in environment variables, never hardcoded
- URL Encoding: Proper encoding of artist/title data to prevent injection attacks
- Input Validation: Validates all configuration and file data before use
- Error Handling: Doesn't expose sensitive information in error messages

📋 API Integration
NPS01.py / NPS02.py integrates with the RadioPlayer API using the following endpoint format:

`POST {API_ENDPOINT}?rpuid={RPUID}&startTime={TIMESTAMP}&title={TITLE}&artist={ARTIST}`

## Parameters

- rpuid: Your RadioPlayer station identifier
- startTime: ISO 8601 timestamp in configured timezone
- title: URL-encoded track title
- artist: URL-encoded artist name

### Authentication
NPS01.py uses HTTP Basic Authentication with your API username and password.\
NPS02.py uses X-API-KEY header authentication instead of basic authentication.

🤝 Contributing

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request

📝 License\
This project is licensed under the MIT License - see the LICENSE file for details.

🆘 Support\
For support, please:

1. Check the troubleshooting section above
2. Review your log output with LOG_LEVEL=DEBUG
3. Verify your .env configuration
4. Open an issue with detailed information about your problem


NPS01.py / NPS02.py - instant and reliable Now Playing radio metadata updates.
