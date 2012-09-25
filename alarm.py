from flask import Flask, redirect, request, flash
from flask import render_template
from datetime import datetime
from apscheduler.scheduler import Scheduler
from random import randrange
from mpd import MPDClient
from socket import error as SocketError
import ConfigParser
import os

app = Flask(__name__)
app.secret_key = 'Soeren is the gr3atest OMGWAT'

sched = Scheduler()
sched.start()

config = ConfigParser.RawConfigParser()
config.read(os.getcwd() + 'mpd.cfg')
try:
  HOST = config.get("mpd","host")
  PORT = config.get("mpd","port")
  PASSWORD = config.get("mpd","password")
except:
  print os.getcwd()

mpd = MPDClient()


def play():
  try:
    if PASSWORD:
      mpd.connect(host=HOST, port=PORT, PASSWORD=PASSWORD)
    else:
      mpd.connect(host=HOST, port=PORT) 
    mpd.play()
  except SocketError:
    print "Connection Error"

def extract_date_name(job):
  return (job.name, str(job.trigger.run_date))

def extract_dates_names(jobs):
  return [extract_date_name(x) for x in jobs]

@app.route("/", methods=['GET','POST'])
def main_page():
  print ("a")
  if request.method == 'POST':
    print request.form['hour']
    print request.form['minute']
    jobdate = datetime(int(request.form['year']), int(request.form['month']), int(request.form['day']), int(request.form['hour']), int(request.form['minute']))
    print jobdate
    try:
      sched.add_date_job(play, jobdate, name = randrange(1, 1000000000))
      flash((False,'Alarm added'))
    except:
      flash((True, 'Job not added, would never run'))
  
  job_date_times = extract_dates_names(sched.get_jobs())
  return render_template('alarm.html', job_date_times=job_date_times)

@app.route("/delete/<jobname>")
def delete(jobname):
  filtered = [job for job in sched.get_jobs() if str(job.name)==str(jobname)]
  for job in sched.get_jobs():
    print job.name
  sched.unschedule_job(filtered[0])
  return redirect('/')

if __name__ == "__main__":
  
  app.run(debug=True,host='0.0.0.0')
