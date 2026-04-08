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

    if not (0 <= study_hours <= 12):
        return "study hours must be between 0-12"

    if not (0 <= phone_usage <= 12):
        return "phone usage must be between 0-12"

    if not (0 <= attendence <= 100):
        return "attendence must be between 0-100"

    if not (0 <= sem1 <= 100):
        return "sem1 must be between 0-100"

    if not (0 <= sem2 <= 100):
        return "sem2 must be between 0-100"

    if not (3 <= sleep_hours <= 12):
        return "sleep hour must be between 3-12"
        
    with open("data/data.csv",mode="a",newline="") as file:
        writer = csv.writer(file)
        writer.writerow([study_hours,phone_usage,sleep_hours,num_subjects,easy_subjects,attendence,sem1,sem2])
        print("data saved to csv")
        return "data saved successfully"
    
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug = True)


