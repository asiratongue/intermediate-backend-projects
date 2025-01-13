from PIL import Image

def sepia(Img):
    width, height = Img.size

    pixels = Img.load()

    for py in range(height):
        for px in range(width):
            r, g, b = Img.getpixel((px, py))

            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)

            if tr > 255:
                tr = 255

            if tg > 255:
                tg = 255
                 
            if tb > 255:
                tb = 255
               
            pixels[px, py] = (tr, tg, tb)

    return Img


def HighContrast(Img):

    width, height = Img.size

    pixels = Img.load()

    for py in range(height):
        for px in range(width):
            r, g, b = Img.getpixel((px, py))

            tr = int(1.5 * r + 0 * g + 0 * b)
            tg = int(0 * r + 1.5 * g + 0 * b)
            tb = int(0 * r + 0 * g + 1.5 * b)

            if tr > 255:
                tr = 255

            if tg > 255:
                tg = 255
                 
            if tb > 255:
                tb = 255
               
            pixels[px, py] = (tr, tg, tb)

    return Img


def Warmth(Img):

    width, height = Img.size

    pixels = Img.load()

    for py in range(height):
        for px in range(width):
            r, g, b = Img.getpixel((px, py))

            tr = int(1.2 * r + 0 * g + 0 * b)
            tg = int(0 * r + 1.1 * g + 0 * b)
            tb = int(0 * r + 0 * g + 0.9 * b)

            if tr > 255:
                tr = 255

            if tg > 255:
                tg = 255
                 
            if tb > 255:
                tb = 255
               
            pixels[px, py] = (tr, tg, tb)

    return Img



def Coolness(Img):

    width, height = Img.size

    pixels = Img.load()

    for py in range(height):
        for px in range(width):
            r, g, b = Img.getpixel((px, py))

            tr = int(0.9 * r + 0 * g + 0 * b)
            tg = int(0 * r + 0.9 * g + 0 * b)
            tb = int(0 * r + 0 * g + 1.2 * b)

            if tr > 255:
                tr = 255

            if tg > 255:
                tg = 255
                 
            if tb > 255:
                tb = 255
               
            pixels[px, py] = (tr, tg, tb)

    return Img
 
def Vintage(Img):

    width, height = Img.size

    pixels = Img.load()

    for py in range(height):
        for px in range(width):
            r, g, b = Img.getpixel((px, py))

            tr = int(0.9 * r + 0.5 * g + 0.1 * b)
            tg = int(0.3 * r + 0.8 * g + 0.1 * b)
            tb = int(0.2 * r + 0.3 * g + 0.5 * b)

            if tr > 255:
                tr = 255

            if tg > 255:
                tg = 255
                 
            if tb > 255:
                tb = 255
               
            pixels[px, py] = (tr, tg, tb)

    return Img

def fallenAngel(Img):

    width, height = Img.size

    pixels = Img.load()

    for py in range(height):
        for px in range(width):
            r, g, b = Img.getpixel((px, py))

            tr = int(1.3 * r + -0.1 * g + -0.1 * b)
            tg = int(0.1 * r + 1.5 * g + 0.2 * b)
            tb = int(0.1 * r + 0.2 * g + 1.4 * b)

            if tr > 255:
                tr = 255

            if tg > 255:
                tg = 255
                  
            if tb > 255:
                tb = 255
               
            pixels[px, py] = (tr, tg, tb)

    return Img