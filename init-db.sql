SELECT 'CREATE DATABASE osmproduction' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'osmproduction')\gexec
SELECT 'CREATE DATABASE osmRh' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'osmRh')\gexec
SELECT 'CREATE DATABASE osmsecurity' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'osmsecurity')\gexec
SELECT 'CREATE DATABASE abiooc_inventory' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'abiooc_inventory')\gexec
SELECT 'CREATE DATABASE osmfinance' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'osmfinance')\gexec
SELECT 'CREATE DATABASE osmoc' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'osmoc')\gexec
