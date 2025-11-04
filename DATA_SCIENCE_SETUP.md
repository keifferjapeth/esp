# 📊 Python Data Science Setup Guide

## ✅ Installed Extensions

### Core Data Science Pack
- **Python Data Science** (27,114 installs) - Complete extension pack for data scientists
  - Jupyter Notebook support
  - Python language support
  - Data visualization tools
  - Machine learning capabilities

### Additional Extensions Installed

1. **DBCode** - Database Management
   - ✅ BigQuery support
   - ✅ PostgreSQL, MySQL, MongoDB support
   - ✅ Query execution and editing
   - ✅ AI-assisted SQL queries
   - Features: Data graphing, report sharing, table management

2. **BigQuery Previewer** 
   - ✅ Analyze BigQuery SQL files
   - ✅ Dry run analysis
   - ✅ Query preview and validation
   - ✅ Data scan analysis

3. **Data Wrangler** ✅ (Pre-installed)
   - ✅ Data viewing and cleaning
   - ✅ Tabular dataset preparation
   - ✅ Data transformation tools
   - ✅ CSV, Excel, Parquet support

4. **Geo Data Viewer**
   - ✅ Geo data analytics
   - ✅ Kepler.gl map visualization
   - ✅ GeoJSON, Shapefile, KML support
   - ✅ Data lineage visualization

5. **Variable Explorer**
   - ✅ Python variable inspection
   - ✅ Pandas DataFrame viewing
   - ✅ Interactive debugging
   - ✅ Spyder-like experience

6. **Pylance** ✅ (Pre-installed)
   - ✅ Python language intelligence
   - ✅ Type checking
   - ✅ Code analysis

7. **Makefile Tools** ✅ (Just installed)
   - ✅ Makefile support
   - ✅ Task automation

---

## 🚀 Quick Start

### 1. Python Environment Setup

```bash
# Check Python version
python3 --version

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Data Science Libraries

```bash
# Core data science stack
pip install jupyter pandas numpy scipy scikit-learn matplotlib seaborn

# BigQuery and Google Cloud
pip install google-cloud-bigquery google-cloud-storage

# Additional tools
pip install plotly bokeh altair openpyxl

# Database drivers
pip install psycopg2-binary pymysql sqlalchemy

# Development tools
pip install black flake8 pytest pylint
```

### 3. Start Jupyter Notebook

```bash
# From project directory
jupyter notebook

# Or use VS Code's built-in Jupyter support
# Ctrl+Shift+P → "Jupyter: Create New Notebook"
```

---

## 📚 Working with Jupyter Notebooks

### Create Notebook

1. **Via Command Palette**
   - Press `Ctrl+Shift+P`
   - Type "Jupyter: Create New Notebook"
   - Choose Python kernel

2. **Via File**
   - Create `.ipynb` file
   - VS Code will detect and enable Jupyter support

### Notebook Features

```python
# Cell 1: Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from google.cloud import bigquery

# Cell 2: Load data
df = pd.read_csv('data.csv')
print(df.head())

# Cell 3: Display DataFrame
df  # Auto-renders in notebook

# Cell 4: Create visualization
df.plot(kind='scatter', x='col1', y='col2')
plt.show()
```

---

## 🗄️ BigQuery Integration

### Setup Authentication

```bash
# Option 1: Service Account (Recommended)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Option 2: Application Default Credentials
gcloud auth application-default login
```

### Query BigQuery from Python

```python
from google.cloud import bigquery
import pandas as pd

# Initialize client
client = bigquery.Client(project='your-project-id')

# Simple query
query = """
    SELECT COUNT(*) as count
    FROM `project.dataset.table`
    LIMIT 1000
"""

df = client.query(query).to_pandas()
print(df)
```

### Use BigQuery Previewer Extension

1. Create `.sql` file with BigQuery query
2. Right-click → "BigQuery: Analyze"
3. View results and cost estimation

---

## 📊 Working with Data

### Data Wrangler Features

1. **Open Data Wrangler**
   - Right-click CSV/Excel file → "Open with Data Wrangler"
   - Or use Command Palette

2. **Data Exploration**
   - View data summary
   - Check data types
   - Identify missing values

3. **Data Cleaning**
   - Remove duplicates
   - Fill missing values
   - Rename columns
   - Filter rows

4. **Data Transformation**
   - Create derived columns
   - Group and aggregate
   - Pivot tables
   - Join datasets

5. **Export Code**
   - Generate Python/pandas code
   - Copy to notebook or script

### Variable Explorer

1. **View Variables**
   - Press `Ctrl+Shift+P` → "Variable Explorer: Focus"
   - Or View → Explorer → Python Variables

2. **Inspect DataFrames**
   - Click on DataFrame variable
   - View rows, columns, types
   - Edit values directly

3. **Debugging**
   - Stop at breakpoints
   - Inspect variable state
   - Modify values during debug

---

## 🗺️ Geo Data Visualization

### Supported Formats

- GeoJSON (`.geojson`)
- Shapefiles (`.shp`)
- KML (`.kml`)
- GPX (`.gpx`)
- CSV with coordinates

### Using Geo Data Viewer

```python
# Python script to generate GeoJSON
import json
import pandas as pd

# Create GeoJSON from coordinates
features = []
for idx, row in df.iterrows():
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [row['longitude'], row['latitude']]
        },
        "properties": {
            "name": row['name'],
            "value": row['value']
        }
    })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

