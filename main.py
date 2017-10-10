# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow

import sys, os, numpy, math

try: # Pillow
  from PIL import Image
except:
  print 'Error: Pillow has not been installed.'
  sys.exit(0)

try: # PyOpenGL
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print 'Error: PyOpenGL has not been installed.'
  sys.exit(0)



# Globals

windowWidth  = 600 # window dimensions
windowHeight =  800
Key_h = False
Key_a = False
factor = 1 # factor by which luminance is scaled
bright = 0 # about by which the brightness is changed

xdim = 1
ydim = 1
filterData = [[1]]

radius = 2
toFilter = set()
wasRC = False
lastX = 0
lastY = 0

# Image directory and pathe to image file

imgDir      = 'images'
imgFilename = 'mandrill.png'

imgPath = os.path.join( imgDir, imgFilename )



# File dialog

import Tkinter, tkFileDialog

root = Tkinter.Tk()

root.withdraw()



# Read and modify an image.

def buildImage():
  global Key_h, Key_a, toFilter
  # Read image and convert to YCbCr

  print imgPath
  src = Image.open( imgPath ).convert( 'YCbCr' )
  srcPixels = src.load()

  width  = src.size[0]
  height = src.size[1]


  # Set up a new, blank image of the same size

  dst = Image.new( 'YCbCr', (width,height) )
  dstPixels = dst.load()

  # Build destination image from source image

  for i in range(width):
    for j in range(height):

      # read source pixel

      y,cb,cr = srcPixels[i,j]

      # ---- MODIFY PIXEL ----

      y = int(factor * y + bright) if int(factor * y + bright)<=255 else 255
      

      # write destination pixel (while flipping the image in the vertical direction)

      dstPixels[i,height-j-1] = (y,cb,cr)

      if (i,j) in toFilter:
        dstPixels[i, height-j-1] = convolution(dstPixels, i, j, width, height)
        toFilter.remove((i,j))

  # Done
   ######################### histogram List generator

  histList = histogram_List_generator(dstPixels, width, height)

  
  if Key_h:
      histList, count = histogram_List_generator(dstPixels, width, height)
      print histList
      for i in range(width):
          for j in range(height):

              y,cb,cr = dstPixels[i,j]
              y = round(((count/(480.0*480.0)) * sum(histList[:y]))-1) # using the function from the note
              dstPixels[i,j] = (y,cb,cr)
      histList, count = histogram_List_generator(dstPixels, width, height)
      print histList
      #Key_h = False
   ######################### filter applying

  if Key_a:

      fimg = Image.new( 'YCbCr', (width,height) ) # new img
      fPixels = fimg.load()
      for i in range(width):
          for j in range(height):

              fPixels[i,j] = convolution(dstPixels, i, j, width, height)

      dst = fimg
      #Key_a = False


  #########################

  return dst.convert( 'RGB' )

################## HELPING FUNCTIONS #################
def histogram_List_generator(pixel, width, height):
    histList = [0]*256
    count = 0
    for i in range(width):
        for j in range(height):
          y,cb,cr = pixel[i,j]
          histList[y] +=1  ## generate the histogram list
    for i in range(len(histList)):
        if histList[i] != 0:
            count +=1
    return histList, count

def filter(File):
    global xdim, ydim, filterData
    ##use global varible to save xdim, ydim, filterData


def convolution(Pixels, x, y, width, height):
    global xdim, ydim, filterData


    tmpy, tmpcb, tmpcr = 0,0,0
    Y,CB,CR = Pixels[x,y]
    for a in range(ydim):
        for b in range(xdim):
            if x-(len(filterData[0])/2)+b < 0 or y-(len(filterData)/2)+a < 0 or x-(len(filterData[0])/2)+b > width-1 or y-(len(filterData)/2)+a > height-1:
                Y=0
            else:
                Y,CB,CR = Pixels[x-(len(filterData[0])/2)+b,y-(len(filterData)/2)+a]
            tmpy += filterData[a][b] * Y
            tmpcb += filterData[a][b] * CB
            tmpcr += filterData[a][b] * CR
    return int(round(tmpy)), int(round(tmpcb)), int(round(tmpcr)) # return (Y,Cb,Cr)


def loadFilter():
    global xdim, ydim, filterData
   
    path = tkFileDialog.askopenfilename( initialdir = 'filters' )
    if path:
       
        filterFile = open(path)
        xydim = filterFile.readline().strip().split()
        scaleFactor = filterFile.readline().strip()
       
        data = filterFile.readlines()
        for i in range(len(data)):
          data[i] = data[i].strip()
          data[i] = data[i].split()
          for j in range(len(data[i])):
             data[i][j] = float(data[i][j])
             data[i][j] = data[i][j]*float(scaleFactor)

        
        xdim = int(xydim[0])
        ydim = int(xydim[1])
        filterData = data

