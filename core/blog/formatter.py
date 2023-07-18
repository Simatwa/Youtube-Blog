from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from xml.etree.ElementTree import QName
from os import path


class VidifyTreeprocessor(Treeprocessor):
    video_extensions = [".webm", ".mp4", ".ogg", ".mkv", ".3gp"]
    audio_extensions = [".mp3", ".wav", ".aac"]

    def __init__(self, md, autoplay, controls, loop, muted):
        self.md = md
        self.autoplay = autoplay
        self.controls = controls
        self.loop = loop
        self.muted = muted

    def run(self, root):
        self.format_videos(root)
        self.format_audio(root)

    def format_videos(self, root):
        for video in root.findall(".//img"):
            if not path.splitext(video.attrib.get("src", "").lower())[1] in self.video_extensions:
            	continue	
            video.tag = "video"
            if "alt" in video.attrib.keys():
                del video.attrib["alt"]

            if self.autoplay:
                video.attrib["autoplay"] = "autoplay"
            if self.controls:
                video.attrib["controls"] = "controls"
            if self.loop:
                video.attrib["loop"] = "loop"
            if self.muted:
                video.attrib["muted"] = "muted"

    def format_audio(self, root):
        for audio in root.findall(".//img"):
            if not path.splitext(audio.attrib.get("src", "").lower())[1] in self.audio_extensions:
            	continue            
            audio.tag = "audio"
            if "alt" in audio.attrib.keys():
                del audio.attrib["alt"]
            if self.autoplay:
                audio.attrib["autoplay"] = "autoplay"
            if self.controls:
                audio.attrib["controls"] = "controls"
            if self.loop:
                audio.attrib["loop"] = "loop"
            if self.muted:
                audio.attrib["muted"] = "muted"


class VidifyExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            "autoplay": [False, "Videos should autoplay by default"],
            "controls": [False, "Videos should have controls by default"],
            "loop": [False, "Videos should loop by default"],
            "muted": [False, "Videos should be muted by default"],
        }
        super(VidifyExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md):
        md.treeprocessors.register(
            VidifyTreeprocessor(
                md,
                autoplay=self.getConfig("autoplay"),
                controls=self.getConfig("controls"),
                loop=self.getConfig("loop"),
                muted=self.getConfig("muted"),
            ),
            "vidifytreeprocessor",
            5
        )


def makeExtension(**kwargs):
    return VidifyExtension(**kwargs)

import markdown
#from markdown_vidify import VidifyExtension

md = markdown.Markdown(extensions=[VidifyExtension()])

markdown_text = """
This is a paragraph with an embedded video:

![Video](video.mp4)

And here's an embedded audio:

![Audio](audio.mp3)
"""

html = md.convert(markdown_text)
print(html)