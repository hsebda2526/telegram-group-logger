CREATE USER telegram_user WITH PASSWORD 'supersecret';
CREATE DATABASE telegram OWNER telegram_user;
GRANT ALL PRIVILEGES ON DATABASE telegram TO telegram_user;