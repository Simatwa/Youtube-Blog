from flask import Blueprint

app = Blueprint(
   "blogs",
   __name__,
   )
   
@app.app_template_global()
def youtube_iframe(video_id):
	return f'<iframe width="100%" height="auto" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
	
@app.app_template_global()
def len_(element):
	return len(element)