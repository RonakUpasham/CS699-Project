from flask import Flask, render_template, request
import pandas as pd
import plotly
import plotly.express as px
from datetime import datetime
from io import StringIO
from cv2 import goodFeaturesToTrack
import requests
import plotly.graph_objects as go
import plotly.subplots as sp

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime


app = Flask(__name__, static_folder='static')

def getNSEHistoryData(company, from_date, to_date):
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

def scrape_data(stock_name, from_date, to_date):
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-gpu')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)

    driver.get('https://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?flag=0&type=ETF')

    driver.find_element(By.XPATH, "//input[@value='rad_no1']").click()
    search = driver.find_element(By.ID, "ContentPlaceHolder1_smartSearch")
    search.send_keys(stock_name)
    search.send_keys(Keys.RETURN)

    start_date = datetime.datetime.strptime(from_date, "%d/%m/%Y")
    end_date = datetime.datetime.strptime(to_date, "%d/%m/%Y")

    chunk_size = 26

    current_date = start_date
    columns = ["Date","Open","High","Low","Close","WAP","No. of Shares","No. of Trades","Total Turnover"]
    df = pd.DataFrame(columns=columns)
    while current_date < end_date:
        date_from = current_date.strftime("%d/%m/%Y")
        date_to = (current_date + datetime.timedelta(days=chunk_size - 1)).strftime("%d/%m/%Y")

        date_input = driver.find_element(By.ID, "ContentPlaceHolder1_txtFromDate")
        driver.execute_script("arguments[0].value = '{}';".format(date_from), date_input)

        date_input = driver.find_element(By.ID, "ContentPlaceHolder1_txtToDate")
        driver.execute_script("arguments[0].value = '{}';".format(date_to), date_input)

        date_input.send_keys(Keys.RETURN)
        submit_button = driver.find_element(By.ID, "ContentPlaceHolder1_btnSubmit")
        submit_button.click()

        wait = WebDriverWait(driver, 10)
        table = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_spnStkData")))

        table_html = table.get_attribute('outerHTML')

        soup = BeautifulSoup(table_html, 'html.parser')

        data = []
        for row in soup.find_all('tr', class_='TTRow'):
            date = row.find('td', class_='TTRow_left10').text.strip()
            values = [td.text.replace(',', '') for td in row.find_all('td', class_='tdcolumn text-right')][0:8]
            data.append([date] + values)

        df_chunk = pd.DataFrame(data, columns=columns)

        df = pd.concat([df, df_chunk], ignore_index=True)

        current_date += datetime.timedelta(days=chunk_size)

    driver.quit()
    return df

def NSE_line_plot(df):
    df['Date '] = pd.to_datetime(df['Date '], format='%d-%b-%Y')
    df['OPEN '] = pd.to_numeric(df['OPEN '].str.replace(',', ''), errors='coerce')
    df['VOLUME '] = pd.to_numeric(df['VOLUME '].str.replace(',', ''), errors='coerce')

    fig = sp.make_subplots(rows=2, cols=1, shared_xaxes=True,
                           subplot_titles=('Opening Prices Over Time', 'Volume Over Time'),
                           vertical_spacing=0.1, row_heights=[0.8, 0.2])

    trace_open = go.Scatter(x=df['Date '], y=df['OPEN '], mode='lines', name='Opening Price')
    fig.add_trace(trace_open, row=1, col=1)

    trace_volume = go.Bar(x=df['Date '], y=df['VOLUME '], name='Volume')
    fig.add_trace(trace_volume, row=2, col=1)

    fig.update_layout(title_text=f'Opening Prices and Volume Over Time for (NSE)', height=600)

    return fig

def NSE_candlestick_plot(df):
    #df['OPEN '] = pd.to_numeric(df['OPEN '].str.replace(',', ''), errors='coerce')
    df['HIGH '] = pd.to_numeric(df['HIGH '].str.replace(',', ''), errors='coerce')
    df['LOW '] = pd.to_numeric(df['LOW '].str.replace(',', ''), errors='coerce')
    df['close '] = pd.to_numeric(df['close '].str.replace(',', ''), errors='coerce')
    df['Date '] = pd.to_datetime(df['Date '], format='%d-%b-%Y')

    fig = go.Figure(data=[go.Candlestick(x=df['Date '],
                                         open=df['OPEN '],
                                         high=df['HIGH '],
                                         low=df['LOW '],
                                         close=df['close '])])

    fig.update_layout(title='Candlestick Chart for Stock Prices',
                      xaxis_title='Date',
                      yaxis_title='Stock Price',
                      xaxis_rangeslider_visible=False,
                      height=600)

    return fig

