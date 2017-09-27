import sys, os, numpy

try: # Pillow
  from PIL import Image, ImageEnhance, ImageDraw
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
factor_x = 0 # factor by which luminance is scaled
factor_y = 1 # for mouse only


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
  global Key_h
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
  y_list=[]
  for i in range(width):
    for j in range(height):

      # read source pixel

      y,cb,cr = srcPixels[i,j]

      # ---- MODIFY PIXEL ----


      y = int(factor_y * y +(factor_x*50))



      # write destination pixel (while flipping the image in the vertical direction)

      dstPixels[i,height-j-1] = (y,cb,cr)

  # Done
  dstPixels = dst.load()


  return dst.convert( 'RGB' )

######################################################

def img_histogram():
    img = buildImage().convert('L')
    width, height = img.size
    pixels = img.load()
    # cumulative histogram generator
    a = [0]*256
    for w in range(width):
        for h in range(height):
            p = pixels[w,h]
            a[p] = a[p] + 1
#    print a

    histogram = Image.new('RGB',(256,256),(255,255,255))
    draw = ImageDraw.Draw(histogram)
    for k in range(256):
        a[k] = a[k]/10
        start = (k,255)
        end = (k,255-a[k])
        draw.line([start, end], (0,0,0))
    histogram.show()

    img = histeq(img,width,height).convert('L')
    width, height = img.size
    pixels = img.load()
    # cumulative histogram generator
    a = [0]*256
    for w in range(width):
        for h in range(height):
            p = pixels[w,h]
            a[p] = a[p] + 1
#    print a
    histogram = Image.new('RGB',(256,256),(255,255,255))
    draw = ImageDraw.Draw(histogram)
    for k in range(256):
        a[k] = a[k]*200/max(a)
        start = (k,255)
        end = (k,255-a[k])
        draw.line([start, end], (0,0,0))
    histogram.show()

def histeq(i,width, height):
    img = numpy.array(i)
    imghist,bins = numpy.histogram(img.flatten(),256)
    cumulative_distribution = imghist.cumsum()
    # print
    cumulative_distribution = 256*cumulative_distribution/cumulative_distribution[-1]

    img2 = numpy.interp(img.flatten(),bins[:-1],cumulative_distribution)

    Image.fromarray(img2.reshape(width, height)).show()
    return Image.fromarray(img2.reshape(width, height))

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
     img_histogram()
     Key_h = True


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
initFactor_x = 0
initFactor_y = 0


# Handle mouse click/unclick

def mouse( btn, state, x, y ):

  global button, initX, initY, initFactor_x, initFactor_y

  if state == GLUT_DOWN:

    button = btn
    initX = x
    initY = y
    initFactor_x = factor_x
    initFactor_y = factor_y

  elif state == GLUT_UP:

    button = None



# Handle mouse motion

def motion( x, y ):

  diffX = x - initX
  diffY = y - initY

  global factor_x, factor_y

  factor_x = initFactor_x + diffX / float(windowWidth)
  factor_y = initFactor_y + diffY / float(windowHeight)

  if factor_x < 0:
    factor_x = 0
  if factor_y < 0:
    factor_y = 0

  glutPostRedisplay()

################################## no need to change ##################################

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
