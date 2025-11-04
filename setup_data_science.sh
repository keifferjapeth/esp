#!/bin/bash

###############################################################################
#                                                                             #
#          Python Data Science Environment Setup Script                      #
#                                                                             #
###############################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Main setup
print_header "Python Data Science Environment Setup"

# Parse command-line arguments
FORCE=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -f|--force) FORCE=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Check Python installation
print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Create virtual environment
print_info "Creating virtual environment..."
if [ -d "venv" ]; then
    if [ "$FORCE" = true ]; then
        print_info "Force flag detected. Deleting and recreating virtual environment."
        rm -rf venv
        python3 -m venv venv
        print_success "Virtual environment recreated"
    else
        print_error "Virtual environment already exists at ./venv"
        read -p "Do you want to delete and recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            python3 -m venv venv
            print_success "Virtual environment recreated"
        else
            print_info "Using existing virtual environment"
        fi
    fi
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Install dependencies from requirements-ds.txt
print_header "Installing Data Science Packages"

if [ ! -f "requirements-ds.txt" ]; then
    print_error "Error: requirements-ds.txt not found!"
    exit 1
fi

print_info "Installing packages from requirements-ds.txt..."
pip install -r requirements-ds.txt --quiet
print_success "All packages from requirements-ds.txt installed successfully."

# Create requirements.txt
print_info "Creating requirements.txt from requirements-ds.txt..."
cp requirements-ds.txt requirements.txt
print_success "requirements.txt created."

# Create necessary directories
print_header "Creating Project Directories"

mkdir -p notebooks data/raw data/processed data/external
mkdir -p src logs models
mkdir -p {backups/mysql,backups/postgresql,backups/redis}

print_success "Project directories created"

# Create .env.example file
print_header "Creating Configuration Files"

if [ ! -f ".env.example" ]; then
    cat > ".env.example" << 'EOF'
# Google Cloud Configuration
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# BigQuery Configuration
BIGQUERY_DATASET=your_dataset
BIGQUERY_TABLE=your_table

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API Configuration
API_PORT=8000
API_DEBUG=True

# Jupyter Configuration
JUPYTER_PORT=8888
JUPYTER_TOKEN=

# Data Science Configuration
RANDOM_SEED=42
TEST_SIZE=0.2
EOF
    print_success ".env.example created"
else
    print_info ".env.example already exists"
fi

# Copy .env.example to .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_success ".env created (update with your credentials)"
fi

# Create Python notebooks example
print_header "Creating Example Notebook"

cat > "notebooks/00_example.ipynb" << 'EOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Data Science Project Template\n",
    "\n",
    "This is a template notebook for data science work."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Import libraries\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "\n",
    "# Set up plotting style\n",
    "sns.set_style('whitegrid')\n",
    "plt.rcParams['figure.figsize'] = (12, 6)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load data\n",
    "df = pd.read_csv('../data/raw/example.csv')\n",
    "\n",
    "# Display info\n",
    "print(f'Shape: {df.shape}')\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Data exploration\n",
    "df.info()\n",
    "df.describe()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Visualization\n",
    "plt.figure(figsize=(10, 6))\n",
    "df.hist(bins=30)\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.11.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF
print_success "Example notebook created at notebooks/00_example.ipynb"

# Create a Python module template
print_header "Creating Python Module Templates"

cat > "src/__init__.py" << 'EOF'
"""Data Science Project Module"""

__version__ = "0.1.0"
EOF
print_success "Created src/__init__.py"

cat > "src/data_loader.py" << 'EOF'
"""Data loading utilities"""

import pandas as pd
from pathlib import Path


def load_csv(file_path):
    """Load CSV file into DataFrame"""
    return pd.read_csv(file_path)


def load_from_bigquery(project_id, query):
    """Load data from BigQuery"""
    from google.cloud import bigquery
    client = bigquery.Client(project=project_id)
    return client.query(query).to_pandas()


def save_data(df, file_path, format='csv'):
    """Save DataFrame to file"""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    if format == 'csv':
        df.to_csv(file_path, index=False)
    elif format == 'parquet':
        df.to_parquet(file_path, index=False)
    elif format == 'excel':
        df.to_excel(file_path, index=False)
EOF
print_success "Created src/data_loader.py"

cat > "src/processor.py" << 'EOF'
"""Data processing utilities"""

import pandas as pd
import numpy as np


def remove_duplicates(df):
    """Remove duplicate rows"""
    return df.drop_duplicates()


def handle_missing_values(df, strategy='mean'):
    """Handle missing values"""
    if strategy == 'mean':
        return df.fillna(df.mean(numeric_only=True))
    elif strategy == 'forward_fill':
        return df.fillna(method='ffill')
    elif strategy == 'drop':
        return df.dropna()
    return df


def normalize_columns(df, columns):
    """Normalize specified columns"""
    df_copy = df.copy()
    for col in columns:
        if col in df_copy.columns:
            df_copy[col] = (df_copy[col] - df_copy[col].min()) / (df_copy[col].max() - df_copy[col].min())
    return df_copy
EOF
print_success "Created src/processor.py"

# Display system information
print_header "Installation Complete!"

echo "Environment Details:"
echo "  Python: $(python --version 2>&1)"
echo "  Pip: $(pip --version 2>&1)"
echo "  Virtual Environment: $(which python)"
echo ""

print_success "All packages installed successfully!"

print_header "Next Steps"

echo "1. Verify Installation:"
echo "   python -c 'import pandas; import numpy; print(\"✅ Core packages OK\")'"
echo ""

echo "2. Configure Authentication (if using BigQuery):"
echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json"
echo ""

echo "3. Start Jupyter:"
echo "   jupyter notebook"
echo ""

echo "4. Or use VS Code's Jupyter Support:"
echo "   code notebooks/00_example.ipynb"
echo ""

echo "5. Explore Data:"
echo "   cd notebooks && python"
echo "   >>> from src.data_loader import load_csv"
echo "   >>> df = load_csv('../data/raw/data.csv')"
echo ""

print_info "Project structure created:"
echo "  ✓ notebooks/         - Jupyter notebooks"
echo "  ✓ data/              - Raw, processed, external data"
echo "  ✓ src/               - Python modules"
echo "  ✓ models/            - Trained models"
echo "  ✓ logs/              - Log files"
echo "  ✓ backups/           - Database backups"
echo ""

print_success "Happy Data Science! 🚀📊"

###############################################################################
