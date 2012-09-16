from flask import Flask, session, redirect, url_for, escape, request, flash
from flask import render_template

app = Flask(__name__)

@app.route("/", methods=['GET','POST'])
def main_page():
	if request.method == 'POST':
		print request.form['hour']
		print request.form['minute']
		flash('Alarm added')
	else:
		pass

	return render_template('alarm.html')

if __name__ == "__main__":
	app.secret_key = 'Soeren is the gr3atest OMGWAT'
	app.run(debug=True,host='0.0.0.0')