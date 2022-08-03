<!-- PROJECT INTRO -->
<div align="center">

  <h1 align="center">Solving nutritional and allergen missing information in a foodtech company: A data-based approach</h1>

  <p align="center">
    This repo contains all files and scripts developed for this dissertation.
  </p>
</div>

## App ingredient match
Contains all files to deploy an API server with two endpoints:
- **Match ingredients:** recieves ingredient names as a list in the request, and returns the best-matching id from the standardised taxonomy, as well as its matching score (between 0 and 1).
- **Get properties:** given a list of standardised ids, returns all nutritional and allergen properties from those ingredients.

The directory contains a Dockerfile to build images containing the server. It also requires a connection to a database containing support data.

## App management
Contains all scripts and files to maintain the application. These include:
- Ingesting new data, whether stopwords or taxonomy elements.
- Re-training the model and nutrition database.
- Generate a summary table of all standardised ingredients, nutritional properties and allergens.

## Dissertation figures
Contains Jupyter notebooks with the code and data used to build all visualisations in the dissertation document.

## Pantry construction
Contains all developing and testing scripts used to create the application. This directory should be consulted as a guideline, instead of a production-ready folder.