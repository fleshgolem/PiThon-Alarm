from flask import Flask, redirect, request, flash
from flask import render_template
from datetime import datetime, timedelta
from apscheduler.scheduler import Scheduler
from random import randrange
from mpd import MPDClient
import os
import logging
from sqlalchemy import create_engine, Table, Column, Integer, MetaData, DateTime, select

#logging.basicConfig()
app = Flask(__name__)
app.secret_key = 'Soeren is the gr3atest OMGWAT'

sched = Scheduler()
sched.start()

engine = create_engine('sqlite:///alarm.db', echo=True)
metadata = MetaData()
alarms = Table('alarms', metadata, Column('id', Integer, primary_key=True), Column('date', DateTime))

HOST = 'localhost'
PORT = '6600'
PASSWORD = False

mpd = MPDClient()



  

def delete_job_from_db_by_name(name, conn):
  conn.execute(alarms.delete().where(alarms.c.id == name))

def delete_job_from_db_by_name_noconn(name):
  conn=engine.connect()
  delete_job_from_db_by_name(name, conn)
  conn.close()

def readDB():
  conn = engine.connect()
  s = select([alarms])
  results = conn.execute(s)
  for row in results:
    try:
      add_job(row['id'], row['date'])
    except:
      delete_job_from_db_by_name(row['id'], conn)
  conn.close()

def play(name):
  try:
    mpd.connect(host=HOST, port=PORT)
    if PASSWORD:
      mpd.password(PASSWORD)

    mpd.play()
    mpd.disconnect()
  except Exception as e:
    print e
  finally:
    delete_job_from_db_by_name_noconn(name)

def add_job(name, date): 
  sched.add_date_job(play, date, [name], name = name)


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
    mpd.disconnect()
  except:
    print 'Connection error'
    mpdPlaying = False

  if request.method == 'POST':
    print request.form['hour']
    print request.form['minute']
    jobdate = datetime(int(request.form['year']), int(request.form['month']), int(request.form['day']), int(request.form['hour']), int(request.form['minute']))
    print jobdate
    try:
      jobID = randrange(1, 1000000000)
      add_job(jobID, jobdate)
      
      flash((False,'Alarm added'))
      conn = engine.connect()
      ins = alarms.insert()
      conn.execute(ins, id = jobID, date = jobdate)
      conn.close()
    except Exception as e:
      print e
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
  conn = engine.connect()
  delete_job_from_db_by_name(job.name, conn)
  conn.close()
  return redirect('/')

@app.route("/snooze")
def snooze():
  try:
    mpd.connect(host=HOST, port=PORT)
    mpd.pause()
    mpd.disconnect()
    jobtime = datetime.now() + timedelta(minutes=10)
    add_job(randrange(1, 1000000000), jobtime)
    flash((False,'SNOOOOOZE'))
  except:
    flash((True,'Something went wrong'))

  return redirect('/')

@app.route("/stop")
def stop():
  try:
    mpd.connect(host=HOST, port=PORT)
    mpd.stop()
    mpd.disconnect()
  except:
    pass
  return redirect('/')

readDB()

if __name__ == "__main__":
  
  app.run(debug=True,host='0.0.0.0')
  
