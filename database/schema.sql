-- Cheapest Near Me — Supabase Postgres Schema

-- Enable PostGIS for geo queries (enable via Supabase dashboard Extensions)
-- CREATE EXTENSION IF NOT EXISTS postgis;

-- ─────────────────────────────────────────────
-- SHOPS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shops (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    address     TEXT NOT NULL,
    lat         DOUBLE PRECISION NOT NULL,
    lng         DOUBLE PRECISION NOT NULL,
    place_id    TEXT UNIQUE,          -- Google Places ID
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS shops_location_idx ON shops (lat, lng);

-- ─────────────────────────────────────────────
-- PRODUCTS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    category    TEXT,
    barcode     TEXT UNIQUE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS products_name_idx ON products USING gin (to_tsvector('english', name));

-- ─────────────────────────────────────────────
-- PRICES
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS prices (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id     UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    product_id  UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price       NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    reported_by TEXT,               -- anonymous session id or user email
    verified    BOOLEAN DEFAULT FALSE,
    upvotes     INTEGER DEFAULT 0,
    downvotes   INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS prices_shop_idx    ON prices (shop_id);
CREATE INDEX IF NOT EXISTS prices_product_idx ON prices (product_id);
CREATE INDEX IF NOT EXISTS prices_updated_idx ON prices (updated_at DESC);

-- Keep updated_at current automatically
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER prices_updated_at
BEFORE UPDATE ON prices
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ─────────────────────────────────────────────
-- USER REPORTS  (crowdsource verification)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_reports (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    price_id    UUID NOT NULL REFERENCES prices(id) ON DELETE CASCADE,
    reporter    TEXT,               -- anonymous session id or user email
    vote        SMALLINT NOT NULL CHECK (vote IN (1, -1)),  -- 1=confirm, -1=dispute
    note        TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS user_reports_price_idx ON user_reports (price_id);

-- ─────────────────────────────────────────────
-- CONVENIENCE VIEW: cheapest prices per product
-- ─────────────────────────────────────────────
CREATE OR REPLACE VIEW cheapest_prices AS
SELECT
    p.id            AS price_id,
    pr.name         AS product_name,
    pr.category,
    s.name          AS shop_name,
    s.address,
    s.lat,
    s.lng,
    p.price,
    p.verified,
    p.upvotes,
    p.downvotes,
    p.updated_at
FROM prices p
JOIN shops    s  ON s.id  = p.shop_id
JOIN products pr ON pr.id = p.product_id
ORDER BY pr.name, p.price ASC;