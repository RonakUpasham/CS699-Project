from flask import Flask, render_template, request
import pandas as pd
import plotly
import plotly.express as px

app = Flask(__name__, static_folder='static')

# Assuming 'stock_data.csv' is the CSV file with the required columns
csv_path = 'static/stock_data.csv'
df = pd.read_csv(csv_path)

@app.route("/", methods=["GET", "POST"])
def index():
    query = request.form.get("query")
    results = []
    if request.method == 'POST':
        # Extracting form data
        selected_stock = request.form.get("stock")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        # Filtering DataFrame based on selected stock and date range
        filtered_df = df[(df['Date '] >= start_date) & (df['Date '] <= end_date) & (df['series '] == selected_stock)]

        # Your Plotly graph code
        fig = px.line(filtered_df, x='Date ', y='OPEN ', title=f'Opening Prices for {selected_stock} Over Time',
                      labels={'Date': 'Date', 'OPEN': 'Opening Price'})

        # Convert the Plotly figure to HTML
        graph_html = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')

        # Render the template with the graph
        return render_template("index.html", graph_html=graph_html)

    # Render the template without the graph on initial load
    return render_template("index.html", query=query, results=results, graph_html=None)

if __name__ == "__main__":
    app.run(debug=True)



