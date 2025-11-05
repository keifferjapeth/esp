# ESP - Enhanced Service Platform

A platform that can interact with terminal automator notes, local apps, Google/BigQuery, Gemini, Vertex AI, and custom keys with intelligent priority management.

## Features

- **Multi-Service Integration**: Connect to BigQuery, Gemini, Vertex AI, and local applications
- **Intelligent Key Management**: Priority-based API key system (primary → Tilda env → Google service → Vertex → local backup)
- **Natural Language Interface**: Execute tasks using natural language commands
- **7-Pass Validation System**: Comprehensive validation framework
- **Tilda AI Console**: Beautiful black & white translucent liquid glass UI
- **Terminal Automator Support**: Interact with terminal automator notes

## Architecture

### Key Components

1. **Key Manager** (`key_manager.py`)
   - Manages API keys with priority hierarchy
   - Supports multiple key sources (environment, files)
   - Automatic fallback to next priority

2. **Service Manager** (`service_manager.py`)
   - Manages connections to external services
   - BigQuery, Gemini, Vertex AI integration
   - Terminal automator interface

3. **Validation System** (`validation_system.py`)
   - 7-pass validation framework:
     1. Key availability
     2. Service connectivity
     3. Permission check
     4. Rate limit check
     5. Data integrity
     6. Security validation
     7. End-to-end test

4. **Natural Language Processor** (`nlp_processor.py`)
   - Processes natural language commands
   - Routes to appropriate services
   - Supports commands like:
     - "list my Tilda projects"
     - "show me my files"
     - "query BigQuery"

5. **Backend Server** (`backend.py`)
   - HTTP API server
   - Endpoints for status, validation, execution
   - CORS-enabled for web UI

6. **Tilda AI Console** (`tilda_ai_console.html`)
   - Liquid glass effect UI
   - Black & white translucent design
   - Real-time command execution

## Setup

### Prerequisites

- Python 3.7 or higher
- Web browser (for UI)

### Configuration

1. **Set up API keys** (in order of priority):

   a. Environment variables (highest priority):
   ```bash
   export ESP_PRIMARY_KEY="your-primary-key"
   export TILDA_API_KEY="your-tilda-key"
   ```

   b. Create key files in `~/Documents/GitHub/keys/`:
   ```bash
   mkdir -p ~/Documents/GitHub/keys
   
   # Google Service key
   echo '{"api_key": "your-google-key"}' > ~/Documents/GitHub/keys/google_service.json
   
   # Vertex AI key
   echo '{"api_key": "your-vertex-key"}' > ~/Documents/GitHub/keys/vertex_key.json
   
   # Backup keys
   echo '{"api_key": "your-backup-key"}' > ~/Documents/GitHub/keys/backup_keys.json
   ```

2. **Configure services** in `config.json`:
   - Update BigQuery project_id and dataset_id
   - Customize service settings as needed

## Usage

### Step 1: Start Backend

```bash
cd /Users/keifferjapeth/Documents/GitHub/masterdata
./start_console.sh
```

The backend will start on `http://127.0.0.1:8080`

### Step 2: Open UI

Open `tilda_ai_console.html` in your web browser:

```bash
open tilda_ai_console.html
```

### Step 3: Try Commands!

Type natural language commands in the console:

- `list my Tilda projects` ← Works now!
- `show me my files`
- `query BigQuery`
- `analyze my data`
- `run optimization task`

## API Endpoints

### GET /status
Get server status and active services

```bash
curl http://127.0.0.1:8080/status
```

### GET /validate
Run 7-pass validation

```bash
curl http://127.0.0.1:8080/validate
```

### GET /services
Get service status

```bash
curl http://127.0.0.1:8080/services
```

### POST /execute
Execute natural language command

```bash
curl -X POST http://127.0.0.1:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "list my Tilda projects"}'
```

### POST /query
Execute service-specific query

```bash
curl -X POST http://127.0.0.1:8080/query \
  -H "Content-Type: application/json" \
  -d '{"service": "bigquery", "query": "SELECT * FROM table"}'
```

## Key Priority System

The platform uses a priority-based key management system:

1. **Primary** - Environment variable `ESP_PRIMARY_KEY` (highest priority)
2. **Tilda Env** - Environment variable `TILDA_API_KEY`
3. **Google Service** - File `~/Documents/GitHub/keys/google_service.json`
4. **Vertex** - File `~/Documents/GitHub/keys/vertex_key.json`
5. **Local Backup** - File `~/Documents/GitHub/keys/backup_keys.json` (lowest priority)

The system automatically falls back to the next priority if a key is unavailable.

## Validation Passes

The system runs 7 validation passes to ensure everything is working correctly:

1. **Key Availability** - Checks if API keys are accessible
2. **Service Connectivity** - Validates service connections
3. **Permission Check** - Verifies necessary permissions
4. **Rate Limit Check** - Ensures services are within rate limits
5. **Data Integrity** - Validates data consistency
6. **Security Validation** - Checks security configurations
7. **End-to-End Test** - Tests complete workflow

## Development

### Testing Individual Components

```bash
# Test key manager
python3 key_manager.py

# Test service manager
python3 service_manager.py

# Test validation system
python3 validation_system.py

# Test NLP processor
python3 nlp_processor.py
```

## Security Notes

- Keep API keys secure and never commit them to version control
- Use environment variables for sensitive keys when possible
- Store key files in secure locations with appropriate permissions
- The system validates security configurations in the 6th validation pass

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on the GitHub repository.
