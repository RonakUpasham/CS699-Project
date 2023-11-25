from flask import Flask, render_template, request
import pandas as pd
import plotly
import plotly.express as px
from datetime import datetime
from io import StringIO
from cv2 import goodFeaturesToTrack
import requests
import plotly.graph_objects as go

app = Flask(__name__, static_folder='static')

# Function to get historical stock data
def getHistoryData(company, from_date, to_date):
    session = requests.session()
    headers = {"user-agent": "Chrome/87.0.4280.88"}
    head = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ""Chrome/87.0.4280.88 Safari/537.36 "}

    session.get("https://www.nseindia.com", headers=head)
    session.get("https://www.nseindia.com/get-quotes/equity?symbol=" + company, headers=head)  
    session.get("https://www.nseindia.com/api/historical/cm/equity?symbol="+company, headers=head)
    url = "https://www.nseindia.com/api/historical/cm/equity?symbol=" + company + "&series=[%22EQ%22]&from=" + from_date + "&to=" + to_date + "&csv=true"
    webdata = session.get(url=url, headers=head)
    df = pd.read_csv(StringIO(webdata.text[3:]))
    return df

# Function to create candlestick plot
def candlestick_plot(stock_name, from_date, to_date):
    df = getHistoryData(stock_name, from_date=from_date, to_date=to_date)
    df['OPEN '] = pd.to_numeric(df['OPEN '].str.replace(',', ''), errors='coerce')
    df['HIGH '] = pd.to_numeric(df['HIGH '].str.replace(',', ''), errors='coerce')
    df['LOW '] = pd.to_numeric(df['LOW '].str.replace(',', ''), errors='coerce')
    df['close '] = pd.to_numeric(df['close '].str.replace(',', ''), errors='coerce')
    df['Date '] = pd.to_datetime(df['Date '], format='%d-%b-%Y')

    # Create a candlestick trace
    trace = go.Candlestick(x=df['Date '],
                           open=df['OPEN '],
                           high=df['HIGH '],
                           low=df['LOW '],
                           close=df['close '])

    # Create a layout for the figure
    layout = dict(title='Candlestick Chart for Stock Prices',
                  xaxis=dict(title='Date'),
                  yaxis=dict(title='Stock Price'),
                  xaxis_rangeslider_visible=False)

    # Create the figure
    fig = go.Figure(data=[trace], layout=layout)

    return fig
# Function to create line plot
def line_plot(stock_name, from_date, to_date):
    df = getHistoryData(stock_name, from_date=from_date, to_date=to_date)
    df['Date '] = pd.to_datetime(df['Date '], format='%d-%b-%Y')
    df['OPEN '] = pd.to_numeric(df['OPEN '].str.replace(',', ''), errors='coerce')

    fig = px.line(df, x='Date ', y='OPEN ', title=f'Opening Prices for {stock_name} Over Time',
                  labels={'Date': 'Date', 'OPEN': 'Opening Price'})

    return fig

# Flask route to handle form submission and display the plot
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        selected_stock = request.form.get("stock")
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")        
        
        # Parse input strings to datetime objects
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
        
        # Check if the user selected a line or candlestick plot
        plot_type = request.form.get("plot_type")

        if plot_type == "line":
            # Call the line_plot function with form data
            fig = line_plot(selected_stock, start_date, end_date)
        elif plot_type == "candlestick":
            # Call the candlestick_plot function with form data
            fig = candlestick_plot(selected_stock, start_date, end_date)

        # Convert the Plotly figure to HTML
        graph_html = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')

        # Render the template with the graph
        return render_template("index.html", graph_html=graph_html)

    # Render the template without the graph on initial load
    return render_template("index.html", graph_html=None)

if __name__ == "__main__":
    app.run(debug=True)
