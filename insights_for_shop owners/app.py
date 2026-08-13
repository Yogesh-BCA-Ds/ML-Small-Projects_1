'''
flask creates the web application
render template tells flask to get the html file in templates
'''
import os
from flask import Flask, render_template,request
from werkzeug.utils import secure_filename
from backend.data_validation import read_file
from backend.data_profile import profile
from backend.retail_validator import validate_retail

app = Flask(__name__,template_folder="frontend/templates")


allowed_extension = {"csv","xlsx","xls"}

def allowed_file(filename):
    return(
        "." in filename and filename.rsplit(".",1)[1].lower() in allowed_extension)

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
    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        return "only csv and excel file are allowed"
    file_path = os.path.join("uploads",filename)
    file.save(file_path) 
    #return f"file svaed successfully:{filename}"
    df = read_file(filename,file_path)
    if df is None:
        return "unable to read the file"
    if df.empty:
        return "the dataset is empty"
    if df.columns.duplicated().any():
        return "dataset has duplicate columns"
    rows, columns = df.shape
    profile_info = profile(df)
    retail_result = validate_retail(df.columns,profile_info)
    print("\n========== RETAIL VALIDATION ==========")

    print("\nMatched Families:")
    print(retail_result["matched_families"])

    print("\nDetected Concepts:")
    print(retail_result["detected_concepts"])

    print("\nStrong Signals:")
    print(retail_result["strong_signals"])

    print("\nSupporting Signals:")
    print(retail_result["supporting_signals"])

    print("\nWeak Signals:")
    print(retail_result["weak_signals"])

    print("\nEvidence Score:")
    print(retail_result["evidence_score"])

    print("\nCombination Evidence:")
    print(retail_result["combination_evidence"])

    print("\nStructural Evidence:")
    print(retail_result["structural_evidence"])

    print("\nFinal Confidence:")
    print(retail_result["final_confidence"],"%")
    print("\nDecision:")
    print(retail_result["decision"])

    print("\n======================================")
    
    return render_template(
    "index.html",
    success=True,
    rows=rows,
    columns=columns,
    file_format=filename.rsplit(".", 1)[1])

if __name__ == "__main__":
    app.run(debug=True)
