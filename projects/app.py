from flask import Flask, render_template, request
import csv
app = Flask(__name__)
@app.route("/")
def home():
   return render_template("form.html")

@app.route("/submit",methods=["POST"])
def submit():
    num_subjects = request.form["num_subjects"]
    easy_subjects = request.form["easy_subjects"]   
    attendence = request.form["attendence"]
    sem1 = request.form["sem1_percentage"]
    sem2 = request.form["sem2_percentage"]
    sleep_hours = request.form["sleep_hours"]
    phone_usage = request.form["phone_usage"]
    study_hours = request.form["study_hours"]

    num_subjects = int(num_subjects)
    easy_subjects = int(easy_subjects)
    attendence = float(attendence)
    sem1 = float(sem1)
    sem2 = float(sem2)
    sleep_hours = float(sleep_hours)
    phone_usage = float(phone_usage)
    study_hours = float(study_hours)

    if easy_subjects > num_subjects:
        return "error: easy subjects cannot exceed total subjects"
    with open("data/data.csv",mode="a",newline="") as file:
        writer = csv.writer(file)
        writer.writerow([study_hours,phone_usage,sleep_hours,num_subjects,attendence,sem1,sem2])
        print("data saved to csv")
        return "data saved successfully"
    
if __name__ == "__main__":
    app.run(debug = True)


