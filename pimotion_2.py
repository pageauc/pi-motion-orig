#!/usr/bin/python

# original script by brainflakes, improved by pageauc, peewee2 and Kesthal
# www.raspberrypi.org/phpBB3/viewtopic.php?f=43&t=45235
# modified by Claude Pageau 4-Mar-2014 to include numbering sequence plus dat/lock files for grive script integration
# also made program independent of path and file names.
# You need to install PIL to run this script
# type "sudo apt-get install python-imaging-tk" in an terminal window to do this

import StringIO
import subprocess
import os
import time
import shutil

from datetime import datetime
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


# Get the path of this python script and set some global path variables
mypath        = os.path.abspath(__file__)
baseDir       = mypath[0:mypath.rfind("/")+1]
baseFileName  = mypath[mypath.rfind("/")+1:mypath.rfind(".")]
progname      = os.path.basename(__file__)

starttime = datetime.now()

######################## Image Settings 

imagePrefix   = "Deck-"  # String that prefixes the file name for easier identification of files.
imageWidth    = 1296     # Width of image in pixels
imageHeight   = 972      # Height of image in pixels
imageQuality  = 15       # Set jpeg quality (0 to 100)
imageSettings = "-vf -hf"
imagePath     = baseDir + "google_drive"  # Folder where all images will be stored. Note baseDir where this python script is run from.
if not os.path.isdir(imagePath):
  print "%s - Creating image storage folder %s " % (progname, imagePath)
  os.makedirs(imagePath)

######################## Motion Detection Settings
#
# Motion Detect looks for changed pixels between two smaller bmp images in memory.  Image is taken if threshold exceeded.
motionOn          = True
motionPrefix      = "M-"   # Prefix in front of file name to identify that it was taken as a motion detect image.
motionThreshold   = 50     # How much a pixel has to change by to be marked as "changed"
motionSensitivity = 100    # How many changed pixels before capturing an image, needs to be higher if noisy view
motionNumberingOn = True
motionStartCount  = 1000   
motionMaxImages   = 500
motionCounter     = motionStartCount  # Keeps track of current image counter for motion file names.
motionCounterPath = baseDir + motionPrefix + baseFileName + ".dat"  # FileName that stores the current counter. Note baseDir where this python script is run from.
motionShowDateOnImage = True  # Puts a date time stamp directly on the image including imagePrefix.

######################## Force Capture Setting
#
# If Motion Detection does not see any activity during a force capture time period then image will be taken if waiting time exceeded.
forceCaptureOn          = True       # If no activity then force an image to be captured every forceCaptureTime seconds, values True or False
forceCaptureTime        = 60 * 60    # Once an hour
forceCaptureLast        = time.time()

######################### Time Lapse Settings
#
# Time lapse takes a photo on a fixed time period. Photos can have a special prefix to distinquish from motion capture
# This can be run in conjunction with motion capture and takes priority. 
timeLapseOn              = True
timeLapsePrefix          = "T-"    # Prefix in front of file name to identify that it was taken as a time lapse image.
timeLapseTime            = 60      # Seconds
timeLapseNumberingOn     = True    # Uses number sequence instate of datetime file naming
timeLapseMaxImages       = 3000    # Zero if for Ever
timeLapseStartCounter    = 1000    # Start of Numbering sequence
timeLapseCounter         = timeLapseStartCounter
timeLapseLast            = time.time()
timeLapseCounterPath     = baseDir + timeLapsePrefix + baseFileName + ".dat" # File that stores the current counter for time lapse
timeLapseShowDateOnImage = False   # Puts a Date Time stamp directly on the image file including timeLapsePrefix

# Sync Lock creates a file to indicate the there are images ready to process by grive or another program
syncLockOn   = True
syncLockPath =  baseDir + baseFileName + ".sync" 

# diskSpaceToReserve - Deletes oldest images to avoid filling disk. How much disk space to keep free.
diskReserveSpaceOn = True
diskReserveSpaceMb = 200   # Number of megabytes to reserve on Disk
diskReserveSpace   = diskReserveSpaceMb * 1024 * 1024 # Keep 200 mb free on disk

diskSpaceToReserve = diskReserveSpace

# Test-Image settings
testWidth  = 100
testHeight = 75

