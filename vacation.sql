--
-- Database: `vacation`
--

-- --------------------------------------------------------

--
-- Table structure for table `outofoffice`
--

CREATE TABLE IF NOT EXISTS `outofoffice` (
  `username` varchar(64) NOT NULL DEFAULT '',
  `startdate` datetime DEFAULT NULL,
  `enddate` datetime DEFAULT NULL,
  `subject` text,
  `bodytext` text,
  `ooofrom` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`username`),
  KEY `enddate` (`enddate`),
  KEY `startdate` (`startdate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `outofoffice_log`
--

CREATE TABLE IF NOT EXISTS `outofoffice_log` (
  `recipient` varchar(255) NOT NULL,
  `sender` varchar(255) NOT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`created`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
