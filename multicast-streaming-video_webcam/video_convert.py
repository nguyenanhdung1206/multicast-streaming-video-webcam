import moviepy.editor as mp
clip = mp.VideoFileClip("test.mp4")
clip.audio.write_audiofile("test.wav")