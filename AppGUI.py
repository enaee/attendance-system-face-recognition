import os
from tkinter import *
from tkinter import filedialog as fd
import numpy as np
import cv2
import face_recognition

from Student import Student


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

def faceMatch(img, facesInFrame, encodesInFrame, knownEncodings, names):
    for encodeFace, faceLoc in zip(encodesInFrame, facesInFrame):
        matches = face_recognition.compare_faces(knownEncodings, encodeFace)
        faceDistance = face_recognition.face_distance(knownEncodings, encodeFace)
        matchIndex = np.argmin(faceDistance)
        if matches[matchIndex]:
            name = names[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)


def PrikaziVideo(filename, students):
    knownEncodings = getStudentEncodings(students)
    names = getStudentNames(students)
    cap = cv2.VideoCapture(filename)
    counter = 0
    waitTime = 24
    if (cap.isOpened() == False):
        print("Error opening video stream or file")

    while (cap.isOpened()):
        success, img = cap.read()
        if success == True and counter == 0:
            img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            facesInFrame = face_recognition.face_locations(img)
            encodesInFrame = face_recognition.face_encodings(img, facesInFrame)
            faceMatch(img, facesInFrame, encodesInFrame, knownEncodings, names)
            cv2.imshow(filename, img)
            cv2.waitKey(1)
            counter = counter + 1
        elif counter < waitTime:
            counter = counter+1
        elif counter == waitTime:
            counter = 0
        else:
            break

    cap.release()
    cv2.destroyAllWindows()


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

    def Otvori(self):
        filename = fd.askopenfilename()
        PrikaziVideo(filename, students)

    def ImportDB(self):
        global students
        path = 'imagesDB'
        myList = os.listdir(path)
        students = find_images_and_names(myList, path)



    def CreateWidgets(self):
        self.lab = Label(self, text='Otvori video koji želiš učitati!')
        self.lab.pack()
        self.tipka = Button(self, text='Otvori', command=self.Otvori)
        self.tipka.pack()
        self.ImportDB()

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.CreateWidgets()
        self.winfo_geometry()