def NSE_line_compare(df_1, df_2, label_1='Line 1', label_2='Line 2'):
    try:
        df_2['Date '] = pd.to_datetime(df_2['Date '], format='%d-%b-%Y')
    except:
        pass
    try:
        df_2['OPEN '] = pd.to_numeric(df_2['OPEN '].str.replace(',', ''), errors='coerce')
    except:
        pass
    try:
        df_1['Date '] = pd.to_datetime(df_1['Date '], format='%d-%b-%Y')
    except:
        pass
    try:
        df_1['OPEN '] = pd.to_numeric(df_1['OPEN '].str.replace(',', ''), errors='coerce')
    except:
        pass

    fig = sp.make_subplots(rows=2, cols=1, shared_xaxes=True,
                           subplot_titles=(label_1, label_2),
                           vertical_spacing=0.1)

    trace_1 = go.Scatter(x=df_1['Date '], y=df_1['OPEN '], mode='lines', name=label_1)
    trace_2 = go.Scatter(x=df_2['Date '], y=df_2['OPEN '], mode='lines', name=label_2)

    fig.add_trace(trace_1, row=1, col=1)
    fig.add_trace(trace_2, row=2, col=1)

    fig.update_layout(title_text='Opening Prices Over Time', height=600)

    return fig
    

def BSE_line_plot(df):
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')
    df['Open'] = pd.to_numeric(df['Open'].str.replace(',', ''), errors='coerce')
    df['No. of Shares'] = pd.to_numeric(df['No. of Shares'].str.replace(',', ''), errors='coerce')

    fig = sp.make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=['Opening Prices Over Time', 'Volume Over Time'],
                        vertical_spacing=0.1, row_heights=[0.8, 0.2])

    trace_open = go.Scatter(x=df['Date'], y=df['Open'], mode='lines', name='Opening Price')
    fig.add_trace(trace_open, row=1, col=1)

    trace_volume = go.Bar(x=df['Date'], y=df['No. of Shares'], name='Volume')
    fig.add_trace(trace_volume, row=2, col=1)

    fig.update_layout(title_text='Opening Prices and Volume Over Time', height=600)

    return fig

def BSE_candlestick_plot(df):
    #df['Open'] = pd.to_numeric(df['Open'].str.replace(',', ''), errors='coerce')
    df['High'] = pd.to_numeric(df['High'].str.replace(',', ''), errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'].str.replace(',', ''), errors='coerce')
    df['Close'] = pd.to_numeric(df['Close'].str.replace(',', ''), errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')

    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])

    fig.update_layout(title='Candlestick Chart for Stock Prices',
                      xaxis_title='Date',
                      yaxis_title='Stock Price',
                      xaxis_rangeslider_visible=False,
                      height=600)

    return fig
    
def BSE_line_compare(df_1, df_2, label_1='Line 1', label_2='Line 2'):
    df_1['Date'] = pd.to_datetime(df_1['Date'], format='%d/%m/%y')

    df_1['Open'] = pd.to_numeric(df_1['Open'].str.replace(',', ''), errors='coerce')
    
    df_2['Date'] = pd.to_datetime(df_2['Date'], format='%d/%m/%y')

    df_2['Open'] = pd.to_numeric(df_2['Open'].str.replace(',', ''), errors='coerce')

    fig = sp.make_subplots(rows=2, cols=1, shared_xaxes=True,
                           subplot_titles=(label_1, label_2),
                           vertical_spacing=0.1)

    trace_1 = go.Scatter(x=df_1['Date'], y=df_1['Open'], mode='lines', name=label_1)
    trace_2 = go.Scatter(x=df_2['Date'], y=df_2['Open'], mode='lines', name=label_2)

    fig.add_trace(trace_1, row=1, col=1)
    fig.add_trace(trace_2, row=2, col=1)

    fig.update_layout(title_text='Opening Prices Over Time', height=600)

    return fig
    

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        selected_stock = request.form.get("stock")
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")        
        num_stocks = int(request.form.get("num"))

        plot_type = request.form.get("plot_type")
        exchange_type = request.form.get("website")

        if exchange_type == "BSE":
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
            df = scrape_data(selected_stock, start_date, end_date)

            if num_stocks == 1:
                fig1 = BSE_line_plot(df)
                fig2 = BSE_candlestick_plot(df)
            elif num_stocks == 2:
                selected_stock_2 = request.form.get("stock2")
                df_2 = scrape_data(selected_stock_2, start_date, end_date)
                fig1 = BSE_line_compare(df, df_2, label_1=selected_stock, label_2=selected_stock_2)

        elif exchange_type == "NSE":
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
            df = getNSEHistoryData(selected_stock,from_date=start_date,to_date=end_date)
            if num_stocks == 1:
                fig1 = NSE_line_plot(df)
                fig2 = NSE_candlestick_plot(df)
            elif num_stocks == 2:
                selected_stock_2 = request.form.get("stock2")
                df_2 = getNSEHistoryData(selected_stock_2, from_date=start_date, to_date=end_date)
                fig1 = NSE_line_compare(df, df_2, label_1=selected_stock, label_2=selected_stock_2)

        graph_html1 = plotly.offline.plot(fig1, include_plotlyjs=False, output_type='div')
        if(num_stocks == 1):
            graph_html2 = plotly.offline.plot(fig2, include_plotlyjs=False, output_type='div')
            return render_template("index.html", graph_html1=graph_html1, graph_html2=graph_html2, num_stocks=num_stocks)
        else:
            return render_template("index.html", comparison_graph_html=graph_html1, num_stocks=num_stocks)


    return render_template("index.html", graph_html1=None, graph_html2=None, num_stocks=None)


if __name__ == "__main__":
    app.run(debug=True)
