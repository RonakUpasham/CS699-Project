from flask import Flask, render_template, request

app = Flask(__name__, static_folder='static')

data = ["TATAMOTORS", "HCLTECH", "INDUSINDBK", "TATACONSUM", "NESTLEIND", "AXISBANK", "ADANIENT", "WIPRO"]

@app.route("/", methods=["GET", "POST"])
def index():
    query = request.form.get("query")
    results = []

    if query:
        results = [item for item in data if query.lower() in item.lower()]

    return render_template("index.html", query=query, results=results)

if __name__ == "__main__":
    app.run(debug=True)


