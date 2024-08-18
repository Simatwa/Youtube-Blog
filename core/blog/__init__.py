from flask import Blueprint

app = Blueprint(
    "blogs",
    __name__,
)


@app.app_template_global()
def youtube_iframe(video_id, width=100):
    video_id = video_id.split("/")[-1]
    return f'<iframe width="{width}%" height="auto" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'


@app.app_template_global()
def len_(element):
    return len(element)


@app.app_template_global()
def str_(value):
    return str(value)


@app.app_template_global()
def enumerate_(value, start=0):
    return enumerate(value, start=0)