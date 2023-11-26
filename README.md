# CS699-Project
Overview

This project is a stock analysis tool that allows users to retrieve and analyze stock data from both BSE (Bombay Stock Exchange) and NSE (National Stock Exchange) using Python. The project utilizes Flask for the web interface, Plotly for data visualization, and PostgreSQL for storing scraped stock data.
Key Features
1. Web Interface

    The project provides a user-friendly web interface where users can make requests for various stock graphs.
    Users can request graphs for a single stock or compare two stocks.

2. Data Scraping

    Stock data is scraped from both BSE and NSE using Python.
    

3. Data Visualization

    Plotly is used for dynamic and interactive data visualization.
    Users can visualize different aspects of stock data, including opening and closing prices, volume, and more.

Project Structure
1. Flask App

    The Flask app handles user requests and communicates with the backend for data retrieval.
    Various routes are defined to support different functionalities, such as single stock analysis and stock comparison.

3. Data Scraping Scripts

    Python scripts are responsible for scraping stock data from BSE and NSE websites.
    The scraped data is processed and inserted into the PostgreSQL database.

4. Plotly Graphs

   Time series line graph (Historical stock price)
   Candlestick chart (Historical stock price)
   Bar Graph for relevant parameter (Eg: Volume of traded shares)
   Line Graph for Comparison of a parameter between 2 stocks 

Getting Started

    Go to this link and download v.26.2 : https://github.com/plotly/plotly.js/releases
    Extract the downloaded zip file in static folder and rename it to "plotly"
    Run the Flask app using python app.py.
    Access the web interface at http://localhost:5000 in your browser.

Dependencies

    Flask
    Plotly

Contributors

    Ronak Upasham
    Yogesh Mandlik

