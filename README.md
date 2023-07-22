<h1 align="center">Youtube-Blog</h1>

<p align="center">
<!--
<a href="https://github.com/Simatwa/y2mate-api/actions/workflows/python-test.yml"><img src="https://github.com/Simatwa/y2mate-api/actions/workflows/python-test.yml/badge.svg" alt="Python Test"/></a>
-->
<a href="LICENSE"><img alt="License" src="https://img.shields.io/static/v1?logo=GPL&color=Blue&message=MIT&label=License"/></a>
<a href="https://github.com/psf/black"><img alt="Black" src="https://img.shields.io/static/v1?logo=Black&label=Code-style&message=Black"/></a>
<a href="#"><img alt="Passing" src="https://img.shields.io/static/v1?logo=Docs&label=Docs&message=Passing&color=green"/></a>
<a href="#"><img alt="coverage" src="https://img.shields.io/static/v1?logo=Coverage&label=Coverage&message=60%&color=yellowgreen"/></a>
<a href="#" alt="progress"><img alt="Progress" src="https://img.shields.io/static/v1?logo=Progress&label=Progress&message=95%&color=green"/></a>
<a href="#"><img src="https://visitor-badge.glitch.me/badge?page_id=Simatwa.youtube-blog&left_color=red&right_color=lime&left_text=Counts" alt="Visitors"/></a>
</p>

> Blogging site optimized for YouTubers

## Features

- Design for Mobile user's exclusively
- Admin endpoint for managing contents
- Markdown to HTML conversion
- Content's subscription
- Ads intergration support
- Auto SEO
- Comment Section
- Views count per article
- Likes count per article

Other minor features include

* Auto-generate Audio & Video html tags
* Live Article Search
* Social Media Intergration
* M-M Category-Blog relation
* Auto-rank trending blogs

#Technologies used
- W3CS
- W3JS
- HTML
- FLASK

# Installation and Usage
## Installation

Since the site is Flask-Based, [Python>=3.8](python.org) has to be in path.

Clone repo and install dependencies

```
git clone https://github.com/Simatwa/Youtube-Blog.git
pip install -r requirements.txt
```

## Usage

Before firing up the site, you have to setup environment variables, by editing the [env](env) file as per your preferences and finally rename the file to *.env*

Setup admin for content management

```
flask user create-admin
```
Fill the prompts and then fire up the server `flask run`

The site will be accessed at `http://localhost:5000` 

Admin endpoint will be available at `http://localhost:5000/admin`

# Further info

To insert *audio* or *video* in an article, use the format `%(file_n)s`  where **n** is the file number at upload.

To append path to an image or any other file other than video & audio, use the format `%(category_n)s` where **category** is either *file* or *image* and **n** is the media position at upload.

To insert ads to an article use the tag `{ads}` anywhere within the article. The tag can be used unlimited times to display as many ads as you had published.

> **Note** Script based tags are rendered immediate before `</body>` tag and not in the `{ads}` like the non-script ads-code.

# Disclaimer

- This is just but a micro-blog site thus might be vulnerable to a number of attacks. The developer(s) of this site will not be liable to any lose or illegal concerns arising from the commercially or personally use of this site.

# Conclusion

- To any Blogger intending to monetise the site through ads, I'd recommend using [Adsterra](https://adsterra.com).

<p align="center">Made with ❤️</p>
