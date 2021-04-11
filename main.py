from tkinter import *

from AppGUI import Application

"""def find_encoding(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encode = face_recognition.face_encodings(img)[0]
    return encode


def find_images_and_names(myList):
    students = []
    for cl in myList:
        currentImage = cv2.imread(f'{path}/{cl}')
        students.append(Student(os.path.splitext(cl)[0], find_encoding(currentImage)))
        print(os.path.splitext(cl)[0])
    return students


def mark_attendance(name):
    with open('attendanceRecord.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')




path = 'imagesDB'
myList = os.listdir(path)
students = find_images_and_names(myList)"""

root = Tk()
root.geometry('300x150')
app = Application(root)
app.mainloop()

"""cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    facesInFrame = face_recognition.face_locations(imgS)
    encodesInFrame = face_recognition.face_encodings(imgS, facesInFrame)

    for encodeFace, faceLoc in zip(encodesInFrame, facesInFrame):
        matches = face_recognition.compare_faces(encodeListKnow, encodeFace)
        faceDistance = face_recognition.face_distance(encodeListKnow, encodeFace)
        matchIndex = np.argmin(faceDistance)
        print(faceDistance)

        if matches[matchIndex]:
            name = names[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            mark_attendance(name)

    cv2.imshow('Webcam', img)
    cv2.waitKey(1)"""