# this is the default setting, if the whole image should be scanned for changed pixel
testAreaCount = 1
testBorders = [ [[1,testWidth],[1,testHeight]] ]  # [ [[start pixel on left side,end pixel on right side],[start pixel on top side,stop pixel on bottom side]] ]
# testBorders are NOT zero-based, the first pixel is 1 and the last pixel is testWith or testHeight

# with "testBorders", you can define areas, where the script should scan for changed pixel
# for example, if your picture looks like this:
#
#     ....XXXX
#     ........
#     ........
#
# "." is a street or a house, "X" are trees which move arround like crazy when the wind is blowing
# because of the wind in the trees, there will be taken photos all the time. to prevent this, your setting might look like this:

# testAreaCount = 2
# testBorders = [ [[1,50],[1,75]], [[51,100],[26,75]] ] # area y=1 to 25 not scanned in x=51 to 100

# even more complex example
# testAreaCount = 4
# testBorders = [ [[1,39],[1,75]], [[40,67],[43,75]], [[68,85],[48,75]], [[86,100],[41,75]] ]

# in debug mode, a file debug.bmp is written to disk with marked changed pixel an with marked border of scan-area
# debug mode should only be turned on while testing the parameters above

debugModeOn   = False # False or True
debugFilePath = imagePath + "/debug.bmp"   # File Path of debug file

# Capture a small test image (for motion detection)
def captureTestImage(settings, width, height):
    command = "raspistill %s -w %s -h %s -t 200 -e bmp -n -o -" % (settings, width, height)
    imageData = StringIO.StringIO()
    imageData.write(subprocess.check_output(command, shell=True))
    imageData.seek(0)
    im = Image.open(imageData)
    buffer = im.load()
    imageData.close()
    return im, buffer

# Save a full size image to disk
def saveImage(filename, settings, width, height, quality, diskSpaceToReserve):
    keepDiskSpaceFree(diskSpaceToReserve)
    time = datetime.now()

    subprocess.call("raspistill %s -w %s -h %s -t 200 -e jpg -q %s -n -o %s" % (settings, width, height, quality, filename), shell=True)

    imageTagName = imagePrefix + "%04d/%02d/%02d-%02d:%02d:%02d" % (time.year, time.month, time.day, time.hour, time.minute, time.second)
    if (motionShowDateOnImage or timeLapseShowDateOnImage):
        writeDateToImage(filename,imageTagName)
    print "%s - %s saved %s" % (progname, imageTagName, filename)
    # Make a copy of the latest image so you can find where the current series ends.
    imageNow= filepath + "/" + filenamePrefix + "_current.jpg"
    shutil.copy(filename,imageNow)
    
# Keep free space above given level
def keepDiskSpaceFree(bytesToReserve):
    if (getFreeSpace() < bytesToReserve):
        for filename in sorted(os.listdir(imagePath + "/")):
            if filename.startswith(imagePrefix) and filename.endswith(".jpg"):
                os.remove(imagePath + "/" + filename)
                print "%s - Deleted %s/%s to avoid filling disk" % (progname,imagePath,filename)
                if (getFreeSpace() > bytesToReserve):
                    return

# Write Date to Image
def writeDateToImage(imagename,datetoprint):
    FOREGROUND = (255, 255, 255)
    TEXT = datetoprint
    font_path = '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
    font = ImageFont.truetype(font_path, 24, encoding='unic')
    text = TEXT.decode('utf-8')
    img = Image.open(imagename)
    draw = ImageDraw.Draw(img)
    # draw.text((x, y),"Sample Text",(r,g,b))

    draw.text((500, 930),text,FOREGROUND,font=font)
    img.save(imagename)
    return

# Get available disk space
def getFreeSpace():
    st = os.statvfs(imagePath + "/")
    du = st.f_bavail * st.f_frsize
    return du

def initialize_motion_numbering():
    # If motionCounter file does not exist create one and initialize with value of motionStartCount
    if not os.path.exists(motionCounterPath):
        print "%s - Creating New Motion Counter File %s Counter=%i" % (progname, motionCounterPath, motionStartCount)
        open(motionCounterPath, 'w').close()
        f = open(motionCounterPath, 'w+')
        f.write(str(motionStartCount -1))
        f.close()
 
    with open(motionCounterPath, 'r') as f:
        writeCount = f.read()
        f.closed
    motionCounter = int(writeCount) + 1 
    if (motionCounter > motionStartCount + motionMaxImages):
        motionCounter = motionStartCount
    return motionCounter

