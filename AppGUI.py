import os
from tkinter import *
from tkinter import filedialog as fd
import numpy as np
import cv2
import face_recognition
from datetime import datetime

from Student import Student


def markAttendance(name):
    with open('attendanceRecord.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            f.writelines(f'\n{name}')


def find_encoding(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encode = face_recognition.face_encodings(img)[0]
    return encode


def find_images_and_names(myList, path):
    students = []
    for cl in myList:
        currentImage = cv2.imread(f'{path}/{cl}')
        students.append(Student(os.path.splitext(cl)[0], find_encoding(currentImage)))
        print(os.path.splitext(cl)[0])
    return students


def drawRectangle(img, name, faceLoc):
    y1, x2, y2, x1 = faceLoc
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)


def faceMatch(img, facesInFrame, encodesInFrame, knownEncodings, names, fileName):
    for encodeFace, faceLoc in zip(encodesInFrame, facesInFrame):
        matches = face_recognition.compare_faces(knownEncodings, encodeFace)
        faceDistance = face_recognition.face_distance(knownEncodings, encodeFace)
        matchIndex = np.argmin(faceDistance)
        if matches[matchIndex]:
            name = names[matchIndex].upper()
            markAttendance(name)
            drawRectangle(img, name, faceLoc)
        else:
            name = "Unknown"
            markAttendance(name)
            drawRectangle(img, name, faceLoc)


def PrikaziVideo(filePath, students):
    knownEncodings = getStudentEncodings(students)
    names = getStudentNames(students)
    cap = cv2.VideoCapture(filePath)
    counter = 0
    waitTime = 15
    k = cv2.waitKey(1) & 0xFF
    if (cap.isOpened() == False):
        print("Error opening video stream or file")

    while cap.isOpened():
        success, img = cap.read()
        if success == True and counter == 0:
            img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            facesInFrame = face_recognition.face_locations(img)
            encodesInFrame = face_recognition.face_encodings(img, facesInFrame)
            faceMatch(img, facesInFrame, encodesInFrame, knownEncodings, names, filePath)
            #cv2.imshow(filePath, img)
            #cv2.waitKey(1)
            counter = counter + 1
        elif counter < waitTime:
            counter = counter + 1
        elif counter == waitTime:
            counter = 0
        elif k == 27:
            #cv2.destroyAllWindows()
            break
        else:
            #cv2.destroyAllWindows()
            break
    cap.release()
    #cv2.destroyAllWindows()



def ObradiVideo(filename, students):
    knownEncodings = getStudentEncodings(students)
    names = getStudentNames(students)
    cap = cv2.VideoCapture(filename)
    while True:
        success, img = cap.read()
        if success == True:
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2GRAY)
            facesInFrame = face_recognition.face_locations(imgS)
            encodesInFrame = face_recognition.face_encodings(imgS, facesInFrame)
            faceMatch(imgS, facesInFrame, encodesInFrame, knownEncodings, names, filename)
            cv2.imshow(filename, imgS)
            cv2.waitKey(1)
        else:
            break
    cap.release()


def getStudentEncodings(students):
    encodings = []
    for student in students:
        encodings.append(student.encoding)
    return encodings


def getStudentNames(students):
    names = []
    for student in students:
        names.append(student.name)
    return names


class Application(Frame):
    students = []

    def Otvori(self):
        global students
        filePath = fd.askopenfilename()
        PrikaziVideo(filePath, students)

    def ImportDB(self):
        path = 'imagesDB'
        myList = os.listdir(path)
        global students
        students = find_images_and_names(myList, path)

    def CreateWidgets(self):
        global students
        self.lab = Label(self, text='Otvori video koji želiš učitati!').grid(column=0)
        self.tipka = Button(self, text='Otvori', command=self.Otvori).grid(column=0, rowspan=2)

        for student in students:
            if students.index(student) % 2 == 0:
                self.labelname = Label(self, text=student.name.upper(), bg='#cccccc').grid(
                    row=students.index(student) + 5, column=0, sticky="ew")
                self.labelcount = Label(self, text=student.noTimesAttended, bg='#cccccc').grid(
                    row=students.index(student) + 5, column=1, sticky="ew")
            else:
                self.labelname = Label(self, text=student.name.upper()).grid(row=students.index(student) + 5, column=0,
                                                                             sticky="ew")
                self.labelcount = Label(self, text=student.noTimesAttended).grid(row=students.index(student) + 5,
                                                                                 column=1, sticky="ew")

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.ImportDB()
        self.pack()
        self.CreateWidgets()
        self.winfo_geometry()
