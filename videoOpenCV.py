import cv2, time

#function to detect and draw features
def detectFeatures(classifier, frame, thisScaleFactor, thisMinNeighbors, color, thickness):
	resizedFrame = cv2.resize(frame, (256,256))
	grayImg = cv2.cvtColor(resizedFrame, cv2.COLOR_BGR2GRAY)

	features = classifier.detectMultiScale(grayImg, scaleFactor=thisScaleFactor, minNeighbors=thisMinNeighbors)

	for x,y,w,h in features:
		resizedFrame = cv2.rectangle(resizedFrame,(x,y),(x+w,y+h),color,thickness)
	return resizedFrame, len(features);

def classify_features():
	#define what eye and nose classifiers you would like to use
	faceClassifier = cv2.CascadeClassifier('data\haarcascade_frontalface_alt.xml')
	eyeClassifier = cv2.CascadeClassifier('data\haarcascade_eye.xml')
	mouthClassifier = cv2.CascadeClassifier('data\haarcascade_smile.xml')
	return faceClassifier, eyeClassifier, mouthClassifier

def check_mask(numOfEyes, numOfMouths):
	wearingMask = None
	if numOfEyes >= 2 and numOfMouths == 0:
		wearingMask = True
	elif numOfEyes >= 2 and numOfMouths >= 1:
		wearingMask = False
	return wearingMask

def detect_faces(frame, scaleDownFactor, faceClassifier):
	smallImg = cv2.resize(frame, (0,0), fx=scaleDownFactor, fy=scaleDownFactor)
	grayImg = cv2.cvtColor(smallImg, cv2.COLOR_BGR2GRAY)
	faceRects = faceClassifier.detectMultiScale(grayImg, scaleFactor=1.05, minNeighbors=1)
	return smallImg, grayImg, faceRects

def mark_face(frame, wearingMask, descaledX, descaledY, descaledW, descaledH):
	frame = cv2.rectangle(frame,(descaledX,descaledY),(descaledX+descaledW,descaledY+descaledH),(255,255,0),3)
	faceLabel = "Wearing Mask: "+str(wearingMask)
	frame = cv2.putText(frame, faceLabel, (descaledX,descaledY-10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.25, (255,255,0))
	return frame

def process_frames(frame, faceRects, scaleDownFactor, mouthClassifier, eyeClassifier):
	for x,y,w,h in faceRects:
		# De-scale xywh
		descaledX = int(x/scaleDownFactor)
		descaledY = int(y/scaleDownFactor)
		descaledW = int(w/scaleDownFactor)
		descaledH = int(h/scaleDownFactor)

		# Get img of only the face in the frame
		faceFrame = frame[descaledY:descaledY+descaledH, descaledX:descaledX+descaledW]

		# Detect features of face
		faceFrame, numOfEyes = detectFeatures(eyeClassifier, faceFrame, 1.05, 100, (255,0,0), -1)
		faceFrame, numOfMouths = detectFeatures(mouthClassifier, faceFrame, 1.05, 200, (0,255,0), 3)
		#frame[descaledY:descaledY+descaledH, descaledX:descaledX+descaledW] = cv2.resize(faceFrame, (descaledW,descaledH))

		# Check if wearing mask
		wearingMask = check_mask(numOfEyes, numOfMouths)
		# Draw face rectangle and label
		frame = mark_face(frame, wearingMask, descaledX, descaledY, descaledW, descaledH)

	return frame
	
def detect_mask_from_video():
	faceClassifier, eyeClassifier, mouthClassifier = classify_features()
	#constants
	video = cv2.VideoCapture(0) 
	scaleDownFactor = 0.2 #change resolution of image for face detection

	while(video.isOpened()):

		check, frame = video.read()

		smallImg, grayImg, faceRects = detect_faces(frame, scaleDownFactor, faceClassifier)
		
		frame = process_frames(frame, faceRects, scaleDownFactor, mouthClassifier, eyeClassifier)
		cv2.imshow("video", frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cv2.destroyAllWindows()
	video.release()

detect_mask_from_video()