def initialize_timelapse_numbering():
    # If timeLapseCounter file does not exist create one and initialize with value of motionStartCount
    if not os.path.exists(timeLapseCounterPath):
        print "%s - Creating New Time Lapse Counter File %s Counter=%i" % (progname, timeLapseCounterPath, timeLapseStartCounter)
        open(timeLapseCounterPath, 'w').close()
        f = open(timeLapseCounterPath, 'w+')
        f.write(str(timeLapseStartCounter -1))
        f.close()
 
    with open(timeLapseCounterPath, 'r') as f:
        writeCount = f.read()
        f.closed
    timeLapseCounter = int(writeCount) + 1 
    if (timeLapseCounter > timeLapseStartCounter + timeLapseMaxImages):
        timeLapseCounter = timeLapseStartCounter
    return timeLapseCounter   
    
def check_for_motion(image1,buffer1):
    global forceCaptureLast motionCounter image1 buffer1
    changedPixels = 0
    # Get comparison image
    image2, buffer2 = captureTestImage(imageSettings, testWidth, testHeight)

    if (debugModeOn): # in debug mode, save a bitmap-file with marked changed pixels and with visible testarea-borders
        debugimage = Image.new("RGB",(testWidth, testHeight))
        debugimage = debugimage.load()

    for z in xrange(0, testAreaCount): # = xrange(0,1) with default-values = z will only have the value of 0 = only one scan-area = whole picture
        for x in xrange(testBorders[z][0][0]-1, testBorders[z][0][1]): # = xrange(0,100) with default-values
            for y in xrange(testBorders[z][1][0]-1, testBorders[z][1][1]):   # = xrange(0,75) with default-values; testBorders are NOT zero-based, buffer1[x,y] are zero-based (0,0 is top left of image, testWidth-1,testHeight-1 is botton right)
                if (debugModeOn):
                    debugim[x,y] = buffer2[x,y]
                    if ((x == testBorders[z][0][0]-1) or (x == testBorders[z][0][1]-1) or (y == testBorders[z][1][0]-1) or (y == testBorders[z][1][1]-1)):
                        # print "Border %s %s" % (x,y)
                        debugim[x,y] = (0, 0, 255) # in debug mode, mark all border pixel to blue
                # Just check green channel as it's the highest quality channel
                pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
                if pixdiff > motionThreshold:
                    changedPixels += 1
                    if (debugModeOn):
                        debugim[x,y] = (0, 255, 0) # in debug mode, mark all changed pixel to green
                # Save an image if pixels changed
                if (changedPixels > motionSensitivity):
                    if motionNumberingOn:
                        motionCount = str(motionCounter)
                        filename = imagePath + "/" + motionPrefix + imagePrefix + motionCount + ".jpg"
                    else:
                        filename = imagePath + "/" + motionPrefix + imagePrefix + "%04d%02d%02d-%02d%02d%02d.jpg" % (time.year, time.month, time.day, time.hour, time.minute, time.second)
                    saveImage(filename, imageSettings, imageWidth, imageHeight, imageQuality, diskReserveSpace)
                    if syncLockOn:
                        write_sync_file()
                    if forceCaptureOn
                        forceCaptureLast = time.time()
                    if motionNumberingOn:
                        motionCounter += 1
                        if (motionCounter > motionStartCount + motionMaxImages):
                            motionCounter = motionStartCount
                    if not os.path.exists(motionCounterPath):
                        print "%s - Creating %s" % (progname,motionCounterPath)
                        open(motionCounterPath, 'w').close()
                    f = open(motionCounterPath, 'w+')
                    f.write(str(motionCounter))
                    f.close()
                if ((debugModeOn == False) and (changedPixels > motionSensitivity)):
                    break  # break the y loop
            if ((debugModeOn == False) and (changedPixels > motionSensitivity)):
                break  # break the x loop
        if ((debugModeOn == False) and (changedPixels > motionSensitivity)):
            break  # break the z loop

    if (debugModeOn):
        debugimage.save(debugFilePath) # save debug image as bmp
        print "%s - Saved Debug to %s/debug.bmp  Changed Pixel=%i" % (progname, debugFilePath, changedPixels)

    image1  = image2
    buffer1 = buffer2       
    return 

