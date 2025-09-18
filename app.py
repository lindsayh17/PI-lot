from flask import *
import datetime
import time
import mysql.connector
import json
import sys
import pyttsx3

import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
lcd.color = [50,0,50]

engine = pyttsx3.init()

app = Flask(__name__)
app.secret_key = "abc"

credentials = json.load(open("credentials.json", "r"))

@app.route('/message', methods=['GET'])
def message():
    database = mysql.connector.connect(
        host=credentials["host"],
        user=credentials["user"],
        passwd=credentials["password"],
        database=credentials["database"]
    )

    # Returns records from database
    cursor = database.cursor()
    query = "SELECT * FROM message_data WHERE fldSource = 'Raspberry Pi' AND pmkID > 114 ORDER BY pmkID DESC;"

    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    database.close()

    return render_template('message_chart.html', data = data, name = 'Lindsay Hall')

@app.route('/', methods=['GET'])
def default():
    return redirect(url_for('index'))

@app.route('/message_chart.html', methods=['GET'])
def message_chart():
    return redirect(url_for('message'))

@app.route('/sendMessage', methods=['GET', 'POST'])
def sendMessage(): 
    # Database connection     
    database = mysql.connector.connect(
        host=credentials["host"],
        user=credentials["user"],
        passwd=credentials["password"],
        database=credentials["database"]
    )
    cursor = database.cursor()

    valid = ["Y", "Yes", "Ye", "Yeah", "N", "No", "Nope"]
    yes = ["Y", "Yes", "Ye", "Yeah"]
    no = ["N", "No", "Nope"]
        
    if request.method == 'POST':
        lcd.clear()

        # Get message
        message = request.form.get('txtMessage', '')

        #use buttons to scroll
        start = 0
        while True:
            longMessage = message[start:start+16]
            lcd.message = longMessage
            if lcd.left_button:
                start -= 1
            if start < 0:
                start = len(message)-16
            if lcd.right_button:
                start += 1
                if start > len(message) - 16:
                    start = 0
            if lcd.select_button:
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 5)
                engine.say(message)
                engine.runAndWait()
            #reply
            if lcd.down_button:
                lcd.clear()
                break
            
        # Put records into database
        now = datetime.datetime.now()
        timestamp = now.strftime("%m/%d/%Y %H:%M")
        destination = "Raspberry Pi"
        source = "HQ"

        insert_sql = "INSERT INTO `message_data` (`timestamp`, `fldMessage`, `fldSource`, `fldDestination`) VALUES (%s, %s, %s, %s);"
        inserts = (timestamp, message, source, destination)
        cursor.execute(insert_sql, inserts)
        database.commit()

        lcd.message = "Reply to message?\nYes: y   No: n"
        reply = "x"
        msg = " "
        while reply not in valid:
            reply = input("Yes(y) or No(n): ").capitalize()
        if reply in yes:
            send = "N"
            while send in no:
                lcd.blink = True
                lcd.clear()
                lcd.message = "Please type your\nreply: "
                msg = input("Please type your reply: ")
                lcd.blink = False
                lcd.clear()
                while True:
                    longMessage = msg[start:start+16]
                    lcd.message = longMessage
                    if lcd.left_button:
                        start -= 1
                    if start < 0:
                        start = len(msg)-16
                    if lcd.right_button:
                        start += 1
                        if start > len(msg) - 16:
                            start = 0
                    if lcd.select_button:
                        engine.setProperty('rate', 150)
                        engine.setProperty('volume', 5)
                        engine.say(msg)
                        engine.runAndWait()
                    if lcd.down_button:
                        break
                lcd.message = "\nSend?"
                send = input().capitalize()
                while send not in valid:
                    lcd.clear()
                    lcd.message = "Send (Y or N):"
                    send = input().capitalize()
                lcd.clear()
            lcd.message = "Message sent"
            flash("Your message was received. You have a new message.")
            time.sleep(5)
        elif reply in no:
            lcd.clear()
            lcd.message = "Ending Session\nGoodnight!"
            flash("Your message was received!")
            time.sleep(3)
            lcd.clear()
        else: # input validation
            lcd.clear()
            lcd.blink = False
            lcd.message = "Please enter\nYes: y or No: n"
            print("Please enter yes(y) or no(n): ")
        
        lcd.clear()

        # Put records into database
        now = datetime.datetime.now()
        timestamp = now.strftime("%m/%d/%Y %H:%M")
        destination = "HQ"
        source = "Raspberry Pi"

        insert_sql = "INSERT INTO `message_data` (`timestamp`, `fldMessage`, `fldSource`, `fldDestination`) VALUES (%s, %s, %s, %s);"
        inserts = (timestamp, msg, source, destination)
        cursor.execute(insert_sql, inserts)
        database.commit()

        cursor.close()
        database.close()

        return render_template('sendMessage.html')
    else:
        return render_template('sendMessage.html')

@app.route('/sentMessagesChart', methods=['GET'])
def sentMessagesChart():
    database = mysql.connector.connect(
        host=credentials["host"],
        user=credentials["user"],
        passwd=credentials["password"],
        database=credentials["database"]
    )

    # Returns records from database
    cursor = database.cursor()
    query = "SELECT * FROM message_data WHERE fldSource = 'HQ' AND pmkID > 114 ORDER BY pmkID DESC;"

    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    database.close()

    return render_template('sentMessagesChart.html', data = data)

@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')