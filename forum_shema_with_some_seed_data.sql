CREATE DATABASE IF NOT EXISTS forum_system
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE forum_system;

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET default_storage_engine = InnoDB;

CREATE TABLE `roles` (
  role_id        INT NOT NULL AUTO_INCREMENT,
  role_name      VARCHAR(20) NOT NULL UNIQUE,
  PRIMARY KEY (role_id)
);


CREATE TABLE `users` (
  user_id         INT NOT NULL AUTO_INCREMENT,
  first_name      VARCHAR(32) NOT NULL,
  last_name       VARCHAR(32) NOT NULL,
  email           VARCHAR(254) NOT NULL UNIQUE,
  username        VARCHAR(16) NOT NULL UNIQUE,
  password_hash   VARCHAR(255) NOT NULL,
  role_id         INT NOT NULL,
  is_blocked      BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (user_id),
  FOREIGN KEY (role_id) REFERENCES roles (role_id) ON DELETE RESTRICT,
  CONSTRAINT first_name_length CHECK (CHAR_LENGTH(first_name) >= 2),
  CONSTRAINT last_name_length CHECK (CHAR_LENGTH(last_name) >= 2),
  CONSTRAINT username_length CHECK (CHAR_LENGTH(username) >= 2)
);


CREATE TABLE `topics` (
  topic_id         INT NOT NULL AUTO_INCREMENT,
  author_id        INT NOT NULL,
  title            VARCHAR(128) NOT NULL,
  content          VARCHAR(8192) NOT NULL,
  created_at       DATETIME NOT NULL DEFAULT NOW(),
  is_private       BOOLEAN NOT NULL DEFAULT FALSE,
  is_locked        BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (topic_id),
  FOREIGN KEY (author_id) REFERENCES users (user_id) ON DELETE RESTRICT,
  CONSTRAINT title_length CHECK (CHAR_LENGTH(title) >= 16),
  CONSTRAINT topics_content_length CHECK (CHAR_LENGTH(content) >= 32)
);


CREATE TABLE `replies` (
  reply_id         INT NOT NULL AUTO_INCREMENT,
  topic_id         INT NOT NULL,
  author_id        INT NOT NULL,
  content          VARCHAR(8192) NOT NULL,
  created_at       DATETIME NOT NULL DEFAULT NOW(),
  PRIMARY KEY (reply_id),
  FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE, 
  FOREIGN KEY (author_id) REFERENCES users (user_id) ON DELETE RESTRICT,
  CONSTRAINT replies_content_length CHECK (CHAR_LENGTH(content) >= 2)
);


CREATE TABLE `reply_votes` (
  user_id            INT NOT NULL,
  reply_id           INT NOT NULL,
  vote               TINYINT NOT NULL,
  PRIMARY KEY (user_id, reply_id),
  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
  FOREIGN KEY (reply_id) REFERENCES replies (reply_id) ON DELETE CASCADE,
  CONSTRAINT vote_value CHECK (vote IN (1, -1))
);


CREATE TABLE `best_replies` (
  topic_id           INT NOT NULL,
  reply_id           INT NOT NULL,
  PRIMARY KEY (topic_id),
  FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE,
  FOREIGN KEY (reply_id) REFERENCES replies (reply_id) ON DELETE CASCADE
);


CREATE TABLE `topic_members` (
  topic_id          INT NOT NULL,
  user_id           INT NOT NULL,
  PRIMARY KEY (topic_id, user_id),
  FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

INSERT INTO roles (role_name)
VALUES ('user'), ('admin');