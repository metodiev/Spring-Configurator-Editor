# Spring-Configurator-Editor

A Python automation tool for managing Spring Boot configuration files across multiple Java services using GitHub API.

## Features

- Create and manage branches across multiple repositories
- Replace Spring configuration files (bootstrap.yml, application.yml)
- Support for multiple database connections (Oracle, Snowflake, PostgreSQL, Azure SQL)
- Compare pom.xml files between branches
- Trigger and monitor GitHub Actions workflows
- Extract and save workflow logs
- Interactive menu-driven interface
- Comprehensive logging

## Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token with appropriate permissions
- Access to target GitHub organization repositories

## Project Structure
```
Spring-Configurator-Editor/
├── config/
│   ├── services_config.json          # Service configuration
│   └── connection_templates/         # Database connection templates
│       ├── oracle.yml
│       ├── snowflake.yml
│       ├── postgres.yml
│       └── azure.yml
├── src/
│   ├── main.py                       # Main application
│   ├── services/
│   │   ├── github_client.py          # GitHub API wrapper
│   │   ├── service_manager.py        # Service organization
│   │   ├── config_replacer.py        # Configuration replacement
│   │   ├── pom_comparator.py         # POM file comparison
│   │   └── workflow_manager.py       # GitHub Actions management
│   └── utils/
│       └── logger.py                 # Logging utility
├── workspace/                         # Working directory (created at runtime)
├── logs/                             # Application logs (created at runtime)
├── requirements.txt
└── README.md
```

## Installation

### Step 1: Clone the repository
```bash
git clone <repository-url>
cd Spring-Configurator-Editor
```

### Step 2: Create virtual environment

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

Windows:
```bash
pip install -r requirements.txt --break-system-packages
```

Mac/Linux:
```bash
pip install -r requirements.txt
```

### Step 4: Setup GitHub Token

Create a Personal Access Token at https://github.com/settings/tokens with the following scopes:
- repo (Full control of private repositories)
- workflow (Update GitHub Actions workflows)
- read:org (Read organization data)

Set the token as environment variable:

Windows:
```bash
setx GITHUB_TOKEN "ghp_your_token_here"
```

Mac/Linux:
```bash
export GITHUB_TOKEN="ghp_your_token_here"
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
```

Important: After setting GITHUB_TOKEN on Windows, close and reopen your terminal.

### Step 5: Configure services

Edit `config/services_config.json` with your actual service names and settings:
```json
{
  "organization": "your-github-org",
  "service_groups": {
    "config_services": {
      "folder": "config_services",
      "services": [
        "service-config-1",
        "service-config-2"
      ]
    },
    "client_services": {
      "folder": "client_services",
      "services": [
        "client-service-1",
        "client-service-2"
      ]
    }
  },
  "branches": {
    "base_branch": "main",
    "compare_branch": "develop",
    "new_branch_prefix": "config-update"
  },
  "config_files": {
    "bootstrap": "src/main/resources/bootstrap.yml",
    "application": "src/main/resources/application.yml",
    "pom": "pom.xml"
  },
  "workflow": {
    "workflow_file": "build.yml",
    "wait_for_completion": true,
    "timeout_seconds": 600
  }
}
```

## Usage

### Run the application
```bash
python src/main.py
```

### Menu Options

1. Create service folders structure
   - Creates workspace folders for each service group

2. Create branches for all services
   - Creates new branches from base branch across all repositories

3. Replace configurations - Config Services Group
   - Updates configuration files for config service group

4. Replace configurations - Client Services Group
   - Updates configuration files for client service group

5. Replace configurations - All Services
   - Updates configuration files for all service groups

6. Compare pom.xml files
   - Compares pom.xml between two branches for a specific service

7. Compare pom.xml for all services
   - Compares pom.xml files across all services

8. Trigger workflows for all services
   - Triggers GitHub Actions workflows for all services

9. Extract workflow logs
   - Saves workflow execution logs to files

10. Run full automation
    - Executes all steps in sequence

11. View configuration
    - Displays current configuration settings

12. View logs directory
    - Shows recent log files

## Configuration Templates

The tool includes database connection templates in `config/connection_templates/`:

- oracle.yml - Oracle database configuration
- snowflake.yml - Snowflake database configuration
- postgres.yml - PostgreSQL database configuration
- azure.yml - Azure SQL database configuration

These templates are used when replacing application.yml files in services.

## Workflow Automation Steps

The full automation process executes these steps:

1. Create folder structure for service groups
2. Create new branches for all services
3. Replace configuration files in config services
4. Replace configuration files in client services
5. Compare pom.xml files between branches
6. Trigger GitHub Actions workflows
7. Extract and save workflow logs

## Logging

All operations are logged to:
- Console output (real-time)
- Log files in `logs/` directory
- Workflow logs in `logs/workflows/` directory

Log format: `[timestamp] [component] [level] message`

## Troubleshooting

### GITHUB_TOKEN not found
Ensure the token is set as environment variable and terminal is restarted.

Verify on Windows:
```bash
echo %GITHUB_TOKEN%
```

Verify on Mac/Linux:
```bash
echo $GITHUB_TOKEN
```

### Connection failed
- Check token permissions (repo, workflow, read:org)
- Verify organization name in config
- Ensure token is authorized for SSO (if applicable)

### Service not found
- Verify service names in config/services_config.json
- Check repository exists in GitHub organization
- Ensure correct organization name

### Workflow trigger failed
- Verify workflow file exists in repository
- Check workflow has workflow_dispatch trigger
- Ensure branch exists in repository

### File not found errors
- Verify file paths in config match actual repository structure
- Check branch name is correct
- Ensure files exist in target branch

## Testing

To be created 

## License

MIT License - see LICENSE file for details
