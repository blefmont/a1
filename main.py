# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow

import sys, os, numpy

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



# Image directory and pathe to image file

imgDir      = 'images'
imgFilename = 'mandrill.png'

imgPath = os.path.join( imgDir, imgFilename )



# File dialog

import Tkinter, tkFileDialog

#root = Tkinter.Tk()
#root.withdraw()



# Read and modify an image.

def buildImage():
  global Key_h, Key_a
  # Read image and convert to YCbCr

  print imgPath
  src = Image.open( imgPath ).convert( 'YCbCr' )
  srcPixels = src.load()

  width  = src.size[0]
  height = src.size[1]




  xdim = 3
  ydim = 1
  #EF = [[0.0625,0.125,0.0625],[0.125,0.25,0.125],[0.0625,0.125,0.0625]]
  #EF = [[0.3333333,0.3333333,0.3333333]]
  EF = [[0,0,1]]
  #EF = [[1,1,1],[1,-8,1],[1,1,1]]



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

  # Done
   ######################### histogram List generator

  histList = histogram_List_generator(dstPixels, width, height)

  if Key_h:
      # TODO: cannot catch key action
      histList = histogram_List_generator(dstPixels, width, height)
      print histList
      256/sum(histList)* -1
      for i in range(width):
          for j in range(height):

              y,cb,cr = dstPixels[i,j]
              y = round(((256/(480.0*480.0)) * sum(histList[:y]))-1) # using the function from the note
              dstPixels[i,j] = (y,cb,cr)

      print histogram_List_generator(dstPixels, width, height)
   ######################### filter applying


  fimg = Image.new( 'YCbCr', (width,height) )
  fPixels = fimg.load()
  for i in range(width):
    for j in range(height):

        tmp = 0
        for a in range(ydim):
            for b in range(xdim):
          #print len
                if i-b < 0 or j-a < 0:
                    Y = 0
                else:
                    Y,CB,CR = dstPixels[i-b,j-a]
                tmp += EF[a][b] * Y
          #print tmp == Y
        y = int(tmp)
        fPixels[i,j] = (y,CB,CR)




  #########################

  return fimg.convert( 'RGB' )

################## HELPING FUNCTIONS #################
def histogram_List_generator(pixel, width, height):
    histList = [0]*256
    for i in range(width):
        for j in range(height):
          y,cb,cr = pixel[i,j]
          histList[y] +=1  ## generate the histogram list
    return histList


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

  global factor, bright

  factor = initFactor + diffX / float(windowWidth)
  bright = initBright + diffY / float(windowHeight) * 225

  if factor < 0:
    factor = 0

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
