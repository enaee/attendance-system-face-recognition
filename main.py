import os
import csv
import tkinter as tk
from tkinter import filedialog as fd
import numpy as np
import cv2
import face_recognition
from datetime import datetime
import pickle
from tkinter import *
from Student import Student


class Application(Frame):

    def __init__(self, master):
        # Creating instances for all GUI components
        Frame.__init__(self, master)
        self.frame = Frame(master)
        self.frame_choose_video_source = LabelFrame(self, text='Choose Video source')
        self.student_frame = LabelFrame(self, text='Students')
        self.lab = Label(self.frame_choose_video_source, text='Open video you want to check!')
        self.labFileName = Label(self.frame_choose_video_source, text='No file is opened yet!')
        self.button_import = Button(self, text='Import student names', command=self.importDB) # calls importDB() method
        self.btnLoadVideo = Button(self.frame_choose_video_source, text='Otvori', command=self.open_video_file)  # calls open_video_file() method
        self.btnDeleteAll = Button(self.student_frame, text="delete", command=self.delete_students_from_DB)
        self.labelStudentName = Label(self.student_frame)
        self.labelCountAttended = Label(self.student_frame)
        self.students = []
        self.grid()
        self.create_widgets()
        self.winfo_geometry()

    def create_widgets(self):
        # Defining locations of GUI elements
        self.button_import.pack()
        self.frame_choose_video_source.pack()
        self.lab.grid(column=0, row=0)
        self.btnLoadVideo.grid(column=0, row=1)
        self.labFileName.grid(column=0, row=2)

    def update_results(self):
        # destroys student frame because I cant delete specific student,
        # this way it deletes and creates new list every time its updated
        self.student_frame.destroy()
        students = self.students
        if len(students) != 0:
            self.student_frame = LabelFrame(self, text='results')
            self.btnDeleteAll = Button(self.student_frame, text="delete", command=self.delete_students_from_DB)
            self.student_frame.pack()
            self.btnDeleteAll.grid(column=0, row=100)
            # making table with names and results
            for student in students:
                # colors background gray for every second student
                if students.index(student) % 2 == 0:
                    self.labelStudentName = Label(self.student_frame, text=student.name.upper(), bg='#cccccc')
                    self.labelStudentName.grid(row=students.index(student) + 50, column=0, sticky="ew")
                    self.labelCountAttended = Label(self.student_frame, text=student.noTimesAttended, bg='#cccccc')
                    self.labelCountAttended.grid(row=students.index(student) + 50, column=1, sticky="ew")
                # colors bg white
                else:
                    self.labelStudentName = Label(self.student_frame, text=student.name.upper())
                    self.labelStudentName.grid(row=students.index(student) + 50, column=0, sticky="ew")
                    self.labelCountAttended = Label(self.student_frame, text=student.noTimesAttended)
                    self.labelCountAttended.grid(row=students.index(student) + 50, column=1, sticky="ew")

    # deletes student frame and students from DB
    def delete_students_from_DB(self):
        self.students = []
        self.update_results()

    # creates student database from images
    def importDB(self):
        path = 'imagesDB'
        myList = os.listdir(path)
        self.find_encodings_and_names(myList, path)
        self.button_import['state'] = DISABLED
        self.update_results()

    # gets student names and encodings from images
    def find_encodings_and_names(self, myList, path):
        for cl in myList:
            currentImage = cv2.imread(f'{path}/{cl}')
            self.students.append(Student(os.path.splitext(cl)[0].upper(), find_encoding(currentImage)))
            print(os.path.splitext(cl)[0])

    # opens file dialog to get video and calls show_video() method
    def open_video_file(self):
        filePath = fd.askopenfilename()
        self.labFileName.config(text=os.path.basename(filePath))
        self.show_video(filePath, self.students)

    def show_video(self, filePath, students):
        #gets name of the file from file path and creates .csv file with that name
        file_name = os.path.basename(filePath)
        file_name = file_name.split('.')
        file_name = file_name[0]
        cvs_file_name = "video_results/" + file_name + ".csv"
        f = open(cvs_file_name, 'w')

        knownEncodings = getStudentEncodings(students)
        cap = cv2.VideoCapture(filePath)
        general_info = (students, knownEncodings, cvs_file_name)
        if not cap.isOpened():
            print("Error opening video stream or file")
        # skips every 7 frames (aprox. 1/4 second for 30fps video)
        counter = 0
        waitTime = 7
        while cap.isOpened():
            success, img = cap.read()
            if success and counter == 0:
                img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                # for some reason it wont work with the line below
                # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                facesInFrame = face_recognition.face_locations(img)
                encodesInFrame = face_recognition.face_encodings(img, facesInFrame)
                frame_info = (img, facesInFrame, encodesInFrame)
                # calls method to check if faces in frame match faces in DB
                self.faceMatch(frame_info, general_info)
                cv2.imshow(filePath, img)
                cv2.waitKey(1)
                counter = counter + 1
            elif success and counter < waitTime:
                counter = counter + 1
            elif success and counter == waitTime:
                counter = 0
            else:
                break
        cap.release()
        cv2.destroyAllWindows()
        self.update_students(cvs_file_name)
        self.update_results()

    def faceMatch(self, frame_info, general_info):
        # forwarding information
        facesInFrame = frame_info[1]
        encodesInFrame = frame_info[2]
        img = frame_info[0]
        knownEncodings = general_info[1]
        students = general_info[0]
        names = getStudentNames(students)
        fileName = general_info[2]

        # code from tutorial to check if face matches and draws rectangle around face
        for encodeFace, faceLoc in zip(encodesInFrame, facesInFrame):
            matches = face_recognition.compare_faces(knownEncodings, encodeFace)
            faceDistance = face_recognition.face_distance(knownEncodings, encodeFace)
            matchIndex = np.argmin(faceDistance)
            if matches[matchIndex]:
                name = names[matchIndex]
                self.markAttendance(name, faceLoc, fileName)
                drawRectangle(img, name, faceLoc)
            else:
                name = "Unknown"
                self.markAttendance(name, faceLoc, fileName)
                drawRectangle(img, name, faceLoc)

    # saves name of every person in video
    def markAttendance(self, name, faceLoc, fileName):
        with open(fileName, 'a') as f:
            f.writelines(f'{name},{faceLoc}\n')

    # if person is in video, add +1 to attendance
    def update_students(self, fileName):
        f = open(fileName, 'r')
        myDataList = f.readlines()
        names = getStudentNames(self.students)
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            name = entry[0]
            if name not in nameList:
                nameList.append(entry[0])
        print(nameList)
        for name in nameList:
            if name in names:
                index = names.index(name)
                student = self.students[index]
                student.noTimesAttended += 1
                self.students[index] = student
            else:
                student = Student("UNKNOWN", [])
                student.noTimesAttended = 1
                self.students.append(student)


    def how_many_apper_in_video(self, nameList, studName):
        curentstudent = []
        curentstudent[0] = studName
        if curentstudent[0] == name:
            curentstudent[1] += 1
        if curentstudent[1] == 3:
            if name not in nameList:
                nameList.append(entry[0])
                curentstudent[0]
        return True



def getStudentEncodings(students):
    encodings = []
    for student in students:
        encodings.append(student.encoding)
    return encodings

def getStudentNames(students):
    names = []
    for student in students:
        names.append(student.name.upper())
    return names

def find_encoding(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encode = face_recognition.face_encodings(img)[0]
    return encode

def drawRectangle(img, name, faceLoc):
    y1, x2, y2, x1 = faceLoc
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# starts application
root = Tk()
app = Application(root)
app.mainloop()
