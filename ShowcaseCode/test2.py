import vlc
import time

p = vlc.MediaPlayer("/home/yazan/Downloads/tl-b-bwbjy-hhhh.mp3")
p.play()

# انتظر قليلاً حتى يبدأ التشغيل ثم تحقق من الحالة
time.sleep(0.5)
while p.is_playing():
    time.sleep(1)