def filterCircle(centerX, centerY):
    global toFilter

    print ("filterCircle:", centerX, centerY)
    for i in range(-radius, radius + 1):
        for j in range (-radius, radius + 1):
            distance = math.sqrt((centerX - (centerX + i))**2 + (centerY - (centerY + j))**2)
            if distance <= radius:
                toFilter.add(((centerX + i) , (centerY + j)))
   # print toFilter
  
######################################################

# Set up the display and draw the current image

def display():

  # Clear window

  glClearColor ( 1, 1, 1, 0 )
  glClear( GL_COLOR_BUFFER_BIT )

  # rebuild the image

  img = buildImage()

  width  = img.size[0]
  height = img.size[1]

  # Find where to position lower-left corner of image

  baseX = (windowWidth-width)/2
  baseY = (windowHeight-height)/2

  glWindowPos2i( baseX, baseY )

  # Get pixels and draw

  imageData = numpy.array( list( img.getdata() ), numpy.uint8 )

  glDrawPixels( width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

  glutSwapBuffers()



# Handle keyboard input

def keyboard( key, x, y ):
  global Key_h, Key_a, radius

  if key == '\033': # ESC = exit
    sys.exit(0)

  elif key == 'l':
    path = tkFileDialog.askopenfilename( initialdir = imgDir )
    if path:
      loadImage( path )

  elif key == 's':
    outputPath = tkFileDialog.asksaveasfilename( initialdir = '.' )
    if outputPath:
      saveImage( outputPath )

  elif key == 'h':
     Key_h = True

  elif key == 'a':
     Key_a = True
  elif key == 'f':     
     loadFilter()
  elif key == "-" or key == "_":
    radius -= 1
  elif key == "+" or key == "=":
    radius += 1
  else:
    print 'key =', key    # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

  glutPostRedisplay()



# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.

def loadImage( path ):

  global imgPath
  imgPath = path

def saveImage( path ):

  buildImage().save( path )



# Handle window reshape

def reshape( newWidth, newHeight ):

  global windowWidth, windowHeight

  windowWidth  = newWidth
  windowHeight = newHeight

  glutPostRedisplay()



# Mouse state on initial click

button = None
initX = 0
initY = 0
initFactor = 0
initBright = 0



# Handle mouse click/unclick

def mouse( btn, state, x, y ):

  global button, initX, initY, initFactor, initBright

  if state == GLUT_DOWN:

    button = btn
    initX = x
    initY = y
    initFactor = factor
    initBright = bright

  elif state == GLUT_UP:

    button = None



# Handle mouse motion

def motion( x, y ):

  diffX = x - initX
  diffY = y - initY
  

  global factor, bright, button, wasRC, lastX, lastY
  print "pos", x,y
  print "button", button
  if button == 0:
    factor = initFactor + diffX / float(windowWidth)
    bright = initBright + diffY / float(windowHeight) * 225
    wasRC = False
  elif button == 2:
    if wasRC:
      mdiffX = lastX - x
      mdiffY = lastY - y
      distance = math.sqrt((x-lastX)**2 + (y-lastY)**2)
      prevCircleX = lastX
      prevCircleY = lastY
      print "last pos", lastX, lastY
      print "Distance between RC", distance
      for i in range (int(distance)):
        filterCircle(int(round(prevCircleX + (mdiffX*(i+1))/distance)), int(round(prevCircleY + (mdiffY*(i+1))/distance)))
        prevCircleX = prevCircleX + ((mdiffX*(i+1))/distance)
        prevCircleY = prevCircleY + ((mdiffY*(i+1))/distance)

       # filterCircle(int(round(lastX + ((x-lastX) * i)/distance)), int(round(initY + ((y-lastY) * i)/distance)))        
      
    else:
      filterCircle(x,y)
    wasRC = True
  ##  print toFilter
  else:
    wasRC = False
  if factor < 0:
    factor = 0
  lastX = x
  lastY = y
  glutPostRedisplay()


# Run OpenGL

glutInit()
glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
glutInitWindowSize( windowWidth, windowHeight )
glutInitWindowPosition( 50, 50 )

glutCreateWindow( 'imaging' )

glutDisplayFunc( display )
glutKeyboardFunc( keyboard )
glutReshapeFunc( reshape )
glutMouseFunc( mouse )
glutMotionFunc( motion )

glutMainLoop()


