-- CREATE TABLE IF NOT EXISTS users(
--     username VARCHAR UNIQUE,
--     age INT,
--     occupation VARCHAR
-- )

CREATE TABLE IF NOT EXISTS todo(
    username VARCHAR UNIQUE,
    title VARCHAR,
    content VARCHAR,
    created_at DATE,
    last_edited_at DATE
)