import cv2
import multiprocessing as mp

class Camera():

    def __init__(self, rtsp_url, verbose=True):
        # load pipe for data transmission to the process
        self.verbose = verbose
        self.parent_conn, child_conn = mp.Pipe()
        # load process
        self.p = mp.Process(target=self.update, args=(child_conn, rtsp_url))
        # start process
        self.p.daemon = True
        self.p.start()

    def end(self):
        # send closure request to process
        self.parent_conn.send(2)

    def update(self, conn, rtsp_url):
        """
        Runs the camera thread to grab data and keep the buffer empty.

        :param conn:  the Pipe to transmit data
        :param rtsp_url: the url of the camera.
        :return:
        """
        # load cam into seperate process
        if self.verbose:
            print("Cam Loading...")
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        if self.verbose:
            print("Cam Loaded...")
        run = True

        while run:
            # grab frames from the buffer
            cap.grab()
            # recieve input data
            rec_dat = conn.recv()
            if rec_dat == 1:
                # if frame requested
                ret, frame = cap.read()
                conn.send(frame)
            elif rec_dat == 2:
                # if close requested
                cap.release()
                run = False

        if self.verbose:
            print("Camera Connection Closed")
        conn.close()

    def get_frame(self, resize=None):
        """
        Grabs frame from camera

        :param resize: int - used to resize the output i.e 0.5 will half the frame
        :return:
        """

        # send request
        self.parent_conn.send(1)
        frame = self.parent_conn.recv()
        # reset request
        self.parent_conn.send(0)
        # resize if needed
        return self.rescale_frame(frame, resize) if resize is None else frame

    def rescale_frame(self, frame, percent=1):
        return cv2.resize(frame, None, fx=percent, fy=percent) if percent != 1 else frame
