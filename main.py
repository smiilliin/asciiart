from PIL import Image, ImageDraw, ImageFont, ImageGrab, ImageTk
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from keras.models import Sequential, model_from_json
from keras.utils import to_categorical
from argparse import ArgumentParser, FileType
from os.path import isfile
import tkinter as tk
import cv2
import numpy as np


def getFontSize(font):
  maxWidth = 0
  maxHeight = 0
  for i in range(32, 126 + 1):
    left, top, right, bottom = font.getbbox(chr(i))
    width = right
    height = bottom

    if maxWidth < width:
      maxWidth = width
    if maxHeight < height:
      maxHeight = height

  return (maxWidth, maxHeight)


def getChrImage(character, bgColor=0, color=255):
  global fontWidth, fontHeight, font
  image = Image.new("L", (fontWidth, fontHeight), color=bgColor)
  draw = ImageDraw.Draw(image)
  draw.text((0, 0), character, color, font)

  return np.array(image) / 255.0


def getTextImage(data, width, height, bgColor=0, color=255):
  global fontWidth, fontHeight, font

  image = Image.new(
      "L", (width * fontWidth, height * fontHeight), color=bgColor)
  draw = ImageDraw.Draw(image)

  for i, line in enumerate(data):
    draw.text((0, i * fontHeight), "".join(line), color, font)

  return image


def saveModel(model):
  modelJSON = model.to_json()
  with open("model.json", "w") as json_file:
    json_file.write(modelJSON)
  model.save_weights("weights.h5")


def loadModel():
  with open("model.json", "r") as json_file:
    modelJSON = json_file.read()
    model = model_from_json(modelJSON)
  model.load_weights("weights.h5")
  return model


def makeModel(rangeStart, rangeEnd, epochs):
  global fontWidth, fontHeight

  imagesData = []
  yData = []
  for i in range(rangeStart, rangeEnd + 1):
    imageData = getChrImage(chr(i))
    imagesData.append(imageData)
    yData.append(i - rangeStart)

  imagesData = np.array(imagesData)

  classNum = len(imagesData)
  xData = imagesData.reshape(len(imagesData), fontWidth, fontHeight, 1)
  yData = np.array(yData)
  yData = to_categorical(yData, num_classes=classNum)

  model = Sequential()
  model.add(Conv2D(32, (3, 3), activation='relu',
            input_shape=(fontWidth, fontHeight, 1)))
  model.add(MaxPooling2D((2, 2)))
  model.add(Conv2D(64, (3, 3), activation='relu'))
  model.add(MaxPooling2D((2, 2)))
  model.add(Conv2D(64, (3, 3), activation='relu'))
  model.add(Flatten())
  model.add(Dense(64, activation='relu'))
  model.add(Dense(classNum, activation='softmax'))

  model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'])

  model.fit(xData, yData, epochs=epochs, batch_size=64, validation_split=0.2)
  saveModel(model)
  return model


def getStringImage(image, model, rangeStart):
  width, height = image.size
  width //= fontWidth
  height //= fontHeight

  image = np.array(image) / 255.0

  inputData = []
  for y in range(0, height, 1):
    for x in range(0, width, 1):
      fragment = image[y * fontHeight:(y+1) * fontHeight,
                       x * fontWidth:(x+1) * fontWidth, np.newaxis]
      fragment = fragment.reshape(fontWidth, fontHeight, 1)

      inputData.append(fragment)

  inputData = np.array(inputData)
  inputData = inputData.reshape(len(inputData), fontWidth, fontHeight, 1)
  result = model.predict(inputData)
  result = np.argmax(result, axis=1)
  result = np.vectorize(chr)(result + rangeStart).reshape(height, width)

  return getTextImage(result, width, height)


def fromImage(model, rangeStart, inputPath, outputPath, loutputPath):
  image = Image.open(inputPath).convert("L")

  image.save(loutputPath)

  resultImage = getStringImage(image, model, rangeStart)
  resultImage.save(outputPath)


def fromScreen(model, rangeStart):
  global root
  image = ImageGrab.grab().convert("L")
  windowWidth = image.size[0] // 2
  windowHeight = image.size[1] // 2

  root = tk.Tk()
  root.title("AsciiART")
  label = tk.Label(root)
  label.pack()

  while True:
    image = ImageGrab.grab().convert("L")

    frame = getStringImage(image, model, rangeStart).resize(
        size=(windowWidth, windowHeight))
    frameImage = ImageTk.PhotoImage(frame)

    label.configure(image=frameImage)
    root.update()


def fromVideo(model, rangeStart, videoInput, videoOutput, endRange):
  global fontWidth, fontHeight

  cap = cv2.VideoCapture(videoInput)
  width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
  height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
  fps = cap.get(cv2.CAP_PROP_FPS)
  fourcc = cv2.VideoWriter_fourcc(*'mp4v')
  out = cv2.VideoWriter(videoOutput, fourcc, fps, (int(
      (width // fontWidth) * fontWidth), int((height // fontHeight) * fontHeight)))
  frameLength = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
  frameIndex = 1

  while cap.isOpened():
    success, frame = cap.read()

    if not success:
      break

    image = Image.fromarray(frame).convert("L")
    image = getStringImage(image, model, rangeStart)
    out.write(np.array(image.convert("RGB")))

    progress = frameIndex / frameLength * 100
    if progress >= endRange:
      break

    frameIndex += 1
    print(f"{progress}%")

  cap.release()
  out.release()


def main(fontPath, fontSize, rangeStart, rangeEnd, epochs, inputPath, outputPath, loutputPath, videoInput, videoOutput, endRange):
  global fontWidth, fontHeight, font

  font = ImageFont.truetype(fontPath, fontSize)
  fontWidth, fontHeight = getFontSize(font)

  if not isfile("model.json"):
    model = makeModel(rangeStart=rangeStart, rangeEnd=rangeEnd, epochs=epochs)
  else:
    model = loadModel()

  if inputPath:
    fromImage(model=model, rangeStart=rangeStart, inputPath=inputPath,
              outputPath=outputPath, loutputPath=loutputPath)
  elif videoInput:
    fromVideo(model=model, rangeStart=rangeStart, videoInput=videoInput,
              videoOutput=videoOutput, endRange=endRange)
  else:
    fromScreen(model=model, rangeStart=rangeStart)


if __name__ == "__main__":
  parser = ArgumentParser(
      prog='AsciiART',
      description='Ascii Art generator')
  parser.add_argument("--font-path", required=False,
                      type=FileType("r"), default="CascadiaMono.ttf")
  parser.add_argument("--font-size", required=False, type=int, default=30)
  parser.add_argument("--range-start", required=False, type=int, default=32)
  parser.add_argument("--range-end", required=False, type=int, default=126)
  parser.add_argument("--epochs", required=False, type=int, default=800)
  parser.add_argument("--input", required=False, type=FileType("r"))
  parser.add_argument("--output", required=False,
                      type=str, default="result.png")
  parser.add_argument("--loutput", required=False,
                      type=str, default="LMode.png")
  parser.add_argument("--video-input", required=False, type=FileType("r"))
  parser.add_argument("--video-output", required=False,
                      type=str, default="result.mp4")
  parser.add_argument("--end-range", required=False, type=int, default=100)

  args = parser.parse_args()
  main(fontPath=args.font_path.name, fontSize=args.font_size, rangeStart=args.range_start, rangeEnd=args.range_end,
       epochs=args.epochs, inputPath=(args.input.name if args.input else None), outputPath=args.output, loutputPath=args.loutput,
       videoInput=(args.video_input.name if args.video_input else None), videoOutput=args.video_output, endRange=args.end_range)
