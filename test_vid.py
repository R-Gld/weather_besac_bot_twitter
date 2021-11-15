import glob
import cv2
from datetime import date


def __createVid(img_src: str, output_dir: str):
    FPS = 30


    # get alll the images
    glob_l = glob.glob(img_src + "*.jpg")
    # Get the Size of the images
    img = cv2.imread(glob_l[0])
    height, width, layers = img.shape
    size = width, height
    img_array = []
    # Add all the files into the array
    for filename in glob_l:
        img_array.append(cv2.imread(filename))
    # Create the video object

    img_src_loc = img_src.split("\\")[-2]

    strftime_pattern = "%d_%m_%Y"
    file = output_dir + f"output_{img_src_loc}_{date.today().strftime(strftime_pattern)}.avi"
    out = cv2.VideoWriter(file, cv2.VideoWriter_fourcc(*'XVID'), FPS, size)
    # Add the images into the video
    for i in range(len(img_array)):
        out.write(img_array[i])
    # Create the video
    out.release()
    # TODO Add background music -> bg_music.mp3
    """
    # Add music
    import moviepy.editor as mpe
    clip = mpe.VideoFileClip(file)
    audio_bg = mpe.AudioFileClip("bg_music.mp3")
    audio_bg.set_end(clip.duration)
    finalclip = clip.set_audio(audio_bg)
    finalclip.write_videofile(f"output\\output_with_audio_{img_src_loc}_{date.today().strftime(strftime_pattern)}.mp4",
                              fps=FPS)"""
    return file


def createTL():
    flore, rivotte = "images\\flore\\", "images\\rivotte\\"
    output = "output\\"
    # Flore
    # Create the video
    flore_vid = __createVid(flore, output)
    print(f"The Flore Timelapse has been created, the file is: {flore_vid}")
    # Rivotte
    # Create the video
    rivotte_vid = __createVid(rivotte, output)
    print(f"The Rivotte Timelapse has been created, the file is: {rivotte_vid}")
    return flore_vid, rivotte_vid


if __name__ == "__main__":
    createTL()
