-- Creation of users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    hashed_password VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(255)
);

-- Creation of todos table
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description VARCHAR(255),
    priority INTEGER,
    complete BOOLEAN DEFAULT FALSE,
    owner_id INTEGER REFERENCES users(id)
);