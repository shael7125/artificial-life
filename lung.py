from PIL import Image
from PIL import ImageOps

# load your downloaded lung image
img = Image.open("lung.png").convert("L")

# create a new black & white image 
mask = Image.new("L", img.size)

threshold = 128  # everything brighter becomes white (inside), darker becomes black

for x in range(img.width):
    for y in range(img.height):
        pixel = img.getpixel((x,y))
        mask.putpixel((x,y), 255 if pixel > threshold else 0)

mask = ImageOps.invert(mask)
mask.save("lung_mask.png")

mask.save("lung_mask.png")
