-- phpMyAdmin SQL Dump
-- version 4.5.4.1
-- http://www.phpmyadmin.net
--
-- Client :  localhost
-- Généré le :  Mer 02 Juin 2021 à 18:23
-- Version du serveur :  5.7.11
-- Version de PHP :  5.6.18

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


-- Database: veprim_kadirolli_1b_bd

--

-- Database: veprim_kadirolli_1b_bd
-- Détection si une autre base de donnée du même nom existe

DROP DATABASE IF EXISTS veprim_kadirolli_1b_bd;

-- Création d'un nouvelle base de donnée

CREATE DATABASE IF NOT EXISTS veprim_kadirolli_1b_bd;

-- Utilisation de cette base de donnée

USE veprim_kadirolli_1b_bd;

-- --------------------------------------------------------

--
-- Structure de la table `t_championnat`
--

CREATE TABLE `t_championnat` (
  `ID_championnat` int(42) NOT NULL,
  `nom_championnat` varchar(42) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `t_equipe`
--

CREATE TABLE `t_equipe` (
  `ID_equipe` int(42) NOT NULL,
  `nom_equipe` varchar(42) DEFAULT NULL,
  `nom_president_equipe` varchar(42) DEFAULT NULL,
  `nom_entraineur_equipe` varchar(42) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Contenu de la table `t_equipe`
--

INSERT INTO `t_equipe` (`ID_equipe`, `nom_equipe`, `nom_president_equipe`, `nom_entraineur_equipe`) VALUES
(1, 'Lakers', 'de merde', 'Phil Jackson'),
(2, 'Boston', 'Jaccard', 'Rickerts london');

-- --------------------------------------------------------

--
-- Structure de la table `t_equipe_joueur`
--

CREATE TABLE `t_equipe_joueur` (
  `id_dfgd` int(11) NOT NULL,
  `FK_equipe` int(11) NOT NULL,
  `FK_joueur` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Contenu de la table `t_equipe_joueur`
--

INSERT INTO `t_equipe_joueur` (`id_dfgd`, `FK_equipe`, `FK_joueur`) VALUES
(1, 1, 2),
(2, 2, 2);

-- --------------------------------------------------------

--
-- Structure de la table `t_joueur`
--

CREATE TABLE `t_joueur` (
  `ID_joueur` int(42) NOT NULL,
  `nom_joueur` varchar(42) DEFAULT NULL,
  `prenom_joueur` varchar(42) DEFAULT NULL,
  `date_de_naissance` date DEFAULT NULL,
  `taille_joueur` int(255) DEFAULT NULL,
  `poids_joueur` int(255) DEFAULT NULL,
  `type_de_poste` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Contenu de la table `t_joueur`
--

INSERT INTO `t_joueur` (`ID_joueur`, `nom_joueur`, `prenom_joueur`, `date_de_naissance`, `taille_joueur`, `poids_joueur`, `type_de_poste`) VALUES
(1, 'Jordan', 'Michael', '1963-02-17', 198, 90, '0'),
(2, 'ffurzu', 'tzutut', '2021-06-02', 6757, 56756, 'rzrtz');

-- --------------------------------------------------------

--
-- Structure de la table `t_match`
--

CREATE TABLE `t_match` (
  `ID_match` int(42) NOT NULL,
  `date_de_rencontre` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `score_equipe` int(255) NOT NULL,
  `FK_joueur` int(42) NOT NULL,
  `FK_statistique_joueur` int(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Contenu de la table `t_match`
--

INSERT INTO `t_match` (`ID_match`, `date_de_rencontre`, `score_equipe`, `FK_joueur`, `FK_statistique_joueur`) VALUES
(1, '2021-03-04 18:03:23', 102, 1, 1);

-- --------------------------------------------------------

--
-- Structure de la table `t_statistique_joueur`
--

CREATE TABLE `t_statistique_joueur` (
  `ID_statistique_joueur` int(255) NOT NULL,
  `point_marquer_joueur` int(255) NOT NULL,
  `passe desicive_joueur` int(255) NOT NULL,
  `interception_joueur` int(255) NOT NULL,
  `contre_joueur` int(255) NOT NULL,
  `rebond_joueur` int(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Contenu de la table `t_statistique_joueur`
--

INSERT INTO `t_statistique_joueur` (`ID_statistique_joueur`, `point_marquer_joueur`, `passe desicive_joueur`, `interception_joueur`, `contre_joueur`, `rebond_joueur`) VALUES
(1, 32, 8, 4, 7, 5);

--
-- Index pour les tables exportées
--

--
-- Index pour la table `t_championnat`
--
ALTER TABLE `t_championnat`
  ADD PRIMARY KEY (`ID_championnat`);

--
-- Index pour la table `t_equipe`
--
ALTER TABLE `t_equipe`
  ADD PRIMARY KEY (`ID_equipe`);

--
-- Index pour la table `t_equipe_joueur`
--
ALTER TABLE `t_equipe_joueur`
  ADD PRIMARY KEY (`id_dfgd`),
  ADD KEY `FK_equipe` (`FK_equipe`),
  ADD KEY `FK_joueur` (`FK_joueur`);

--
-- Index pour la table `t_joueur`
--
ALTER TABLE `t_joueur`
  ADD PRIMARY KEY (`ID_joueur`);

--
-- Index pour la table `t_match`
--
ALTER TABLE `t_match`
  ADD PRIMARY KEY (`ID_match`),
  ADD KEY `FK_joueur` (`FK_joueur`),
  ADD KEY `FK_statistique_joueur` (`FK_statistique_joueur`);

--
-- Index pour la table `t_statistique_joueur`
--
ALTER TABLE `t_statistique_joueur`
  ADD PRIMARY KEY (`ID_statistique_joueur`);

--
-- AUTO_INCREMENT pour les tables exportées
--

--
-- AUTO_INCREMENT pour la table `t_championnat`
--
ALTER TABLE `t_championnat`
  MODIFY `ID_championnat` int(42) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `t_equipe`
--
ALTER TABLE `t_equipe`
  MODIFY `ID_equipe` int(42) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT pour la table `t_equipe_joueur`
--
ALTER TABLE `t_equipe_joueur`
  MODIFY `id_dfgd` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT pour la table `t_joueur`
--
ALTER TABLE `t_joueur`
  MODIFY `ID_joueur` int(42) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT pour la table `t_match`
--
ALTER TABLE `t_match`
  MODIFY `ID_match` int(42) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT pour la table `t_statistique_joueur`
--
ALTER TABLE `t_statistique_joueur`
  MODIFY `ID_statistique_joueur` int(255) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
--
-- Contraintes pour les tables exportées
--

--
-- Contraintes pour la table `t_equipe_joueur`
--
ALTER TABLE `t_equipe_joueur`
  ADD CONSTRAINT `t_equipe_joueur_ibfk_1` FOREIGN KEY (`FK_equipe`) REFERENCES `t_equipe` (`ID_equipe`),
  ADD CONSTRAINT `t_equipe_joueur_ibfk_2` FOREIGN KEY (`FK_joueur`) REFERENCES `t_joueur` (`ID_joueur`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
