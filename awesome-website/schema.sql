-- schema.sql

DROP DATABASE IF EXISTS awesome;

DROP USER IF EXISTS 'www-data'@'localhost';

CREATE DATABASE awesome;

USE awesome;

CREATE USER 'www-data'@'localhost' identified BY 'www-data';
ALTER USER 'www-data'@'localhost' identified WITH mysql_native_password by 'www-data';
grant select, insert, update, delete on awesome.* to 'www-data'@'localhost';

CREATE TABLE users (
    id VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    passwd VARCHAR(50) NOT NULL,
    admin BOOL NOT NULL,
    name VARCHAR(50) NOT NULL,
    image VARCHAR(500) NOT NULL,
    created_at REAL NOT NULL,
    unique key idx_email (email),
    key idx_created_at (created_at),
    primary key (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

create table blogs (
    id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    user_image VARCHAR(500) NOT NULL,
    name VARCHAR(50) NOT NULL,
    summary VARCHAR(200) NOT NULL,
    content MEDIUMTEXT NOT NULL,
    created_at REAL NOT NULL,
    key idx_created_at (created_at),
    primary key(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

create table comments (
    id VARCHAR(50) NOT NULL,
    blog_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    user_image VARCHAR(500) NOT NULL,
    content mediumtext NOT NULL,
    created_at real NOT NULL,
    key idx_created_at (created_at),
    primary key (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
