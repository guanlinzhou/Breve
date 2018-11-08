import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import csv
import datetime
import gcal_uplink as gcal
import NLU_email_parser as nlu

mailpath = 'parseddata/bmail.csv'
weatherpath = 'parseddata/weather.csv'
todopath = 'parseddata/todo.csv'
credpath = 'fbadmin.json'

cred = credentials.Certificate(credpath)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://calhacks-bb99b.firebaseio.com/'
})
root = db.reference()
emails = root.child('emails')
weather = root.child('weather')
todo = root.child('todo')


def addToDo(ind, name, time):
    event = {
    'time' : time,
    'name' : name
    }
    key = todo.child(str(ind))
    key.set(event)
    return key

def eventToDict(name, time, location):
    return {'name' : name,
            'time' : time,
            'location' : location
            }

def pushToDo():
    array = []
    data = parseRowsCSV(todopath)[3][0] #today
    data = data.split('\nCALENDAR EVENT\n')[1:]
    i = 0
    for event in data:
        info = event.split('\n')[1:4]
        array.append([i] + info)
        i += 1

    for event in array:
        # print(event)
        addToDo(*event[:3])
        time = event[2]
        # print(time)
        ind = findIndex(time, ':')
        event[2] = datetime.datetime(2018, 11, 4, int(time[:ind]), int(time[ind+1:ind+3]))
        # print(event[2])
        gcal.pushToCal(eventToDict(*event[1:]))

def parseRowsCSV(csvpath):
    csv_file = open(csvpath)
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    return list(csv_reader)

def message(temp, precipitation):
    precipitation = int(precipitation[:-1])
    temp = int(temp)
    if precipitation > 60:
        return "Rainy weather ahead! Bring an umbrella, just in case."
    elif 0 < temp < 50:
        return "Brr! It's freezing outside. Dress warmly."
    elif 50 <= temp < 65:
        return "Seems like it's a bit chilly today. Don't forget to bring a jacket."
    elif 65 <= temp < 80:
        return "Perfect weather today! Go take a walk outside."
    return "Time to hit the beach! It's scorching today."

def pushWeather():
    data = parseRowsCSV(weatherpath)[1]
    icon = 'cloudy'
    temp = data[3]
    temp = temp[:2]+temp[3:3]
    precip = data[4]
    msg = message(temp, precip)
    weather.set({
        'forecast' : data[2],
        'temp' : temp + '°',
        'precip' : precip,
        'wind' : data[5],
        'icon' : icon,
        'message' : msg,
        'city' : 'Berkeley'
    })

def findIndex(str, char):
    for i in range(len(str)):
        if str[i] == char:
            return i
    return -1

def pushMail():
    data = parseRowsCSV(mailpath)
    num_mails = -1
    toProcess = []
    for row in data:
        if num_mails == -1:
            pass
        else:
            ind = findIndex(row[5], '-')
            subj = row[5][:ind-2]
            body = row[5][ind+3:]
            sender = row[4]
            time = row[8]
            toProcess.append(addEmail(num_mails, subj, sender, body, time))
        num_mails += 1
    nlu.run(toProcess)

"""Adds email events to GCal and app."""
def addEmail(ind, subj, sender, body, time):
    email = {
    'time' : time,
    'subj' : subj,
    'sender' : sender,
    'body' : body
    }
    key = emails.child(str(ind))
    key.set(email)
    return email

def clearDB():
    root.delete()

def push():
    clearDB()

    print("Parsing email...")
    pushMail()
    print("Success! Events uploaded to GCal")

    print("Parsing calendar...")
    pushToDo()
    print("Success!\n")

    print("Parsing weather...")
    pushWeather()
    print("Success!\n")
    print("Execution complete")
