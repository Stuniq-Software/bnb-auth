CREATE TABLE IF NOT EXISTS address (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    line1 text NOT NULL,
    line2 text,
    city text NOT NULL,
    state text NOT NULL,
    country text NOT NULL,
    postal_code text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text NOT NULL UNIQUE,
    password text NOT NULL,
    first_name text NOT NULL,
    last_name text NOT NULL,
    phone text NOT NULL,
    address_id uuid REFERENCES address(id),
    account_type text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);