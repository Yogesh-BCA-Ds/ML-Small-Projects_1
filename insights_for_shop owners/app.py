'''
flask creates the web application
render template tells flask to get the html file in templates
'''

from flask import Flask, render_template,request
from werkzeug.utils import secure_filename
import os
from backend.preprocessing import validate_dataset
app = Flask(__name__,template_folder="frontend/templates")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/uploads",methods=["POST"])
def upload():

    if "dataset" not in request.files:
        return "no file was uploaded"
    file = request.files["dataset"]

    if file.filename == "":
        return "no file selected"

    if not file.filename.lower().endswith(".csv"):
        return "only csv files are allowed"
        
    filename = secure_filename(file.filename)
    file_path = os.path.join("uploads",filename)
    file.save(file_path) 
    # return f"file svaed successfully:{filename}"
    
    valid,missing_columns,df = validate_dataset(file_path)
    
    if not valid:
        return f"""
        data set rejected<br>
        missing columns:{missing_columns}
        """
    return f"""
    dataset accepted<br>
    file:{file_name}<br>
    rows:{len(df)}<br>
    columns:{len(df.columns)}
    """    
if __name__ == "__main__":
    app.run(debug=True)
