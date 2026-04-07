#ElevenLabs SDK
from elevenlabs.client import ElevenLabs

#Images
from term_image.image import AutoImage

#envarionment variables (.env)
from dotenv import load_dotenv

#system controls
import os
import sys
import subprocess
import multiprocessing

#pathes
from pathlib import Path

#Loading .env File
load_dotenv()

#Setup SDK
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

#Creating audio through input
audio = client.text_to_speech.convert(
    text=sys.argv[1],
    voice_id="JBFqnCBsd6RMkjVDRZzb", # Example: "George"
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128"
)

#Defining saving Path and Current working directory
audioFile   :  Path =  Path("output.mp3")
cwd         :  Path =  Path("/Files/DOCTOBOT/APIxBOT")
finalPath   :  Path =  cwd / audioFile


#Saving file to path
with open(audioFile, "wb") as f:
    for chunk in audio:
        if chunk:
            f.write(chunk)



#Showing images in terminal (Robot Face)
def showImg(imgpath:Path,isanimated:bool,align:str,scale:int,duration:float,_cwd:Path) -> None:
        subprocess.run( ["chafa",imgpath ,"--align",align, "--animate",{"on" if isanimated else "off"} ,"--scale" ,scale],cwd=_cwd ) 

#Playing audio
def playAudio(file:Path,_cwd:Path):
         subprocess.run( f"ffplay {file} -nodisp -autoexit",check=False,cwd=_cwd)

#Defining processes
chafa = multiprocessing.Process(target=showImg,args=( finalPath ,True,"center",300,1.0,cwd))
ffplay = multiprocessing.Process(target=playAudio,args=( finalPath , cwd))

#running
chafa.start()
ffplay.start()


