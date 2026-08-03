'''
flask creates the web application
render template tells flask to get the html file in templates
'''

from flask import Flask, render_template,request
from werkzeug.utils import secure_filename
import os
from backend.preprocessing import validate_dataset
from backend.preprocessing import read_file,preprocess_data
app = Flask(__name__,template_folder="frontend/templates")

@app.route("/")
def home():
    return render_template("index.html")

allowed_extension = {"csv","xlsx","xls"}

def allowed_file(filename):
    return(
        "." in filename and filename.rsplit(".",1)[1].lower() in allowed_extension)
        
    
@app.route("/uploads",methods=["POST"])
def upload():

    if "dataset" not in request.files:
        return "no file was uploaded"
    file = request.files["dataset"]
    if file.filename == "":
        return "no file selected"
    filename = secure_filename(file.filename)
    file_path = os.path.join("uploads",filename)
    file.save(file_path) 
    # return f"file svaed successfully:{filename}"

    if not allowed_file(filename):
        return "only csv and excel file are allowed"

    valid,missing_columns,df = validate_dataset(file_path)
    
    if not valid:
        return f"""
        data set rejected<br>
        missing columns:{missing_columns}
        """

    df = read_file(file)
    df = preprocess_data(df)
    
    return f"""
    dataset accepted<br>
    file:{file_name}<br>
    rows:{len(df)}<br>
    columns:{len(df.columns)}
    """    

    
if __name__ == "__main__":
    app.run(debug=True)
