from flask import Flask, redirect, request, flash
from flask import render_template
from datetime import datetime
from apscheduler.scheduler import Scheduler
from random import randrange
from mpd import MPDClient
from socket import error as SocketError
import os
import logging

logging.basicConfig()
app = Flask(__name__)
app.secret_key = 'Soeren is the gr3atest OMGWAT'

sched = Scheduler()
sched.start()



HOST = 'localhost'
PORT = '6600'
PASSWORD = False

mpd = MPDClient()


def play():
  mpd.connect(host=HOST, port=PORT)
  if PASSWORD:
    mpd.password(PASSWORD)

  mpd.play()

def extract_date_name(job):
  alarm_date = job.trigger.run_date
  return (job.name, alarm_date.strftime("%A %d-%m %H:%M"))

def extract_dates_names(jobs):
  return [extract_date_name(x) for x in jobs]

@app.route("/", methods=['GET','POST'])
def main_page():
  
  #get current mpd state
  try:
    mpd.connect(host=HOST, port=PORT)
    mpdPlaying = (mpd.status()['state'] == 'play')
  except:
    print 'Connection Error'
    mpdPlaying = False

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
  print mpdPlaying
  return render_template('alarm.html', job_date_times=job_date_times, mpd_playing = mpdPlaying)

@app.route("/delete/<jobname>")
def delete(jobname):
  filtered = [job for job in sched.get_jobs() if str(job.name)==str(jobname)]
  for job in sched.get_jobs():
    print job.name
  sched.unschedule_job(filtered[0])
  return redirect('/')

if __name__ == "__main__":
  
  app.run(debug=True,host='0.0.0.0')
