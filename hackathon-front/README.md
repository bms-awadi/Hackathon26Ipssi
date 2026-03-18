# Plateforme de gestion documentaire intelligente

Application front développée dans le cadre d’un **hackathon**, avec pour objectif de centraliser, analyser et exploiter des documents administratifs fournisseurs à travers une interface métier simple et organisée.

## Objectif du projet

Cette application permet de :

- importer des documents administratifs
- simuler leur traitement automatique
- afficher les informations extraites dans une vue **CRM**
- afficher les statuts, anomalies et dates d’expiration dans une vue **Conformité**
- gérer l’accès aux pages selon le **rôle utilisateur**

Le projet s’inscrit dans une architecture plus large où les documents sont traités par un pipeline backend / OCR / validation, puis transmis au frontend sous forme de données structurées.

## Fonctionnalités principales

- **Page d’accueil**
  - présentation de la plateforme
  - statistiques globales
  - accès à la connexion et à l’inscription

- **Authentification simple**
  - inscription
  - connexion
  - stockage temporaire avec `localStorage`
  - profil utilisateur
  - déconnexion

- **Gestion des rôles**
  - opérateur
  - comptable / CRM
  - conformité

- **Protection des routes**
  - chaque utilisateur accède uniquement à la vue correspondant à son rôle

- **Vue Opérateur**
  - upload multi-documents
  - ajout de fichiers
  - suppression de fichiers
  - message de statut simulé

- **Vue CRM**
  - affichage des dossiers fournisseurs
  - recherche
  - filtres par statut
  - détail d’un dossier fournisseur

- **Vue Conformité**
  - tableau de bord documentaire
  - statuts des documents
  - anomalies détectées
  - dates d’expiration
  - score de confiance

## Technologies utilisées

- **React.js**
- **JavaScript**
- **React Router DOM**
- **CSS**
- **localStorage** pour la simulation de l’authentification
- **Données mockées** pour simuler les données backend

## Structure du projet

```bash
src/
  components/
    Header.jsx
    ProtectedRoute.jsx
    UploadBox.jsx
    SupplierForm.jsx
    ComplianceTable.jsx
  pages/
    HomePage.jsx
    LoginPage.jsx
    RegisterPage.jsx
    ProfilePage.jsx
    OperatorPage.jsx
    CRMPage.jsx
    SupplierDetailPage.jsx
    CompliancePage.jsx
  data/
    mockData.js
  App.jsx
  main.jsx
  index.css