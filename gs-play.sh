/usr/bin/gst-launch-1.0 filesrc location=test.h264 ! h264parse ! avdec_h264 ! videoconvert ! videorate ! "video/x-raw,framerate=25/1" ! ximagesink 
