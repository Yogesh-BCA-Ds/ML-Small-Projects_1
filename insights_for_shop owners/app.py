'''
flask creates the web application
render template tells flask to get the html file in templates
'''

from flask import Flask, render_template
app = Flask(__name__,template_folder="frontend/templates")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/backend")
def backend():
    return "congratulations backend connected"

if __name__ == "__main__":
    app.run(debug=True)