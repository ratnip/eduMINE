-- phpMyAdmin SQL Dump
-- version 3.3.9
-- http://www.phpmyadmin.net
--
-- Računalo: localhost
-- Vrijeme generiranja: Ruj 24, 2016 u 11:28 AM
-- Verzija poslužitelja: 5.1.73
-- PHP verzija: 5.3.29-1~dotdeb.0

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Baza podataka: `snalukahum`
--

-- --------------------------------------------------------

--
-- Tablična struktura za tablicu `assess_trust`
--

CREATE TABLE IF NOT EXISTS `assess_trust` (
  `userID` int(11) NOT NULL,
  `idFriend` bigint(20) NOT NULL,
  `questionID` int(11) NOT NULL,
  `trust_level` enum('1','2','3','4','5','0') COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`userID`,`idFriend`,`questionID`),
  KEY `questionID` (`questionID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Tablična struktura za tablicu `compare_two`
--

CREATE TABLE IF NOT EXISTS `compare_two` (
  `userID` int(11) NOT NULL,
  `idFriend1` bigint(20) NOT NULL,
  `idFriend2` bigint(20) NOT NULL,
  `better_friend` enum('1','2','0') COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`userID`,`idFriend1`,`idFriend2`),
  KEY `userID` (`userID`),
  KEY `idFriend1` (`idFriend1`),
  KEY `idFriend2` (`idFriend2`),
  KEY `userID_2` (`userID`,`idFriend2`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Tablična struktura za tablicu `friend_groups`
--

CREATE TABLE IF NOT EXISTS `friend_groups` (
  `userID` int(11) NOT NULL,
  `idFriend` bigint(20) NOT NULL,
  `groupID` int(11) NOT NULL,
  PRIMARY KEY (`userID`,`idFriend`),
  KEY `groupID` (`groupID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Tablična struktura za tablicu `group_types`
--

CREATE TABLE IF NOT EXISTS `group_types` (
  `id` int(11) NOT NULL,
  `group_type` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Tablična struktura za tablicu `logs`
--

CREATE TABLE IF NOT EXISTS `logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userId` int(11) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `ip_address` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `browser_type` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `got_data_time` datetime DEFAULT NULL,
  `got_data_2_time` datetime DEFAULT NULL,
  `got_data` tinyint(4) DEFAULT NULL,
  `got_data_2` int(11) DEFAULT NULL,
  `got_data_3` tinyint(4) DEFAULT NULL,
  `got_data_3_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Tablična struktura za tablicu `neispravni_upiti`
--

CREATE TABLE IF NOT EXISTS `neispravni_upiti` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vrijeme` datetime DEFAULT NULL,
  `ip_address` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `browser_type` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `upit` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Tablična struktura za tablicu `questions`
--

CREATE TABLE IF NOT EXISTS `questions` (
  `id` int(11) NOT NULL,
  `question_text` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Unutarnja struktura za pregledavanje `tokeni`
--
CREATE TABLE IF NOT EXISTS `tokeni` (
`id` int(11)
,`token` text
);
-- --------------------------------------------------------

--
-- Tablična struktura za tablicu `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `age` int(11) DEFAULT NULL,
  `sex` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `country` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `profession` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `profession_detail` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `razred` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `finish` int(11) NOT NULL,
  `feedback` enum('1','2','3','4','5') COLLATE utf8_unicode_ci DEFAULT NULL,
  `comment` text COLLATE utf8_unicode_ci,
  `token` text COLLATE utf8_unicode_ci,
  `vrijemePreuzimanjaTokena` datetime DEFAULT NULL,
  `valjanostTokena` int(11) DEFAULT NULL COMMENT 'valjanost tokena od trenutka preuzimanja',
  `preuzetToken` enum('0','1','2','3','4','5','6','7','8','9','10','11','12','13') COLLATE utf8_unicode_ci NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Tablična struktura za tablicu `user_friend`
--

CREATE TABLE IF NOT EXISTS `user_friend` (
  `idFriend` bigint(20) NOT NULL,
  `userID` int(11) NOT NULL,
  `weight_score` float DEFAULT NULL,
  `picture` text COLLATE utf8_unicode_ci,
  `feed_like` int(11) DEFAULT NULL,
  `feed_comment` int(11) DEFAULT NULL,
  `feed_addressed` int(11) DEFAULT NULL,
  `feed_together_in_post` int(11) DEFAULT NULL,
  `mutual_photo_published_by_user` int(11) DEFAULT NULL,
  `mutual_photo_published_by_friend` int(11) DEFAULT NULL,
  `mutual_photo_published_by_others` int(11) DEFAULT NULL,
  `photo_like` int(11) DEFAULT NULL,
  `photo_comment` int(11) DEFAULT NULL,
  `friend_mutual` int(11) DEFAULT NULL,
  `inbox_chat` int(11) DEFAULT NULL,
  `my_photo_likes` int(11) DEFAULT NULL,
  `my_status_likes` int(11) DEFAULT NULL,
  `my_link_likes` int(11) DEFAULT NULL,
  `is_family` int(11) DEFAULT NULL,
  `is_close_friend` int(11) DEFAULT NULL,
  PRIMARY KEY (`idFriend`,`userID`,`name`),
  KEY `userID` (`userID`),
  KEY `idFriend` (`idFriend`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


--
-- Ograničenja za izbačene tablice
--

--
-- Ograničenja za tablicu `assess_trust`
--
ALTER TABLE `assess_trust`
  ADD CONSTRAINT `assess_trust_ibfk_1` FOREIGN KEY (`questionID`) REFERENCES `questions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `assess_trust_ibfk_2` FOREIGN KEY (`userID`, `idFriend`) REFERENCES `user_friend` (`userID`, `idFriend`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ograničenja za tablicu `compare_two`
--
ALTER TABLE `compare_two`
  ADD CONSTRAINT `compare_two_ibfk_1` FOREIGN KEY (`userID`, `idFriend1`) REFERENCES `user_friend` (`userID`, `idFriend`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `compare_two_ibfk_2` FOREIGN KEY (`userID`, `idFriend2`) REFERENCES `user_friend` (`userID`, `idFriend`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ograničenja za tablicu `friend_groups`
--
ALTER TABLE `friend_groups`
  ADD CONSTRAINT `friend_groups_ibfk_1` FOREIGN KEY (`groupID`) REFERENCES `group_types` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `friend_groups_ibfk_2` FOREIGN KEY (`userID`, `idFriend`) REFERENCES `user_friend` (`userID`, `idFriend`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ograničenja za tablicu `logs`
--
ALTER TABLE `logs`
  ADD CONSTRAINT `logs_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ograničenja za tablicu `user_friend`
--
ALTER TABLE `user_friend`
  ADD CONSTRAINT `user_friend_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
