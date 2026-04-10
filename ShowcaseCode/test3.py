import os
import vlc
import time
import random
import shutil
import subprocess
import multiprocessing
from dotenv import load_dotenv
from pathlib import Path

#============================================================================================

AnimationNumber: int = 0
load_dotenv()

#============================================================================================

envkey:str = f"ANIMATION_PATH{AnimationNumber}"

#============================================================================================

def play_audio(path:Path):
    p:vlc.MediaPlayer = vlc.MediaPlayer(path)
    p.play()

    time.sleep(0.5)
    while p.is_playing() :
        time.sleep(1)

#============================================================================================

def play_gif(envkey:str):
    columns, lines = shutil.get_terminal_size()
    try:
        while True:
            print(envkey)
            FilePath : Path = Path(os.getenv(envkey))
            subprocess.run(["chafa", f"--size={columns+6}x{lines}","--align","center","--speed",'10', FilePath])
            time.sleep(3)
    except FileNotFoundError:
        print("خطأ: يجب تثبيت chafa أولاً (sudo apt install chafa)")
    except KeyboardInterrupt:
        subprocess.run(["pkill","chafa"])
        subprocess.run(["clear"])
        print("Goodbye")

#============================================================================================

GIFPlay = multiprocessing.Process(target=play_gif,args=[envkey])
GIFPlay.start()

#============================================================================================

play_audio(Path("./voices/FP.mp3"))
time.sleep(11)
#============================================================================================

AnimationNumber = 1
envkey= f"ANIMATION_PATH{AnimationNumber}"
#============================================================================================

subprocess.run(['pkill','chafa'])
GIFPlay.terminate()

#============================================================================================

GIFPlay = multiprocessing.Process(target=play_gif,args=[envkey])
GIFPlay.start()
time.sleep(3)
play_audio(Path("./voices/Welcome.mp3"))
time.sleep(2)
play_audio(Path("./voices/processing.mp3"))
#============================================================================================
for _ in range(10):
    AnimationNumber = 4
    envkey= f"ANIMATION_PATH{AnimationNumber}"

    #============================================================================================

    subprocess.run(['pkill','chafa'])
    GIFPlay.terminate()

    #============================================================================================

    GIFPlay = multiprocessing.Process(target=play_gif,args=[envkey])
    GIFPlay.start()
    time.sleep(0.5)

    #============================================================================================

    AnimationNumber = 5
    envkey= f"ANIMATION_PATH{AnimationNumber}"

    #============================================================================================

    subprocess.run(['pkill','chafa'])
    subprocess.run(['clear'])
    GIFPlay.terminate()

    #============================================================================================

    GIFPlay = multiprocessing.Process(target=play_gif,args=[envkey])
    GIFPlay.start()
    time.sleep(0.5)

    #============================================================================================


    AnimationNumber = 1
    envkey= f"ANIMATION_PATH{AnimationNumber}"

    #============================================================================================

    subprocess.run(['pkill','chafa'])
    subprocess.run(['clear'])
    GIFPlay.terminate()

    #============================================================================================

    GIFPlay = multiprocessing.Process(target=play_gif,args=[envkey])
    GIFPlay.start()
    time.sleep(2)


AnimationNumber = 3
envkey= f"ANIMATION_PATH{AnimationNumber}"

#============================================================================================

subprocess.run(['pkill','chafa'])
subprocess.run(['clear'])
GIFPlay.terminate()

#============================================================================================

GIFPlay = multiprocessing.Process(target=play_gif,args=[envkey])
GIFPlay.start()
play_audio(Path("./voices/38.1.mp3"))
time.sleep(0.3)

#============================================================================================

AnimationNumber = 1
envkey= f"ANIMATION_PATH{AnimationNumber}"

#============================================================================================

subprocess.run(['pkill','chafa'])
subprocess.run(['clear'])
GIFPlay.terminate()

#============================================================================================

GIFPlay = multiprocessing.Process(target=play_gif,args=[envkey])
GIFPlay.start()
play_audio(Path("./voices/result.mp3"))
time.sleep(2)

#============================================================================================

AnimationNumber = 1
envkey= f"ANIMATION_PATH{AnimationNumber}"

#============================================================================================

subprocess.run(['pkill','chafa'])
subprocess.run(['clear'])
GIFPlay.terminate()

#============================================================================================

GIFPlay = multiprocessing.Process(target=play_gif,args=[envkey])
GIFPlay.start()
play_audio(Path("./voices/Bye.mp3"))
time.sleep(0.3)

AnimationNumber = 6
envkey= f"ANIMATION_PATH{AnimationNumber}"

#============================================================================================

subprocess.run(['pkill','chafa'])
subprocess.run(['clear'])
GIFPlay.terminate()

#============================================================================================

GIFPlay = multiprocessing.Process(target=play_gif,args=[envkey])
GIFPlay.start()
time.sleep(1)

subprocess.run(['pkill','chafa'])
subprocess.run(['clear'])
GIFPlay.terminate()
