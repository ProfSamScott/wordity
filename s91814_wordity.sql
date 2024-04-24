-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: db-buf-03.sparkedhost.us:3306
-- Generation Time: Apr 24, 2024 at 02:38 PM
-- Server version: 10.6.16-MariaDB-0ubuntu0.22.04.1-log
-- PHP Version: 8.1.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `wordity`
--

-- --------------------------------------------------------

--
-- Table structure for table `wordity_counts`
--

CREATE TABLE `wordity_counts` (
  `size` int(11) NOT NULL,
  `puzzle` int(11) NOT NULL,
  `count` int(11) NOT NULL,
  `language` varchar(10) NOT NULL DEFAULT 'English',
  `rarity` varchar(10) NOT NULL DEFAULT 'common'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Table structure for table `wordity_scores`
--

CREATE TABLE `wordity_scores` (
  `size` int(11) NOT NULL,
  `puzzle` int(40) NOT NULL,
  `id` varchar(40) NOT NULL,
  `score` int(11) NOT NULL,
  `language` varchar(10) NOT NULL DEFAULT 'English',
  `rarity` varchar(10) NOT NULL DEFAULT 'common'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Table structure for table `wordmeister`
--

CREATE TABLE `wordmeister` (
  `id` varchar(40) NOT NULL,
  `puzzle` text NOT NULL,
  `contributors` varchar(200) NOT NULL DEFAULT '[]'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `wordity_counts`
--
ALTER TABLE `wordity_counts`
  ADD PRIMARY KEY (`size`,`puzzle`);

--
-- Indexes for table `wordity_scores`
--
ALTER TABLE `wordity_scores`
  ADD PRIMARY KEY (`size`,`puzzle`,`id`);

--
-- Indexes for table `wordmeister`
--
ALTER TABLE `wordmeister`
  ADD PRIMARY KEY (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