# Save and open in Geo Data Viewer
with open('data.geojson', 'w') as f:
    json.dump(geojson, f)
```

---

## 🔗 DBCode for Database Management

### Connect to BigQuery

1. **Open DBCode**
   - Click Database icon in sidebar
   - Click "New Connection"

2. **Add BigQuery Connection**
   - Provider: BigQuery
   - Project ID: your-project-id
   - Service Account: /path/to/key.json

3. **Query and Explore**
   - Browse tables
   - Edit data
   - Run queries
   - View results

### Database Features

```sql
-- Create table
CREATE TABLE dataset.my_table (
    id INT64,
    name STRING,
    value FLOAT64
);

-- Query data
SELECT * FROM dataset.my_table LIMIT 10;

-- Insert data
INSERT INTO dataset.my_table VALUES
(1, 'Example', 100.5);
```

---

## 📈 Recommended Workflow

### Day 1: Setup
1. ✅ Install extensions (done)
2. ✅ Create virtual environment
3. ✅ Install libraries
4. ✅ Test Jupyter notebooks

### Day 2: Data Exploration
1. Load CSV/Excel files
2. Use Data Wrangler for cleaning
3. Generate exploration code
4. Create visualizations

### Day 3: BigQuery
1. Set up authentication
2. Query your data
3. Load results into pandas
4. Analyze and visualize

### Day 4: Integration
1. Combine local data with BigQuery
2. Create dashboards
3. Build predictive models
4. Export results

---

## 🔧 Configuration

### VS Code Settings

Add to `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.linting.flake8Enabled": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  },
  "jupyter.askForKernelRestart": false,
  "jupyter.runStartupCommands": [],
  "jupyter.notebookFileRoot": "${workspaceFolder}"
}
```

### Python Environment (`.venv`)

```bash
# Create with specific Python version
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Deactivate
deactivate
```

---

## 🧪 Example: Complete Data Science Workflow

### Project Structure

```
my-data-science-project/
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_analysis.ipynb
│   └── 03_modeling.ipynb
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── src/
│   ├── data_loader.py
│   ├── processor.py
│   └── models.py
├── requirements.txt
├── setup.py
└── README.md
```

### Example Notebook

```python
# Cell 1: Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from google.cloud import bigquery

# Cell 2: Load data from BigQuery
client = bigquery.Client()
query = """
    SELECT * FROM `project.dataset.leads`
    WHERE creation_date >= '2024-01-01'
    LIMIT 10000
"""
df = client.query(query).to_pandas()

# Cell 3: Explore data
print(f"Shape: {df.shape}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nMissing values:\n{df.isnull().sum()}")

# Cell 4: Data cleaning with Wrangler
# (Use Data Wrangler for interactive cleaning)

# Cell 5: Feature engineering
df['lead_score'] = df['engagement'] * df['quality']
df['days_old'] = (pd.Timestamp.now() - df['creation_date']).dt.days

# Cell 6: Model training
X = df.drop('conversion', axis=1).select_dtypes(include=[np.number])
y = df['conversion']

X_train, X_test, y_train, y_test = train_test_split(X, y)
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Cell 7: Evaluation
score = model.score(X_test, y_test)
print(f"Accuracy: {score:.4f}")

# Cell 8: Visualization
plt.figure(figsize=(10, 6))
plt.plot(model.feature_importances_)
plt.xlabel('Feature Index')
plt.ylabel('Importance')
plt.title('Feature Importances')
plt.show()
```

---

## 🆘 Troubleshooting

### Jupyter Kernel Issues

```bash
# Reinstall kernel
python -m ipykernel install --user --name venv --display-name "Python (venv)"

# List kernels
jupyter kernelspec list

# Remove kernel
jupyter kernelspec remove venv
```

### BigQuery Connection

```bash
# Test connection
python -c "from google.cloud import bigquery; print(bigquery.Client().project)"

# Set credentials explicitly
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/key.json'
```

### Data Wrangler Not Available

```bash
# Reinstall extension
pip install ipywidgets ipykernel
jupyter nbextension enable --py --sys-prefix widgetsnbextension
```

---

## 📖 Learning Resources

### Official Documentation
- [Jupyter Documentation](https://jupyter.org/documentation)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Scikit-Learn Documentation](https://scikit-learn.org/stable/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)

### VS Code Guides
- [Python in VS Code](https://code.visualstudio.com/docs/languages/python)
- [Jupyter in VS Code](https://code.visualstudio.com/docs/datascience/jupyter-notebooks)
- [Data Science in VS Code](https://code.visualstudio.com/docs/datascience/data-science-tutorial)

### Tutorials
- [Pandas Cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html)
- [ML with Scikit-Learn](https://scikit-learn.org/stable/tutorial/index.html)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)

---

## ✨ Next Steps

1. **Create Virtual Environment**
   ```bash
   python3 -m venv venv && source venv/bin/activate
   ```

2. **Install Core Libraries**
   ```bash
   pip install jupyter pandas numpy scipy scikit-learn matplotlib
   ```

3. **Connect to BigQuery**
   - Get service account key
   - Set `GOOGLE_APPLICATION_CREDENTIALS`
   - Test connection with: `bq ls`

4. **Start First Notebook**
   ```bash
   jupyter notebook
   ```

5. **Explore Your Data**
   - Load CSV or BigQuery table
   - Use Data Wrangler for exploration
   - Create visualizations

---

**Happy Data Science! 🚀📊**
