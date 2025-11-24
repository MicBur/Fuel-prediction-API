CREATE TABLE IF NOT EXISTS stations (
    id TEXT PRIMARY KEY,
    name TEXT,
    brand TEXT,
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    street TEXT,
    house_number TEXT,
    post_code INTEGER
);

CREATE TABLE IF NOT EXISTS price_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id TEXT NOT NULL REFERENCES stations(id),
    captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    fuel_type TEXT NOT NULL,
    price_eur REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature_c REAL,
    humidity REAL,
    wind_speed_ms REAL,
    precipitation_mm REAL,
    cloud_cover_pct REAL
);

CREATE TABLE IF NOT EXISTS feature_vectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_timestamp DATETIME NOT NULL,
    fuel_type TEXT NOT NULL,
    current_price REAL,
    features_json TEXT NOT NULL,
    label_price REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
