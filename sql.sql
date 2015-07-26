CREATE DATABASE IF NOT EXISTS teees;
USE teees;

CREATE TABLE `users` (
    `user_id` int(1) unsigned NOT NULL AUTO_INCREMENT,
    `username` varchar(32) NOT NULL,
    `password` varchar(255) NOT NULL,
    `email` varchar(255) NOT NULL,
    `locked` tinyint(1) NOT NULL DEFAULT '0',
    `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `last_login` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
    PRIMARY KEY (`user_id`),
    UNIQUE KEY `unique_email` (`email`),
    UNIQUE KEY `unique_username` (`username`)
);

CREATE TABLE `log` (
  `event_id` int unsigned NOT NULL AUTO_INCREMENT,
    `username` varchar(32) NOT NULL,
    `action_type` varchar(16) NOT NULL,
    `action_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `ip` int(1) unsigned DEFAULT NULL,
    `user_agent` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`event_id`)
);