def check_for_forcecapture():
    global motionCounter forceCaptureLast
    if time.time() - forceCaptureLast > forceCaptureTime:
        saveImage(filename, imageSettings, imageWidth, imageHeight, imageQuality, diskReserveSpace)
        forceCaptureLast = time.time()
        if motionNumberingOn:
            motionCounter += 1
            if (motionCounter > motionStartCount + motionMaxImages):
                motionCounter = motionStartCount
    return
    
def check_for_timelapse():
    global timeLapseLast forceCaptureLast
    if time.time() - timeLapseLast > timeLapseTime:
        if timeLapseNumberingOn:
            filename = timeLapsePrefix + filepath + "/" + imagePrefix + timeLapseCounter + ".jpg"
        else:
            filename = timeLapsePrefix + filepath + "/" + imagePrefix + "%04d%02d%02d-%02d%02d%02d.jpg" % (time.year, time.month, time.day, time.hour, time.minute, time.second)
        saveImage(filename, imageSettings, imageWidth, imageHeight, imageQuality, diskReserveSpace)
        if syncLockOn:
            write_sync_file()
        if timeLapseNumberingOn:
            timeLapseCounter += 1
            if (timeLapseCounter > timeLapseStartCount + timeLapseMaxImages):
                timeLapseCounter = timeLapseStartCount
        timeLapseLast = time.time()
        forceCaptureLast = time.time()
    return
    
def write_sync_file():
    if not os.path.exists(syncLockPath):
        print "%s - Creating %s" % (progname, syncLockPath)
        open(syncLockPath, 'w').close()
    f = open(syncLockPath, 'w+')
    f.write("Photos available to sync with grive using sync shell script")
    f.close()
    return
    
############################## Start Main Program Code 
# Initialize Settings    

# Get first motion image
if motionOn:
    # Read Saved value for Motion Numbering from a file.
    if motionNumberingOn:
        initialize_motion_numbering()
    image1, buffer1 = captureTestImage(imageSettings, testWidth, testHeight)
    
# Read Saved value for TimeLapse Numbering from a file.
if timeLapseOn:
    if timeLapseNumberingOn:
        initialize_timelapse_numbering()
    timeLapseLast = time.time()

# Reset last capture time
if forceCaptureOn:
    forceCapturelast = time.time()

starttime = datetime.now()
rightnow  = "%04d%02d%02d-%02d:%02d:%02d" % (starttime.year, starttime.month, starttime.day, starttime.hour, starttime.minute, starttime.second)

print "---------------------------------- Settings -----------------------------------------"
print "    Motion .... Sensitivity=%i Threshold=%i Cam-Settings= %s ForceCapture=%s every %i seconds"  % (motionSensitivity, motionThreshold, imageSettings, forceCaptureOn, forceCaptureTime)
print "    Image ..... W=%i H=%i Quality=%i DateOnImage=%s Prefix=%s Path=%s" % (imageWidth, imageHeight, imageQuality, motionShowDateOnImage, imagePrefix, imagePath)
print "    Numbering . On=%s Start=%s Max=%i path=%s Counter=%i" % (motionNumberingOn, motionStartCount, motionMaxImages, motionCounterPath, motionCounter)
print "    Sync File . On=%s Path=%s" % (syncLockOn, syncLockPath)
print "    DiskSpace . Reserved=%i mb" % (diskReserveSpaceMb)
print "    Debug ..... On=%s Path=%s/debug.bmp" % (debugModeOn, debugFilePath)
print "-------------------------------------------------------------------------------------"
print "%s - Waiting for Motion %s ........" % (progname, rightnow)

# Start Main Processing Loop
while (True):
    # If time lapse set on then check and write time lapse photo if required as first priority
    if timeLapseOn:
        check_for_timelapse()

    # If motion capture set on then Check if motion was detected and write photo if required second priority.
    if motionOn:
        check_for_motion(image1,buffer1)
        # Swap comparison buffers

    # If force Capture set on then check if no photos taken during the specified time period
    if forceCaptureOn:
        check_for_forcecapture()

