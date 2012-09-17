from flask import Flask, session, redirect, url_for, escape, request, flash
from flask import render_template
from datetime import date
from apscheduler.scheduler import Scheduler

app = Flask(__name__)

def extract_date_name(job):
	return (job.name, job.trigger.run_date)

def extract_dates_names(jobs):
	return [extract_date_name(x) for x in jobs]

@app.route("/", methods=['GET','POST'])
def main_page():
	if request.method == 'POST':
		print request.form['hour']
		print request.form['minute']
		flash('Alarm added')
	else:
		pass

	job_date_times = extract_dates_names(sched.get_jobs())
	return render_template('alarm.html', job_date_times)

if __name__ == "__main__":
	app.secret_key = 'Soeren is the gr3atest OMGWAT'
	app.run(debug=True,host='0.0.0.0')