CREATE TABLE IF NOT EXISTS recalls (
    id          SERIAL PRIMARY KEY,
    recall_id   VARCHAR(50) UNIQUE NOT NULL,
    title       TEXT NOT NULL,
    category    VARCHAR(200),
    component   TEXT,
    description TEXT,
    consequence TEXT,
    remedy      TEXT,
    report_date DATE,
    make        VARCHAR(100),
    model       VARCHAR(150),
    year        INTEGER,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recalls_make ON recalls (make);
CREATE INDEX IF NOT EXISTS idx_recalls_report_date ON recalls (report_date);
CREATE INDEX IF NOT EXISTS idx_recalls_make_year ON recalls (make, year);