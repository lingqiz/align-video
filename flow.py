import cv2
import numpy as np

def get_frames(video, start, end, sample=1.0, fr=120):
    '''
    Get frames from start (sec) to end (sec) from the video
    '''
    start_index = start * fr
    video.set(cv2.CAP_PROP_POS_FRAMES, start_index)

    frames = []
    for i in range(int((end - start) * fr)):
        ret, frame = video.read()
        if not ret:
            break

        frames.append(convert_frame(frame, sample))

    return np.array(frames)

def convert_frame(frame, sample=1.0):
    '''
    Convert frame to grayscale and resize
    '''
    return cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                      None, fx=sample, fy=sample)

def compute_flow(frames, polar=False):
    # initialization
    n_frame = frames.shape[0]

    prev_frame = frames[0]
    delta = np.zeros((n_frame - 1, *prev_frame.shape, 2))

    if polar:
        magnitude = np.zeros((n_frame - 1, *prev_frame.shape))
        angle = np.zeros((n_frame - 1, *prev_frame.shape))

    for i in range(1, n_frame):
        frame = frames[i]

        # compute dense optical flow using Farneback method
        flow = cv2.calcOpticalFlowFarneback(prev_frame, frame, None,
                                            pyr_scale=0.5, levels=3,
                                            winsize=15, iterations=3,
                                            poly_n=5, poly_sigma=1.2, flags=0)
        # roll forward frames
        prev_frame = frame

        # convert flow to magnitude and angle
        delta[i - 1] = flow
        if polar:
            magnitude[i - 1], angle[i - 1] = cv2.cartToPolar(flow[..., 0],
                                                             flow[..., 1])

    if polar:
        return delta, magnitude, angle

    return delta

def flow_rgb(magnitude, angle):
    '''
    Convert optical flow to RGB for visualization
    '''
    hsv = np.zeros((*magnitude.shape, 3), dtype=np.uint8)
    hsv[..., 1] = 255
    hsv[..., 0] = angle * 180 / np.pi / 2 # openCV uses 0-180 degrees for hue angle
    hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)

    # Convert HSV to RGB for visualization
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)