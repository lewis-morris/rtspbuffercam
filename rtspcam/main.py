from cv2 import VideoCapture, CAP_FFMPEG, resize
import logging
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection


class Camera:
    SEND_FRAME = 1
    END_PROCESS = 2
    log: logging.Logger = logging.getLogger("camera_api")
    parent_conn: Connection
    p: Process

    def __init__(self, rtsp_url: str, buffer: bool = False):
        self._init_logging(logging.INFO)
        self.log.debug("creating pipe for data transmission to the process")
        self.parent_conn, child_conn = Pipe()
        self.log.debug("creating sub-process object")
        self.p = Process(target=self.update, args=(child_conn, rtsp_url, buffer))
        self.p.daemon = True
        self.log.debug("Starting subprocess")
        self.p.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()

    def end(self):
        self.log.debug("send closure request to process")
        self.parent_conn.send(self.END_PROCESS)

    def update(self, conn: Connection, rtsp_url: str, buffer: bool):
        """
        Runs the rtspcam thread to grab data and keep the buffer empty.

        :param conn:  the Pipe to transmit data
        :param rtsp_url: the url of the rtspcam.
        :param buffer:  should the client read frame by frame from the buffer or just grab the latest frame?
        :return:
        """
        self.log.info(f"Starting video capture client for {rtsp_url}")
        cap = VideoCapture(rtsp_url, CAP_FFMPEG)
        self.log.info("Started...")
        run = True
        while run:
            if not conn.poll() and not buffer:
                self.log.debug("clearing buffer frame")
                cap.grab()
                continue
            rec_dat = conn.recv()
            if rec_dat == self.SEND_FRAME:
                self.log.debug("Sending next frame to parent process")
                return_value, frame = cap.read()
                conn.send(frame)
            elif rec_dat == self.END_PROCESS:
                self.log.debug("Closing connection")
                cap.release()
                run = False

        self.log.info("Camera Connection Closed")
        conn.close()

    def get_frame(self, resize_scale: float = None):
        """
        Grabs frame from rtspcam

        :param resize_scale: float - used to resize the output i.e 0.5 will half the frame
        :return:
        """

        self.log.debug("sending frame capture command")
        self.parent_conn.send(self.SEND_FRAME)
        frame = self.parent_conn.recv()
        self.log.debug("frame received")
        return self.rescale_frame(frame, resize_scale) if resize_scale is not None else frame

    def rescale_frame(self, frame, percent:float=1.0):
        self.log.debug(f"resizing image bay factor {percent}")
        return resize(frame, None, fx=percent, fy=percent) if percent != 1.0 else frame

    def _init_logging(self, level):
        self.log.setLevel(level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.log.handlers.pop()
        self.log.addHandler(console_handler)
