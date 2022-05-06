CREATE TABLE IF NOT EXISTS channels (username text);

CREATE TYPE status AS ENUM ('SUCCESS', 'NOT FOUND', 'COOLDOWN');
CREATE TABLE IF NOT EXISTS usage (
    channel text,
    username text,
    query text,
    time timestamp,
    command_status status
);
