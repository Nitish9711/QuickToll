import cv2 
import numpy as np 
import scipy.fftpack 
import os
import re
from PIL import Image
import PIL.ImageOps   
import sys 
import pytesseract



pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class extractnumber:
    def __init__(self):
        self.line="dummytext"

    def start(self):
        self.image_manipulation()
        self.text_extraction()
        self.removefiles()

    def imclearborder(self,imgBW, radius):
        # finding contours from the image
        imgBWcopy = imgBW.copy()
        contours,hierarchy = cv2.findContours(imgBWcopy.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        imgRows = imgBW.shape[0]
        imgCols = imgBW.shape[1]    
        contourList = [] 

        for idx in np.arange(len(contours)):
            cnt = contours[idx]

            for pt in cnt:
                rowCnt = pt[0][1]
                colCnt = pt[0][0]

                check1 = (rowCnt >= 0 and rowCnt < radius) or (rowCnt >= imgRows-1-radius and rowCnt < imgRows)
                check2 = (colCnt >= 0 and colCnt < radius) or (colCnt >= imgCols-1-radius and colCnt < imgCols)

                if check1 or check2:
                    contourList.append(idx)
                    break

        for idx in contourList:
            cv2.drawContours(imgBWcopy, contours, idx, (0,0,0), -1)

        return imgBWcopy

    def bwareaopen(self,imgBW, areaPixels):
        imgBWcopy = imgBW.copy()
        contours,hierarchy = cv2.findContours(imgBWcopy.copy(), cv2.RETR_LIST, 
            cv2.CHAIN_APPROX_SIMPLE)

        for idx in np.arange(len(contours)):
            area = cv2.contourArea(contours[idx])
            if (area >= 0 and area <= areaPixels):
                cv2.drawContours(imgBWcopy, contours, idx, (0,0,0), -1)

        return imgBWcopy
    
    def image_manipulation(self):
        filename_base = "plates/plate-detected"

        picname = filename_base + ".jpg"
        img = cv2.imread(picname, 0)
        rows = img.shape[0]
        cols = img.shape[1]
        imgLog = np.log1p(np.array(img, dtype="float") / 255)
        M = 2*rows + 1
        N = 2*cols + 1
        sigma = 10
        (X,Y) = np.meshgrid(np.linspace(0,N-1,N), np.linspace(0,M-1,M))
        centerX = np.ceil(N/2)
        centerY = np.ceil(M/2)
        gaussianNumerator = (X - centerX)**2 + (Y - centerY)**2
        Hlow = np.exp(-gaussianNumerator / (2*sigma*sigma))
        Hhigh = 1 - Hlow
        HlowShift = scipy.fftpack.ifftshift(Hlow.copy())
        HhighShift = scipy.fftpack.ifftshift(Hhigh.copy())
        If = scipy.fftpack.fft2(imgLog.copy(), (M,N))
        cv2.imwrite('gray.png', img)
        Ioutlow = np.real(scipy.fftpack.ifft2(If.copy() * HlowShift, (M,N)))
        Iouthigh = np.real(scipy.fftpack.ifft2(If.copy() * HhighShift, (M,N)))
        gamma1 = 0.3
        gamma2 = 1.5
        Iout = gamma1*Ioutlow[0:rows,0:cols] + gamma2*Iouthigh[0:rows,0:cols]
        Ihmf = np.expm1(Iout)
        Ihmf = (Ihmf - np.min(Ihmf)) / (np.max(Ihmf) - np.min(Ihmf))
        cv2.imwrite('output4.png', Ihmf)
        Ihmf2 = np.array(255*Ihmf, dtype="uint8")
        cv2.imwrite('Contour_mapping.png', Ihmf2)
        Ithresh = Ihmf2 < 65
        Ithresh = 255*Ithresh.astype("uint8")
        cv2.imwrite('black_white.png', Ithresh)
        Iclear = self.imclearborder(Ithresh, 5)
        cv2.imwrite('Increased_black.png', Iclear)
        Iopen = self.bwareaopen(Iclear, 10)

        cv2.imwrite('output.png', Iopen)
        image = Image.open('output.png')
        inverted_image = PIL.ImageOps.invert(image)
        inverted_image.save('output.png')


    def text_extraction(self):
        text = pytesseract.image_to_string('output.png',  config='--psm 11')

        input_file = open('out.txt', 'w')
        input_file.write(text)
        input_file = open('out.txt', 'r')


        while True:
            line = input_file.readline()
            if not line:
                print("can't detect")
                break
            m=re.search("[A-Z][A-Z][0-9][0-9]",line)
            if m:
                self.line = "".join(line.split())
                # print(type(line))
                print(line)
                self.line = line
                
    def get_number(self):
        return self.line
  
    def removefiles(self):
        print("daf")
        # os.remove('output.png')
        # os.remove('Increased_black.png')
        # os.remove('Contour_mapping.png')
        # os.remove('black_white.png')
        # os.remove('output4.png')
        # os.remove('gray.png')

