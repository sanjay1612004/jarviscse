from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, QTime, QDate, QThread,Qt,QSize
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog, QApplication  ,QLabel, QVBoxLayout, QWidget, QMainWindow, QProgressBar
from jarvissuperUIII import Ui_Dialog 
import speech_recognition as sr
import pyttsx3
import pywhatkit
import wikipedia
import datetime
import time
import os
import openai
import google.generativeai as genai
import pyautogui
from plyer import notification
import requests
from bs4 import BeautifulSoup
import speedtest
from plyer import call
import sys


genai.configure(api_key="AIzaSyBaBkE8xHWPN2T5KmpbZ5kls4n4ibWh0HM")

class MainThread(QThread):
    def __init__(self):
        super(MainThread, self).__init__()
        self.r = sr.Recognizer() 

    def listen(self):
        try:
            with sr.Microphone() as source:
                self.r.adjust_for_ambient_noise(source)
                print("Listening...")
                audio = self.r.listen(source, timeout=60)
                text = self.r.recognize_google(audio).lower()
                print("You said:", text)
                return text
        except Exception as e:
            print("Error:", str(e))
            return ""

    def google_gemini(self, prompt):
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            if 'write' in prompt.lower():
                prompt = prompt + ' ' + 'in short'
                response = model.generate_content(prompt)
            else:
                response = model.generate_content(prompt, generation_config={"max_output_tokens": 50})
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
        
    def speak(self,command):
        engine = pyttsx3.init()
        engine.say(command)
        engine.runAndWait()

    def send_whatsapp(self):
        # same function here
        self.speak("tell the person to who u want to send message")
        d={"mummy":9865120930,"daddy":8248953272,"tamilarasan":9384154339}
        name = self.listen().replace(" ", "")
        phone_number=d.get(name)
        phone_number=f"+91{phone_number}"
        self.speak("What message would you like to send?")
        message = self.listen()

        if not message:
            self.speak("I didn't hear your message. Please try again.")
            return

        self.speak(f"Scheduling message '{message}' to {phone_number} ")
        
        try:
            #pywhatkit.sendwhatmsg(phone_number, message, hour, minute, wait_time=10)
            pywhatkit.sendwhatmsg_instantly(phone_number, message)
            self.speak("Message scheduled successfully.")
        except Exception as e:
            self.speak("There was an error sending the message.")
            print("Error:", e)

    def make_call(self, number):
        call.makecall(tel=number)

    def type_text(self,text):
        pyautogui.write(text,interval=0.05)
        pyautogui.press('enter')

    def get_ipl_score(self):
        import requests
        import json

        #api_key = "1b9cfb09-fc37-4072-9b6d-196be1114b87"  # Replace with your actual API key
        url = "https://api.cricapi.com/v1/currentMatches?apikey=1b9cfb09-fc37-4072-9b6d-196be1114b87&offset=0"

        # Fetch data from API
        response = requests.get(url)
        #print(response)
        datas = response.json()
        #print("datas is",datas)
        # Debug: Print full API response (optional)
        # print(json.dumps(data, indent=2))

        if datas.get("status") != "success":
            print("Error fetching IPL scores.")
        else:
            #matches = datas.get("data", [])
            if "data" in datas:
                matches = datas["data"]
                #print("matches is",matches)
            else:
                print("Key 'data' not found in response")
            ipl_matches = [match for match in matches if match.get("matchType") == "t20"]

            print("ipl mathches is",ipl_matches)
            if not ipl_matches:
                print("No live IPL matches found.")
                self.speak("No live IPL matches found.")
            else:
                match = ipl_matches[0]

                team1, team2 = match["teams"]
                venue = match["venue"]
                status = match["status"]

                print(f"\n🏏 {match['name']}")
                print(f"📍 Venue: {venue}")
                print(f"📢 Status: {status}")

                # Check if scores are available
                if "score" in match and len(match["score"]) >= 2:
                    team1_score = match["score"][0].get("r", "N/A")  # Runs
                    team1_wickets = match["score"][0].get("w", "N/A")  # Wickets
                    team1_overs = match["score"][0].get("o", "N/A")  # Overs

                    team2_score = match["score"][1].get("r", "N/A")
                    team2_wickets = match["score"][1].get("w", "N/A")
                    team2_overs = match["score"][1].get("o", "N/A")
                    notification.notify(
                        title="IPL Score",
                        message=f"{team1}:{team1_score}\n {team2}:{team2_score}",
                        timeout=10
                    )
                    print(f"{team1}: {team1_score}/{team1_wickets} ({team1_overs} overs)")
                    self.speak(f"{team1} score is {team1_score} and wicket taken is{team1_wickets} and completed ({team1_overs} overs)")
                    print(f"{team2}: {team2_score}/{team2_wickets} ({team2_overs} overs)")
                    self.speak(f"{team2} score is{team2_score} and wicket taken is {team2_wickets} and completed ({team2_overs} overs)")
                    
                else:
                    print("🔴 Score not available yet.")
                    self.speak("Score not available yet.")

        
    # other functions go here
    
    def run(self):
        self.commands()
    
    def commands(self):
        # your loop for recognizing commands
        self.speak("Welcome to Jarvis. Say 'Jarvis' to activate sir.")
        try:
            while True:
                self.text = self.listen()

                if 'jarvis' in self.text:
                    self.speak("What help do you need?")
                    
                    while True:
                        self.my_text = self.listen()
                        
                        if not self.my_text:  # Skip if empty
                            continue

                        if "stop" in self.my_text or "exit" in self.my_text or "quit" in self.my_text:
                            self.speak("Okay, exiting the program. Goodbye sir!")
                            exit()

                        elif 'play' in self.my_text:
                            song = self.my_text.replace('play', '').strip()
                            self.speak(f'Playing {song}')
                            pywhatkit.playonyt(song)

                        elif 'date' in self.my_text:
                            today = datetime.date.today().strftime("%Y-%m-%d")
                            self.speak(f"Today's date is {today}")

                        elif 'time' in self.my_text:
                            timenow = datetime.datetime.now().strftime('%H:%M')
                            self.speak(f"The time is {timenow}")

                        elif 'who is' in self.my_text:
                            try:
                                person = self.my_text.replace('who is', '').strip()
                                info = wikipedia.summary(person, sentences=1)
                                self.speak(info)
                            except wikipedia.exceptions.DisambiguationError:
                                self.speak(f"Multiple results found for {person}. Please be more specific.")
                            except wikipedia.exceptions.PageError:
                                self.speak(f"Sorry, I couldn't find any information on {person}.")
                            except Exception:
                                self.speak("An error occurred while searching Wikipedia.")

                        elif "virtual game" in self.my_text:
                            from virtualgame import virtual
                            self.speak("Virtual game started")
                            virtual()

                        elif "virtual mouse" in self.my_text:
                            from virtual_mouse import main
                            self.speak("Virtual mouse started")
                            main()

                        elif 'whatsapp' in self.my_text:
                            self.send_whatsapp()
                        elif 'open' in self.my_text:
                            import os
                            apps = {
                                    "chrome": "start chrome",
                                    "notepad": "notepad",
                                    "calculator": "calc",
                                    "command prompt": "cmd",
                                    "word": "start winword",
                                    "excel": "start excel",
                                    "powerpoint": "start powerpnt",
                                }
                            app = self.my_text.replace('open', '').strip().lower()
                            self.speak('opening app'+app)
                            os.system(apps[app])
                            if app=="notepad" or "word":
                                self.speak("what you want to write")
                                new_text=self.listen()
                                pro=self.google_gemini(new_text)
                                self.type_text(pro)
                        elif 'what' in self.my_text:
                            self.my_text=self.my_text.replace('google','')
                            pywhatkit.search(self.my_text)  # Opens Google search
                            self.speak(f"Here is what I found for {self.my_text} on the web.")
                            
                        elif "screenshot" in self.my_text:
                            import time
                            self.speak("taking screen shot sir")
                            screenshot = pyautogui.screenshot()
                            filename = f"C:\\Users\\sanja\\OneDrive\\Pictures\\Screenshots\\screenshot_{int(time.time())}.png"
                            screenshot.save(filename)
                        elif "ipl" in self.my_text:
                            print(f"Recognized text: {self.my_text}")
                            self.speak("fetching sir")
                            self.get_ipl_score()
                        elif 'click my photo' in self.my_text:
                            import time 
                            pyautogui.press("win")  
                            time.sleep(1)  
                            pyautogui.typewrite("Camera") 
                            time.sleep(1)
                            pyautogui.press("enter") 
                            time.sleep(3)  
                            self.speak("smile please")
                            pyautogui.press("enter")  
                            time.sleep(1)
                            pyautogui.click(x=700, y=500)  
                            self.speak("photo taken sir")

                        elif "gemini" in self.my_text:
                            self.speak("Say what you want")
                            message = self.listen()

                            if message:
                                response = self.google_gemini(message)
                                self.speak(response)
                            else:
                                self.speak("I didn't hear anything.")
                        elif 'internet speed' in self.my_text:
                            import time
                            wifi = speedtest.Speedtest()
                            wifi.get_best_server()  # Selects the best nearby server
                            self.speak("please wait sir")
                            self.speak("Testing Download Speed...")
                            print("Testing Download Speed...")
                            download_net = wifi.download() / 1048576  # Convert to Mbps
                            time.sleep(1)
                            self.speak("Testing Upload Speed...")
                            print("Testing Upload Speed...")
                            upload_net = wifi.upload() / 1048576  # Convert to Mbps
                            print(f"Upload Speed: {upload_net:.2f} Mbps")
                            self.speak(f"your Upload Speed is: {upload_net:.2f} Mbps")
                            print(f"Download Speed: {download_net:.2f} Mbps")
                            self.speak(f"your Download Speed is: {download_net:.2f} Mbps")
                        elif "game" in self.my_text:
                            import random
                            self.speak("lets play rock paper scissors")
                            i=0
                            me=0
                            comp=0
                            self.speak("lets start the game")
                            while(i<5):
                                i+=1
                                choose=["rock","paper","scissor"]
                                comp_choose=random.choice(choose)
                                my_choose=self.listen().lower()
                                if (my_choose=="rock"):
                                    if (comp_choose=="rock"):
                                        self.speak("Rock")
                                        print(f"score myscore:{me} compscore:{comp}")
                                        self.speak(f"your score is {me}")
                                        self.speak(f"my score is {comp}")
                                    elif (comp_choose=="paper"):
                                        self.speak("paper")
                                        comp+=1
                                        print(f"score myscore:{me} compscore:{comp}")
                                        self.speak(f"your score is {me}")
                                        self.speak(f"my score is {comp}")
                                    elif (comp_choose=="scissor"):
                                        self.speak("scissor")
                                        me+=1
                                        print(f"score myscore:{me} compscore:{comp}")
                                        self.speak(f"your score is {me}")
                                        self.speak(f"my score is {comp}")
                                elif (my_choose=="paper"):
                                    if (comp_choose=="rock"):
                                        self.speak("Rock")
                                        me+=1
                                        print(f"score myscore:{me} compscore:{comp}")
                                        self.speak(f"your score is {me}")
                                        self.speak(f"my score is {comp}")
                                    elif (comp_choose=="paper"):
                                        self.speak("paper")
                                        print(f"score myscore:{me} compscore:{comp}")
                                        self.speak(f"your score is {me}")
                                        self.speak(f"my score is {comp}")
                                    elif (comp_choose=="scissor"):
                                        self.speak("scissor")
                                        comp+=1
                                        print(f"score myscore:{me} compscore:{comp}")
                                        self.speak(f"your score is {me}")
                                        self.speak(f"my score is {comp}")
                                elif (my_choose=="scissor"):
                                    if (comp_choose=="rock"):
                                        self.speak("Rock")
                                        comp+=1
                                        print(f"score myscore:{me} compscore:{comp}")
                                        self.speak(f"your score is {me}")
                                        self.speak(f"my score is {comp}")
                                    elif (comp_choose=="paper"):
                                        self.speak("paper")
                                        me+=1
                                        print(f"score myscore:{me} compscore:{comp}")
                                        self.speak(f"your score is {me}")
                                        self.speak(f"my score is {comp}")
                                    elif (comp_choose=="scissor"):
                                        self.speak("scissor")
                                        print(f"score myscore:{me} compscore:{comp}")
                                        self.speak(f"your score is {me}")
                                        self.speak(f"my score is {comp}")
                            if comp>me:
                                self.speak("i am the winner")
                            elif comp==me:
                                self.speak("match is draw")
                            else:
                                self.speak("you are the winner")
                    
                        # elif "news" or "info" in self.my_text:
                        #     import json
                        #     import requests
                        #     get_news()
                        elif "phone call" in self.my_text:
                            no="9865120930"
                            make_call(no)
                        elif "close" in self.my_text:
                            import os
                            self.speak("Closing the app")

                            # Remove "close" and clean the app name
                            app = self.my_text.replace("close", "").strip()

                            # Add .exe if not present
                            if not app.endswith(".exe"):
                                app += ".exe"

                            # Correct taskkill command syntax
                            cmd = f"taskkill /f /im {app}"
                            result = os.system(cmd)

                            if result == 0:
                                self.speak(f"{app.replace('.exe','').capitalize()} has been closed.")
                            else:
                                self.speak("App not found or already closed.")
                        elif "detect" in self.my_text:
                            from face import face_rec
                            self.speak("face detection started")
                            face_rec()



                        elif "shutdown" in self.my_text:
                            import os
                            import time

                            delay = 30  # Delay in seconds before shutdown
                            print(f"System will shut down in {delay} seconds...")
                            time.sleep(delay)
                            os.system(f"shutdown /s /t 0")





                                
                            

        except KeyboardInterrupt:
            self.speak("Goodbye!")
        except Exception as e:
            print("Error:", str(e))




class InitWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Launching Jarvis...")
        self.setStyleSheet("background-color: black;") 
        self.setGeometry(500, 300, 700, 700)

        layout = QVBoxLayout()

        # Loading animation (GIF)
        self.gif_label = QLabel(self)
        self.gif_label.setFixedSize(600, 600)
        self.movie = QMovie("C:\\Users\\sanja\\OneDrive\\Desktop\\NewProjects\\assests\\Mr3W.gif")  
        self.movie.setScaledSize(QSize(600, 600)) 
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        self.gif_label.setAlignment(Qt.AlignCenter)

        # Info text
        self.label = QLabel("Initializing Jarvis Assistant...", self)
        self.label.setAlignment(Qt.AlignCenter)

        # Progress bar
        window_width = self.width()
        progress_width = 700 
        # x = (window_width - progress_width) // 2
        self.progress = QProgressBar(self)
        self.progress.setFixedWidth(700)
        #self.progress.setGeometry(50, 700, 700, 25) 
        self.progress.setRange(0, 100)
        self.progress.setValue(0)


        h_layout = QHBoxLayout()
        h_layout.addStretch(2)  # Add a stretch to push the progress bar to the right
        h_layout.addWidget(self.progress)
        # Add widgets to layout
        layout.addWidget(self.gif_label)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10) 
        self.setLayout(layout)

        # Timer to simulate progress
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        self.timer.start(50)  # update every 50ms

    def update_progress(self):
        if self.progress_value >= 100:
            self.timer.stop()
            self.movie.stop()
            self.launch_main_app()
        else:
            self.progress_value += 1
            self.progress.setValue(self.progress_value)

    def launch_main_app(self):
        self.close()
        self.main_window = Main()
        self.main_window.show()






