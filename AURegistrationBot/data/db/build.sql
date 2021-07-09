CREATE TABLE IF NOT EXISTS giantcard (
	UserID integer PRIMARY KEY,
	EventNumber DEFAULT 0
);

CREATE TABLE IF NOT EXISTS obeliskdeck (
	UserID integer PRIMARY KEY,
	EventNumber DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sliferdeck (
	UserID integer PRIMARY KEY,
	EventNumber DEFAULT 0
);

CREATE TABLE IF NOT EXISTS speedduel (
	UserID integer PRIMARY KEY,
	EventNumber DEFAULT 0
);

CREATE TABLE IF NOT EXISTS winamat (
	UserID integer PRIMARY KEY,
	EventNumber DEFAULT 0
);