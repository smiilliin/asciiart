# AsciiART

Converts an image to a string ASCII string image, or displays the screen as a string image in real time.

## Install

Install packages

```bash
sudo apt-get install python3-tk
sudo pip3 install -r requirements.txt
```

## Usage

Usage of Ascii art. You can check with `python main.py --help.`

```bash
usage: AsciiART [-h] [--font-path FONT_PATH] [--font-size FONT_SIZE] [--range-start RANGE_START] [--range-end RANGE_END] [--epochs EPOCHS] [--input INPUT] [--output OUTPUT] [--loutput LOUTPUT] [--video-input VIDEO_INPUT] [--video-output VIDEO_OUTPUT] [--end-range END_RANGE]

Ascii Art generator

options:
  -h, --help            show this help message and exit
  --font-path FONT_PATH
  --font-size FONT_SIZE
  --range-start RANGE_START
  --range-end RANGE_END
  --epochs EPOCHS
  --input INPUT
  --output OUTPUT
  --loutput LOUTPUT
  --video-input VIDEO_INPUT
  --video-output VIDEO_OUTPUT
  --end-range END_RANGE
```

| option       | description                   |
| ------------ | ----------------------------- |
| font path    | font file path                |
| font size    | font size                     |
| range start  | ascii code range start        |
| range end    | ascii code range end          |
| epochs       | learning epochs               |
| input        | image input file path         |
| output       | image output path             |
| loutput      | gray image output path        |
| video input  | video input file path         |
| video output | video output file path        |
| end range    | video ending percentage range |

### Convert image to string image

Convert the example.png file to result.png file

```bash
python3 main.py --input=example.png --output=result.png
```

### Convert video to string video

Convert the badApple.mp4 file to result.mp4 file

```bash
python3 main.py --video-input=badApple.mp4 --video-output=result.mp4 --end-range=10
```

### Show string screen

Convert the screen in real time.

```bash
python3 main.py
```