class Main(QMainWindow):
   
    def __init__(self):
        super().__init__()
        self.r = sr.Recognizer()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Create a visible button on top of the transparent one
        self.visible_start_button = QPushButton("", self)
        self.visible_start_button.setGeometry(455, 470, 151, 71)
        self.visible_start_button.setStyleSheet("background-color: transparent; color: white; font-weight: bold;")
        self.visible_start_button.raise_()
        self.visible_start_button.clicked.connect(self.startTask)
        #self.visible_start_button.clicked.connect(self.startTask)
        
        self.visible_quit_button = QPushButton("", self)
        self.visible_quit_button.setGeometry(605, 470, 161, 71)  # Adjust position as needed
        self.visible_quit_button.setStyleSheet("""
            background-color: transparent;
            color: white;
            font-weight: bold;
            
        """)
        self.visible_quit_button.raise_()
        self.visible_quit_button.clicked.connect(self.close)

        # Connect the original quitbutton (if it's needed)
        self.ui.quitbutton.clicked.connect(self.close)

        self.thread = MainThread()


    def startTask(self):
        print("Start button clicked!")
    
        #self.ui.datelabel.setText("Started!")
        self.ui.movie = QtGui.QMovie("C:\\Users\\sanja\\OneDrive\\Desktop\\NewProjects\\assests\\Mr3W.gif")
        self.ui.jarvisgui.setMovie(self.ui.movie)
        self.ui.movie.start()

        self.ui.movie = QtGui.QMovie("C:\\Users\\sanja\\OneDrive\\Desktop\\NewProjects\\assests\\PcOY.gif")
        self.ui.earth.setMovie(self.ui.movie)
        self.ui.movie.start()

        self.ui.movie = QtGui.QMovie("C:\\Users\\sanja\\OneDrive\\Desktop\\NewProjects\\assests\\QNBH.gif")
        self.ui.ironman.setMovie(self.ui.movie)
        self.ui.movie.start()


        timer=QTimer(self)
        timer.timeout.connect(self.showtime)
        timer.start(1000)
        self.thread.start()

    def showtime(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        labletime = current_time.toString("hh:mm:ss")
        labledate = current_date.toString(Qt.ISODate)
        font = QFont("Arial", 11, QFont.Bold)

        self.ui.timelabel.setFont(font)
        self.ui.datelabel.setFont(font)
        self.ui.timelabel.setText(f"Time:{labletime}")
        self.ui.datelabel.setText(f"Date:{labledate}")



   
    
# Main execution logic
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # window = Main()
    # window.show()
    # sys.exit(app.exec_())
    init_screen = InitWindow()
    init_screen.show()

    sys.exit(app.exec_())

