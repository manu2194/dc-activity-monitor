# DC Activity Monitor

A Python script to scrape event data from a website and save it to a JSON file.

## Purpose
--------

This script is designed to extract event data from a website and store it in a structured format for further use. The script uses BeautifulSoup and requests libraries to fetch and parse the HTML content of the website.

## How to Use
-------------

1. Clone the repository to your local machine.
2. Navigate to the project directory and run `uv install` to install the required dependencies.
3. Once the installation is complete, run `uv run app.py` to execute the script.
4. The script will fetch the event data from the website and save it to a JSON file named `events.json`.

## Synopsis
----------

The script consists of the following components:

* `fetch_html`: Fetches the HTML content of the website using the `requests` library.
* `parse_events`: Parses the HTML content to extract event data using BeautifulSoup.
* `get_events`: Calls the above functions to fetch and parse the event data.
* `main`: Runs the `get_events` function and saves the event data to a JSON file.

## Requirements
------------

* This project uses the `uv` package manager. Make sure you have `uv` installed and configured on your system.
* The required dependencies are specified in the `uv.lock` file and will be installed automatically when you run `uv install`.

## Notes
-----

* The script assumes that the website structure and event data format remain the same.
* The script may need to be modified if the website structure or event data format changes.
* The script is for educational purposes only and should not be used for commercial purposes without permission from the website owner.