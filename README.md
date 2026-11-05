<img src="assets/OrcaLink_Logo.png" alt="OrcaLink logo" width="180">


# OrcaLink

**CSC 501 - Algorithms and Data Models**  
University of Victoria

**Team:** Aung Htut, Bowen Zhang, Sophia Umukoro

## About the Project

OrcaLink is a database project for Southern Resident killer whales.

We used data from Dryad and The Whale Museum to build a SQLite database that connects whales, sightings, and observations. We also calculate associations between whales based on sightings they share.

Our Flask website lets users view, search, add, edit, and delete whale records.

## Database

We implemented seven main tables:

| Table | Purpose |
|---|---|
| Whale | Stores individual whale information |
| DataSource | Stores where the data came from |
| Location | Stores sighting location information |
| Sighting | Stores sighting records |
| IndividualObservation | Connects whales to sightings |
| GroupObservation | Stores reported group observations |
| Association | Stores whale pairs and their co-sighting scores |

We also use `ObservationStaging` to check the observation data before linking it to the main tables.

## Requirements

Before starting, make sure you have:

- Python 3.10 or newer
- Git
- An internet connection for installing Flask
- A terminal (macOS or Linux)

SQLite is included with Python, so you do not need a separate database server.

## Setup

### 1. Get the project

```bash
git clone https://github.com/CSC501-OrcaLink/orcalink.git
cd orcalink
git switch integration-test
```

### 2. Run the setup script

```bash
bash quickstart.sh
```

The script will:

1. Create a Python virtual environment
2. Install the required packages
3. Create and populate the SQLite database
4. Check the imported data
5. Start the Flask website

The database will be saved as `orcalink_demo.db`.

### 3. Open the website

Go to:

http://127.0.0.1:5000

To stop the server, press `Ctrl+C` in the terminal.

## Using the Website

The current website manages records in the `Whale` table.

**Search:** Enter a whale code, such as `J1`, or search by name.

**Add:** Enter a new whale code and any information you want to include.

**Edit:** Click a whale record, change its information, and select Save changes.

**Delete:** Click Delete whale and confirm the action.

For testing, use a temporary whale code such as `TEST_UI`. This avoids changing the original dataset.

Other tables can be accessed using SQL queries and the Python scripts.

## Rebuilding the Database

To create the database without starting Flask:

```bash
bash quickstart.sh --build-only
```

To rebuild the database from the CSV files:

```bash
bash quickstart.sh --rebuild
```

Rebuilding replaces `orcalink_demo.db`, but does not change your original `orcalink.db`.

## Running Tests

Test the Flask functions:

```bash
.venv/bin/python scripts/web_smoke_test.py
```

This tests viewing, searching, adding, editing, and deleting whale records using a temporary database.

You can also run the SQL checks:

```bash
sqlite3 orcalink_demo.db < sql/sighting_checks.sql
sqlite3 orcalink_demo.db < sql/08_group_observation_checks.sql
sqlite3 orcalink_demo.db < sql/10_association_checks.sql
```

The `sqlite3` terminal command is optional and may need to be installed separately.

## Integration Results

Our integration test on November 4, 2026 produced:

| Table | Records |
|---|---:|
| Whale | 130 |
| Sighting | 122,764 |
| Location | 38,926 |
| IndividualObservation | 35,042 |
| GroupObservation | 116,822 |
| Association | 686 |

All 35,042 individual observations were linked to sightings successfully.

The checks reported:
- 0 unmatched sightings
- 0 foreign-key errors

## Project Files

```text
orcalink/
├── app.py                 # Flask application
├── quickstart.sh          # Runs setup and Flask
├── requirements.txt       # Python packages
├── scripts/               # Data import and setup
├── sql/                   # Tables, queries and checks
├── templates/             # Website HTML
├── assets/                # Logo
├── data/processed/        # Prepared datasets
├── docs/                  # Project notes and screenshots
└── reports/               # Project reports
```

The database is built from the prepared CSV files in `data/processed/data/`.

The setup script runs the import files in the required order, starting with sightings, then whales, individual observations, group observations, and associations.

## Limitations

Not every observation identifies a specific whale. We keep missing or unresolved whale IDs instead of guessing.

The association scores are based on shared sightings. They do not necessarily mean that two whales have a confirmed social relationship.

The current Flask interface only manages whale records. The other relations are available through SQL and Python.

The family-related tables from our earlier ER diagram are not included in this milestone's implementation.

## Data Sources

- Dryad — J-pod whale lifespan and observation data
- The Whale Museum — Historical sighting records
- Center for Whale Research — Background information

Data files must only be shared when permitted by their licenses or data-release agreements. The team must also decide on a code license before releasing the project for reuse.

## Contributions

- **Aung Htut:** Whale, IndividualObservation, and Flask whale interface
- **Sophia Umukoro:** DataSource, Location, and Sighting
- **Bowen Zhang:** GroupObservation, Association, and integration testing

The GitHub commit history shows our individual work.

## Report

The Milestone 4 report includes our relational model, SQL queries, architecture, interface examples, testing results, and AI-use disclosure.
