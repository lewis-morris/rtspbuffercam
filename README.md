# rtspbuffercam

rtspbuffercam can be used to connect to and read images for rtsp enabled camera's.

It uses sub processes to exhaust camera's buffer and eliminate any lag that might occur using a vanilla opencv connection.  


## Installation

Using pypi

```bash
pip install rtspbuffercam

```

or from source 

```bash
git clone https://github.com/lewis-morris/rtspbuffercam
cd rtspbuffercam
python setup.py install
```

## Example Usage

```python
#import the rtspcam
from rtspcam import Camera

#create a new rtspcam object  
cam = Camera("rtsp://admin:[your password]@192.168.0.40/h264Preview_01_main")

#read image
image = cam.get_frame()

```

