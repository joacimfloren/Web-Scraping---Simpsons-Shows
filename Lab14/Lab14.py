import sqlite3
import urllib.request
import re
import time
import datetime
from datetime import timedelta, date

conn = sqlite3.connect('tvdbo.db')
c = conn.cursor()
data = []
daySpan = 7
thisYear, thisMonth, thisDay = int(time.strftime("%Y")), int(time.strftime("%m")), int(time.strftime("%d"))
start_date = date(thisYear, thisMonth, thisDay)
end_date = start_date + datetime.timedelta(days=daySpan)

def collectDataOfDate(date):
    site = urllib.request.urlopen('http://www.svt.se/tv-tabla/TV6/' + date + '/')
    txt = site.read().decode("utf-8")
    dataForDate = re.findall(r'<td class="svtTablaTime">\s*(\d+\.\d+)\s*<\/td>\s*<td.*?>\s*<h4.*?>\s*(Simpsons)\s*<\/h4>\s*<div.*?>\s*<div.*?>\s*<div.*?>\s*<p .*?>\s*.+S.song\s(\d+).\sDel\s(\d+.*?\s\d+).\s*(.+)', txt)
    for d in dataForDate:
        data.append((d, date))

def createDb():
    c.execute("drop table if exists tvshows")
    c.execute("drop table if exists airtimes")

    c.execute('''CREATE TABLE tvshows (
        Id INTEGER PRIMARY KEY AUTOINCREMENT, 
        Title TEXT NOT NULL, 
        Episode TEXT NOT NULL,
        Season TEXT NOT NULL,
        Description TEXT NOT NULL,
        UNIQUE (Title, Episode, Season) ON CONFLICT IGNORE);''')

    c.execute('''CREATE TABLE airtimes (
        Date TEXT NOT NULL,
        StartTime TEXT NOT NULL,
        Id INTEGER NOT NULL,
        UNIQUE (Date, StartTime) ON CONFLICT FAIL);''')

def insertToDb(d):
    for i in range(len(d)):
        c.execute("INSERT INTO tvshows (Title, Episode, Season, Description) VALUES (?, ?, ?, ?);", (d[i][0][1], d[i][0][3], d[i][0][2], d[i][0][4]))
        answ = c.execute("SELECT Id FROM tvshows WHERE Episode = ? AND Season = ?;", (d[i][0][3], d[i][0][2]))
        for row in answ: id = row[0]
        c.execute("INSERT INTO airtimes VALUES (?, ?, ?);", (d[i][1], d[i][0][0], id))
    conn.commit()

def getAndPrintFromDb():
    answer = c.execute("SELECT tvshows.Title, tvshows.Episode, tvshows.Season, airtimes.Date, airtimes.StartTime FROM tvshows INNER JOIN airtimes ON tvshows.Id = airtimes.Id;")
    for row in answer:
        print("----------------- {} --------------------".format(row[0]))
        print("Avsnitt:          {}".format(row[1]))
        print("Sasong:           {}".format(row[2]))
        print("Datum:            {}".format(row[3]))
        print("Klockslag:        {}".format(row[4]))
        print("\n")
    conn.close()

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)



createDb()
for d in daterange(start_date, end_date): 
    collectDataOfDate(d.strftime('%Y-%m-%d'))
insertToDb(data)
getAndPrintFromDb()