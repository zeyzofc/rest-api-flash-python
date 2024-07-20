from flask import (Flask, request, jsonify, redirect, url_for, make_response,
                   render_template, send_from_directory, Response, send_file,
                   render_template_string)

from youtubesearchpython import Search, PlaylistsSearch
from flask_caching import Cache
from flask_cors import CORS, cross_origin
import requests, random, time, urllib, traceback, re, urllib3, socket, html, json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from fake_useragent import UserAgent
from datetime import datetime, timedelta
import config as conf
import utils, os, threading, glob, bleach, base64
from utils import *
from markupsafe import escape
from html import escape
from email_validator import validate_email, EmailNotValidError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

#from flask_limiter import Limiter

app = Flask(__name__)
# cors = CORS(app)
#limiter = Limiter(key_func=lambda: request.headers.get("X-Real-IP", request.remote_addr), default_limits=["100 per day", "10 per hour"], headers_enabled=True, app=app)
CORS(app)

DOWNLOAD_DIR = "./downloads"


def delete_files():
  current_time = time.time()
  for file in os.listdir(DOWNLOAD_DIR):
    file_path = os.path.join(DOWNLOAD_DIR, file)
    if os.path.isfile(
        file_path) and current_time - os.path.getctime(file_path) > 1800:
      os.remove(file_path)


app.config["CORS_HEADERS"] = "Content-Type"
app.config["TEMPLATES_AUTO_RELOAD"] = conf.AUTO_RELOAD
cache = Cache(app,
              config={
                "CACHE_TYPE": "simple",
                "CACHE_DEFAULT_TIMEOUT": 3600
              })


@cache.memoize()
def get_user_agents():
  with open("user_agents.txt", "r") as f:
    return [line.strip() for line in f.readlines()]


# def generate_visitor_id():
#   timestamp = str(time.time())
#   md5_hash = hashlib.md5(timestamp.encode()).hexdigest()
#   return md5_hash

# def generate_cookie(visitor_id):
#   timestamp = str(time.time())
#   sha1_hash = hashlib.sha1((timestamp + visitor_id).encode()).hexdigest()
#   return sha1_hash

user_agent = UserAgent()

random_user_agent = user_agent.random


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
@app.errorhandler(502)
@app.errorhandler(503)
@app.errorhandler(504)
def handle_errors(error):
  return redirect(url_for("index"))


@app.route("/")
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def index():
  visitor_id = generate_visitor_id()
  cookie = generate_cookie(visitor_id)
  # Mendapatkan tanggal saat ini
  current_date = datetime.now()

  # Menghitung tanggal kadaluwarsa (7 hari dari tanggal saat ini)
  expiration_date = current_date + timedelta(days=7)

  response = make_response(render_template("index.jinja2", configs=conf))
  response.set_cookie(visitor_id,
                      value=cookie,
                      httponly=True,
                      expires=expiration_date,
                      samesite="None",
                      secure=True)
  return response


@app.route("/robots.txt")
def robots_txt():
  return '''User-agent: *<br />Disallow: <br /><br />Sitemap: https://0e87ad76-6c4e-40ff-bb5a-6bbdab145ae2-00-39qk1kw7vab6l.worf.replit.dev/sitemap.xml
'''


@app.route('/apk/<filename>', methods=['GET'])
def download_apk(filename):
  # Replace 'path_to_apk_folder' with the actual path to the folder containing the APK file
  apk_folder = 'apk'
  file_path = f'{apk_folder}/{filename}'

  try:
    return send_file(file_path, as_attachment=True)
  except Exception as e:
    return str(e), 404


@app.route('/images')
def get_image():
  image_path = 'dana/dana.webp'  # Replace 'data/dana.jpg' with the actual path to your image file
  return send_file(image_path, mimetype='image/jpeg')


# @app.route('/sitemap.xml')
# def generate_sitemap():
# sitemap_content = generate_sitemap_content()

# response = Response(sitemap_content, mimetype='text/xml')
# response.headers['Content-Disposition'] = 'attachment; filename=sitemap.xml'
# return response


def generate_sitemap_content():
  xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset
      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
<!-- created with Free Online Sitemap Generator www.xml-sitemaps.com -->


<url>
  <loc>https://0e87ad76-6c4e-40ff-bb5a-6bbdab145ae2-00-39qk1kw7vab6l.worf.replit.dev/</loc>
  <lastmod>2024-01-04T05:53:27+00:00</lastmod>
  <priority>1.00</priority>
</url>
<url>
  <loc>https://0e87ad76-6c4e-40ff-bb5a-6bbdab145ae2-00-39qk1kw7vab6l.worf.replit.dev/ringkas</loc>
  <lastmod>2024-01-04T05:53:27+00:00</lastmod>
  <priority>0.80</priority>
</url>
<url>
  <loc>https://0e87ad76-6c4e-40ff-bb5a-6bbdab145ae2-00-39qk1kw7vab6l.worf.replit.dev/zerogpt</loc>
  <lastmod>2024-01-04T05:53:27+00:00</lastmod>
  <priority>0.80</priority>
</url>


</urlset>

  '''
  # xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
  # xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
  # xml_content += '    <url>\n'
  # xml_content += '        <loc>https://tr.deployers.repl.co</loc>\n'
  # xml_content += f'        <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
  # xml_content += '        <changefreq>weekly</changefreq>\n'
  # xml_content += '        <priority>1.0</priority>\n'  # Set priority to 1.0 for high
  # xml_content += '    </url>\n'
  # xml_content += '</urlset>'

  return xml_content


@app.route('/sitemap.xml')
def generate_sitemap():
  xml_content = generate_sitemap_content()
  response = Response(xml_content, content_type='application/xml')
  return response


@app.route('/donasi')
def donasi():
  return '''
<!doctype html>
<html lang=en>
<head>
<script>document.write(unescape("%3C%6D%65%74%61%20%63%68%61%72%73%65%74%3D%55%54%46%2D%38%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%76%69%65%77%70%6F%72%74%20%63%6F%6E%74%65%6E%74%3D%22%77%69%64%74%68%3D%64%65%76%69%63%65%2D%77%69%64%74%68%2C%69%6E%69%74%69%61%6C%2D%73%63%61%6C%65%3D%31%22%3E%0A%3C%74%69%74%6C%65%3E%44%6F%6E%61%73%69%20%75%6E%74%75%6B%20%50%72%6F%67%72%61%6D%6D%65%72%3C%2F%74%69%74%6C%65%3E%0A%3C%73%63%72%69%70%74%20%73%72%63%3D%68%74%74%70%73%3A%2F%2F%63%64%6E%2E%6A%73%64%65%6C%69%76%72%2E%6E%65%74%2F%6E%70%6D%2F%73%77%65%65%74%61%6C%65%72%74%32%40%31%31%3E%3C%2F%73%63%72%69%70%74%3E%0A%3C%6C%69%6E%6B%20%72%65%6C%3D%69%63%6F%6E%20%68%72%65%66%3D%68%74%74%70%73%3A%2F%2F%69%2E%69%62%62%2E%63%6F%2F%68%46%78%57%54%31%70%2F%65%7A%67%69%66%2D%32%2D%66%38%36%36%63%66%34%35%30%39%2E%77%65%62%70%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%74%69%74%6C%65%20%63%6F%6E%74%65%6E%74%3D%44%6F%6E%61%73%69%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%64%65%73%63%72%69%70%74%69%6F%6E%20%63%6F%6E%74%65%6E%74%3D%22%42%65%72%6B%6F%6E%74%72%69%62%75%73%69%20%64%65%6E%67%61%6E%20%64%6F%6E%61%73%69%20%75%6E%74%75%6B%20%70%65%6D%69%6C%69%6B%20%73%65%72%76%65%72%20%61%74%61%75%20%77%65%62%73%69%74%65%20%74%72%2E%64%65%70%6C%6F%79%65%72%2E%72%65%70%6C%2E%63%6F%20%79%61%6E%67%20%6D%65%6D%62%65%72%69%6B%61%6E%20%41%50%49%20%67%72%61%74%69%73%2C%20%6B%75%6E%6A%75%6E%67%69%20%68%61%6C%61%6D%61%6E%20%69%6E%69%20%73%65%6B%61%72%61%6E%67%2E%22%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%6B%65%79%77%6F%72%64%73%20%63%6F%6E%74%65%6E%74%3D%22%64%6F%6E%61%73%69%2C%61%70%69%2C%64%65%76%65%6C%6F%70%65%72%2C%70%72%6F%67%72%61%6D%6D%69%6E%67%2C%70%72%6F%67%72%61%6D%6D%65%72%2C%67%69%74%68%75%62%2C%6F%70%65%6E%73%6F%75%72%63%65%2C%6F%70%65%6E%20%73%6F%75%72%63%65%2C%73%65%6F%22%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%72%6F%62%6F%74%73%20%63%6F%6E%74%65%6E%74%3D%22%69%6E%64%65%78%2C%20%66%6F%6C%6C%6F%77%22%3E%0A%3C%6D%65%74%61%20%68%74%74%70%2D%65%71%75%69%76%3D%43%6F%6E%74%65%6E%74%2D%54%79%70%65%20%63%6F%6E%74%65%6E%74%3D%22%74%65%78%74%2F%68%74%6D%6C%3B%20%63%68%61%72%73%65%74%3D%75%74%66%2D%38%22%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%6C%61%6E%67%75%61%67%65%20%63%6F%6E%74%65%6E%74%3D%45%6E%67%6C%69%73%68%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%61%75%74%68%6F%72%20%63%6F%6E%74%65%6E%74%3D%58%6E%75%76%65%72%73%30%30%37%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%6F%67%3A%74%79%70%65%20%63%6F%6E%74%65%6E%74%3D%77%65%62%73%69%74%65%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%6F%67%3A%75%72%6C%20%63%6F%6E%74%65%6E%74%3D%68%74%74%70%73%3A%2F%2F%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%2F%64%6F%6E%61%73%69%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%6F%67%3A%74%69%74%6C%65%20%63%6F%6E%74%65%6E%74%3D%44%6F%6E%61%73%69%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%6F%67%3A%64%65%73%63%72%69%70%74%69%6F%6E%20%63%6F%6E%74%65%6E%74%3D%22%42%65%72%6B%6F%6E%74%72%69%62%75%73%69%20%64%65%6E%67%61%6E%20%64%6F%6E%61%73%69%20%75%6E%74%75%6B%20%70%65%6D%69%6C%69%6B%20%73%65%72%76%65%72%20%61%74%61%75%20%77%65%62%73%69%74%65%20%74%72%2E%64%65%70%6C%6F%79%65%72%2E%72%65%70%6C%2E%63%6F%20%79%61%6E%67%20%6D%65%6D%62%65%72%69%6B%61%6E%20%41%50%49%20%67%72%61%74%69%73%2C%20%6B%75%6E%6A%75%6E%67%69%20%68%61%6C%61%6D%61%6E%20%69%6E%69%20%73%65%6B%61%72%61%6E%67%2E%22%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%6F%67%3A%69%6D%61%67%65%20%63%6F%6E%74%65%6E%74%3D%68%74%74%70%73%3A%2F%2F%69%2E%69%62%62%2E%63%6F%2F%68%46%78%57%54%31%70%2F%65%7A%67%69%66%2D%32%2D%66%38%36%36%63%66%34%35%30%39%2E%77%65%62%70%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%74%77%69%74%74%65%72%3A%63%61%72%64%20%63%6F%6E%74%65%6E%74%3D%73%75%6D%6D%61%72%79%5F%6C%61%72%67%65%5F%69%6D%61%67%65%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%74%77%69%74%74%65%72%3A%75%72%6C%20%63%6F%6E%74%65%6E%74%3D%68%74%74%70%73%3A%2F%2F%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%2F%64%6F%6E%61%73%69%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%74%77%69%74%74%65%72%3A%74%69%74%6C%65%20%63%6F%6E%74%65%6E%74%3D%44%6F%6E%61%73%69%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%74%77%69%74%74%65%72%3A%64%65%73%63%72%69%70%74%69%6F%6E%20%63%6F%6E%74%65%6E%74%3D%22%42%65%72%6B%6F%6E%74%72%69%62%75%73%69%20%64%65%6E%67%61%6E%20%64%6F%6E%61%73%69%20%75%6E%74%75%6B%20%70%65%6D%69%6C%69%6B%20%73%65%72%76%65%72%20%61%74%61%75%20%77%65%62%73%69%74%65%20%74%72%2E%64%65%70%6C%6F%79%65%72%2E%72%65%70%6C%2E%63%6F%20%79%61%6E%67%20%6D%65%6D%62%65%72%69%6B%61%6E%20%41%50%49%20%67%72%61%74%69%73%2C%20%6B%75%6E%6A%75%6E%67%69%20%68%61%6C%61%6D%61%6E%20%69%6E%69%20%73%65%6B%61%72%61%6E%67%2E%22%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%74%77%69%74%74%65%72%3A%69%6D%61%67%65%20%63%6F%6E%74%65%6E%74%3D%68%74%74%70%73%3A%2F%2F%69%2E%69%62%62%2E%63%6F%2F%68%46%78%57%54%31%70%2F%65%7A%67%69%66%2D%32%2D%66%38%36%36%63%66%34%35%30%39%2E%77%65%62%70%3E%0A%3C%73%74%79%6C%65%3E%62%6F%64%79%7B%66%6F%6E%74%2D%66%61%6D%69%6C%79%3A%41%72%69%61%6C%2C%73%61%6E%73%2D%73%65%72%69%66%3B%6D%61%72%67%69%6E%3A%30%3B%70%61%64%64%69%6E%67%3A%30%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%37%66%37%66%37%7D%2E%63%6F%6E%74%61%69%6E%65%72%7B%6D%61%78%2D%77%69%64%74%68%3A%36%30%30%70%78%3B%6D%61%72%67%69%6E%3A%35%30%70%78%20%61%75%74%6F%3B%70%61%64%64%69%6E%67%3A%32%30%70%78%3B%62%6F%72%64%65%72%3A%31%70%78%20%73%6F%6C%69%64%20%23%63%63%63%3B%62%6F%72%64%65%72%2D%72%61%64%69%75%73%3A%35%70%78%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%66%66%7D%2E%6C%6F%67%6F%2D%77%72%61%70%70%65%72%7B%64%69%73%70%6C%61%79%3A%66%6C%65%78%3B%66%6C%65%78%2D%64%69%72%65%63%74%69%6F%6E%3A%63%6F%6C%75%6D%6E%3B%61%6C%69%67%6E%2D%69%74%65%6D%73%3A%63%65%6E%74%65%72%3B%6D%61%72%67%69%6E%2D%62%6F%74%74%6F%6D%3A%32%30%70%78%7D%2E%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%7B%70%6F%73%69%74%69%6F%6E%3A%72%65%6C%61%74%69%76%65%3B%77%69%64%74%68%3A%32%30%30%70%78%3B%68%65%69%67%68%74%3A%32%30%30%70%78%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%30%66%30%66%30%3B%62%6F%72%64%65%72%2D%72%61%64%69%75%73%3A%35%30%25%3B%6F%76%65%72%66%6C%6F%77%3A%68%69%64%64%65%6E%3B%63%75%72%73%6F%72%3A%70%6F%69%6E%74%65%72%7D%2E%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%20%69%6D%67%7B%77%69%64%74%68%3A%31%30%30%25%3B%68%65%69%67%68%74%3A%31%30%30%25%3B%6F%62%6A%65%63%74%2D%66%69%74%3A%63%6F%76%65%72%7D%2E%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%32%7B%70%6F%73%69%74%69%6F%6E%3A%72%65%6C%61%74%69%76%65%3B%77%69%64%74%68%3A%32%30%30%70%78%3B%68%65%69%67%68%74%3A%32%30%30%70%78%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%30%66%30%66%30%3B%6F%76%65%72%66%6C%6F%77%3A%68%69%64%64%65%6E%3B%63%75%72%73%6F%72%3A%70%6F%69%6E%74%65%72%7D%2E%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%32%20%69%6D%67%7B%77%69%64%74%68%3A%31%30%30%25%3B%68%65%69%67%68%74%3A%31%30%30%25%3B%6F%62%6A%65%63%74%2D%66%69%74%3A%63%6F%76%65%72%7D%2E%68%69%64%64%65%6E%2D%6C%69%6E%6B%7B%70%6F%73%69%74%69%6F%6E%3A%61%62%73%6F%6C%75%74%65%3B%74%6F%70%3A%30%3B%6C%65%66%74%3A%30%3B%77%69%64%74%68%3A%31%30%30%25%3B%68%65%69%67%68%74%3A%31%30%30%25%3B%70%6F%69%6E%74%65%72%2D%65%76%65%6E%74%73%3A%6E%6F%6E%65%7D%2E%74%69%74%6C%65%7B%66%6F%6E%74%2D%73%69%7A%65%3A%32%34%70%78%3B%66%6F%6E%74%2D%77%65%69%67%68%74%3A%37%30%30%3B%63%6F%6C%6F%72%3A%23%33%33%33%3B%6D%61%72%67%69%6E%2D%74%6F%70%3A%31%30%70%78%7D%2E%66%6F%6F%74%65%72%7B%74%65%78%74%2D%61%6C%69%67%6E%3A%63%65%6E%74%65%72%3B%66%6F%6E%74%2D%73%69%7A%65%3A%32%30%70%78%3B%63%6F%6C%6F%72%3A%23%30%30%30%3B%6D%61%72%67%69%6E%2D%62%6F%74%74%6F%6D%3A%31%30%70%78%7D%2A%7B%2D%77%65%62%6B%69%74%2D%74%6F%75%63%68%2D%63%61%6C%6C%6F%75%74%3A%6E%6F%6E%65%3B%2D%77%65%62%6B%69%74%2D%75%73%65%72%2D%73%65%6C%65%63%74%3A%6E%6F%6E%65%3B%2D%6B%68%74%6D%6C%2D%75%73%65%72%2D%73%65%6C%65%63%74%3A%6E%6F%6E%65%3B%2D%6D%6F%7A%2D%75%73%65%72%2D%73%65%6C%65%63%74%3A%6E%6F%6E%65%3B%2D%6D%73%2D%75%73%65%72%2D%73%65%6C%65%63%74%3A%6E%6F%6E%65%3B%75%73%65%72%2D%73%65%6C%65%63%74%3A%6E%6F%6E%65%7D%3C%2F%73%74%79%6C%65%3E"))</script>
</head>
<body>
<script>document.write(unescape("%3C%64%69%76%20%63%6C%61%73%73%3D%63%6F%6E%74%61%69%6E%65%72%3E%0A%3C%68%31%20%73%74%79%6C%65%3D%74%65%78%74%2D%61%6C%69%67%6E%3A%63%65%6E%74%65%72%3E%44%6F%6E%61%73%69%20%75%6E%74%75%6B%20%53%61%79%61%3C%2F%68%31%3E%0A%3C%70%3E%54%65%72%69%6D%61%20%6B%61%73%69%68%20%74%65%6C%61%68%20%6D%65%6E%67%67%75%6E%61%6B%61%6E%20%77%65%62%73%69%74%65%20%41%50%49%20%6B%61%6D%69%2E%20%4A%69%6B%61%20%41%6E%64%61%20%6D%65%72%61%73%61%20%74%65%72%62%61%6E%74%75%2C%20%41%6E%64%61%20%64%61%70%61%74%20%6D%65%6D%62%65%72%69%6B%61%6E%20%64%6F%6E%61%73%69%20%73%65%62%61%67%61%69%20%64%75%6B%75%6E%67%61%6E%2E%3C%2F%70%3E%0A%3C%70%3E%44%6F%6E%61%73%69%20%41%6E%64%61%20%61%6B%61%6E%20%6D%65%6D%62%61%6E%74%75%20%6B%61%6D%69%20%75%6E%74%75%6B%20%74%65%72%75%73%20%6D%65%6E%69%6E%67%6B%61%74%6B%61%6E%20%6C%61%79%61%6E%61%6E%20%6B%61%6D%69%2E%20%54%65%6B%61%6E%20%67%61%6D%62%61%72%20%61%67%61%72%20%6D%65%6E%75%6A%75%20%6B%65%20%70%65%6D%62%61%79%61%72%61%6E%20%28%4B%65%63%75%61%6C%69%20%44%61%6E%61%29%3C%2F%70%3E%3C%62%72%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%77%72%61%70%70%65%72%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%74%69%74%6C%65%3E%53%61%77%65%72%69%61%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%20%6F%6E%63%6C%69%63%6B%3D%72%65%64%69%72%65%63%74%54%6F%44%6F%6E%61%74%69%6F%6E%50%61%67%65%31%28%29%3E%0A%3C%69%6D%67%20%73%72%63%3D%68%74%74%70%73%3A%2F%2F%69%2E%69%62%62%2E%63%6F%2F%68%46%78%57%54%31%70%2F%65%7A%67%69%66%2D%32%2D%66%38%36%36%63%66%34%35%30%39%2E%77%65%62%70%20%61%6C%74%3D%22%4C%6F%67%6F%20%50%65%6D%62%61%79%61%72%61%6E%20%53%61%77%65%72%69%61%22%3E%0A%3C%61%20%63%6C%61%73%73%3D%68%69%64%64%65%6E%2D%6C%69%6E%6B%3E%3C%2F%61%3E%0A%3C%2F%64%69%76%3E%0A%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%77%72%61%70%70%65%72%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%74%69%74%6C%65%3E%44%61%6E%61%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%32%3E%0A%3C%69%6D%67%20%73%72%63%3D%68%74%74%70%73%3A%2F%2F%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%2F%69%6D%61%67%65%73%20%61%6C%74%3D%22%4C%6F%67%6F%20%50%65%6D%62%61%79%61%72%61%6E%20%44%61%6E%61%22%3E%0A%3C%2F%64%69%76%3E%0A%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%77%72%61%70%70%65%72%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%74%69%74%6C%65%3E%54%72%61%6B%74%65%65%72%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%20%6F%6E%63%6C%69%63%6B%3D%72%65%64%69%72%65%63%74%54%6F%44%6F%6E%61%74%69%6F%6E%50%61%67%65%32%28%29%3E%0A%3C%69%6D%67%20%73%72%63%3D%68%74%74%70%73%3A%2F%2F%69%2E%69%62%62%2E%63%6F%2F%53%66%4B%53%4E%4E%73%2F%65%7A%67%69%66%2D%32%2D%62%39%64%32%61%32%39%65%65%65%2E%77%65%62%70%20%61%6C%74%3D%22%4C%6F%67%6F%20%50%65%6D%62%61%79%61%72%61%6E%20%54%72%61%6B%74%65%65%72%22%3E%0A%3C%61%20%63%6C%61%73%73%3D%68%69%64%64%65%6E%2D%6C%69%6E%6B%3E%3C%2F%61%3E%0A%3C%2F%64%69%76%3E%0A%3C%2F%64%69%76%3E%0A%3C%62%72%3E%0A%3C%70%20%73%74%79%6C%65%3D%74%65%78%74%2D%61%6C%69%67%6E%3A%63%65%6E%74%65%72%3B%66%6F%6E%74%2D%77%65%69%67%68%74%3A%62%6F%6C%64%65%72%3B%66%6F%6E%74%2D%73%69%7A%65%3A%31%37%70%78%3E%54%45%52%49%4D%41%4B%41%53%49%48%20%61%74%61%73%20%73%65%62%65%73%61%72%20%62%65%73%61%72%6E%79%61%20%64%61%72%69%20%64%6F%6E%61%73%69%20%79%61%6E%67%20%61%6E%64%61%20%62%65%72%69%6B%61%6E%2C%20%62%65%73%61%72%20%61%74%61%75%20%6B%65%63%69%6C%2E%20%74%65%74%61%70%20%62%65%72%68%61%72%67%61%20%64%69%6D%61%74%61%20%73%61%79%61%2E%20%53%65%6B%61%6C%69%20%6C%61%67%69%2C%20%54%45%52%49%4D%41%4B%41%53%49%48%20%3C%2F%70%3E%0A%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%66%6F%6F%74%65%72%20%73%74%79%6C%65%3D%66%6F%6E%74%2D%77%65%69%67%68%74%3A%62%6F%6C%64%65%72%3E%0A%26%63%6F%70%79%3B%20%32%30%32%33%20%58%6E%75%76%65%72%73%30%30%37%20%41%50%49%20%28%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%29%2E%20%41%6C%6C%20%72%69%67%68%74%73%20%72%65%73%65%72%76%65%64%2E%0A%3C%2F%64%69%76%3E%0A%3C%73%63%72%69%70%74%3E%66%75%6E%63%74%69%6F%6E%20%72%65%64%69%72%65%63%74%54%6F%44%6F%6E%61%74%69%6F%6E%50%61%67%65%31%28%29%7B%76%61%72%20%65%3D%61%74%6F%62%28%22%61%48%52%30%63%48%4D%36%4C%79%39%7A%59%58%64%6C%63%6D%6C%68%4C%6D%4E%76%4C%33%68%75%64%58%5A%6C%63%6E%4D%77%4D%44%63%22%29%3B%77%69%6E%64%6F%77%2E%6F%70%65%6E%28%65%2C%22%5F%62%6C%61%6E%6B%22%2C%22%6E%6F%6F%70%65%6E%65%72%2C%6E%6F%72%65%66%65%72%72%65%72%22%29%7D%66%75%6E%63%74%69%6F%6E%20%72%65%64%69%72%65%63%74%54%6F%44%6F%6E%61%74%69%6F%6E%50%61%67%65%32%28%29%7B%76%61%72%20%65%3D%61%74%6F%62%28%22%61%48%52%30%63%48%4D%36%4C%79%39%30%63%6D%46%72%64%47%56%6C%63%69%35%70%5A%43%39%34%62%6E%56%32%5A%58%4A%7A%4D%44%41%33%22%29%3B%77%69%6E%64%6F%77%2E%6F%70%65%6E%28%65%2C%22%5F%62%6C%61%6E%6B%22%2C%22%6E%6F%6F%70%65%6E%65%72%2C%6E%6F%72%65%66%65%72%72%65%72%22%29%7D%66%75%6E%63%74%69%6F%6E%20%73%68%6F%77%45%72%72%6F%72%28%29%7B%53%77%61%6C%2E%66%69%72%65%28%7B%69%63%6F%6E%3A%22%65%72%72%6F%72%22%2C%74%69%74%6C%65%3A%22%4F%6F%70%73%2E%2E%2E%22%2C%74%65%78%74%3A%22%43%6C%69%63%6B%69%6E%67%20%6F%6E%20%74%68%65%20%6C%6F%67%6F%20%69%73%20%64%69%73%61%62%6C%65%64%20%66%6F%72%20%73%65%63%75%72%69%74%79%20%72%65%61%73%6F%6E%73%2F%52%69%67%68%74%20%43%6C%69%63%6B%20%64%69%73%61%62%6C%65%64%2E%20%50%6C%65%61%73%65%20%75%73%65%20%74%68%65%20%70%72%6F%76%69%64%65%64%20%6C%69%6E%6B%20%74%6F%20%6D%61%6B%65%20%61%20%64%6F%6E%61%74%69%6F%6E%2E%20%54%65%72%69%6D%61%20%6B%61%73%69%68%20%61%74%61%73%20%64%75%6B%75%6E%67%61%6E%6E%79%61%21%22%2C%66%6F%6F%74%65%72%3A%27%3C%61%20%68%72%65%66%3D%22%2F%22%3E%47%6F%20%54%6F%20%49%6E%64%65%78%3C%2F%61%3E%27%7D%29%7D%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%63%6F%6E%74%65%78%74%6D%65%6E%75%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%2C%73%68%6F%77%45%72%72%6F%72%28%29%7D%29%29%3C%2F%73%63%72%69%70%74%3E"))</script>
</body>
</html>
'''


@app.route('/downloadapk')
def aplikasi():
  return '''<!doctype html><html lang=en><head><title>Download APK</title><script>document.write(unescape("%3C%6D%65%74%61%20%63%68%61%72%73%65%74%3D%55%54%46%2D%38%3E%3C%6D%65%74%61%20%6E%61%6D%65%3D%76%69%65%77%70%6F%72%74%20%63%6F%6E%74%65%6E%74%3D%22%77%69%64%74%68%3D%64%65%76%69%63%65%2D%77%69%64%74%68%2C%69%6E%69%74%69%61%6C%2D%73%63%61%6C%65%3D%31%22%3E%3C%73%74%79%6C%65%3E%62%6F%64%79%7B%66%6F%6E%74%2D%66%61%6D%69%6C%79%3A%41%72%69%61%6C%2C%73%61%6E%73%2D%73%65%72%69%66%3B%64%69%73%70%6C%61%79%3A%66%6C%65%78%3B%6A%75%73%74%69%66%79%2D%63%6F%6E%74%65%6E%74%3A%63%65%6E%74%65%72%3B%61%6C%69%67%6E%2D%69%74%65%6D%73%3A%63%65%6E%74%65%72%3B%68%65%69%67%68%74%3A%31%30%30%76%68%3B%6D%61%72%67%69%6E%3A%30%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%34%66%34%66%34%7D%2E%63%6F%6E%74%61%69%6E%65%72%7B%74%65%78%74%2D%61%6C%69%67%6E%3A%63%65%6E%74%65%72%3B%62%6F%72%64%65%72%3A%32%70%78%20%73%6F%6C%69%64%20%23%63%63%63%3B%70%61%64%64%69%6E%67%3A%32%30%70%78%3B%62%6F%72%64%65%72%2D%72%61%64%69%75%73%3A%31%30%70%78%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%66%66%3B%62%6F%78%2D%73%68%61%64%6F%77%3A%30%20%30%20%31%30%70%78%20%72%67%62%61%28%30%2C%30%2C%30%2C%2E%31%29%7D%2E%64%6F%77%6E%6C%6F%61%64%2D%62%74%6E%7B%64%69%73%70%6C%61%79%3A%69%6E%6C%69%6E%65%2D%62%6C%6F%63%6B%3B%70%61%64%64%69%6E%67%3A%31%30%70%78%20%32%30%70%78%3B%66%6F%6E%74%2D%73%69%7A%65%3A%31%38%70%78%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%30%30%37%62%66%66%3B%63%6F%6C%6F%72%3A%23%66%66%66%3B%62%6F%72%64%65%72%3A%6E%6F%6E%65%3B%62%6F%72%64%65%72%2D%72%61%64%69%75%73%3A%35%70%78%3B%63%75%72%73%6F%72%3A%70%6F%69%6E%74%65%72%3B%74%72%61%6E%73%69%74%69%6F%6E%3A%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%20%2E%33%73%2C%74%72%61%6E%73%66%6F%72%6D%20%2E%33%73%7D%2E%64%6F%77%6E%6C%6F%61%64%2D%62%74%6E%3A%68%6F%76%65%72%7B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%30%30%35%36%62%33%7D%2E%64%6F%77%6E%6C%6F%61%64%2D%62%74%6E%2E%61%6E%69%6D%61%74%65%7B%74%72%61%6E%73%66%6F%72%6D%3A%73%63%61%6C%65%28%31%2E%31%29%7D%2E%73%65%72%76%65%72%2D%73%65%6C%65%63%74%69%6F%6E%7B%6D%61%72%67%69%6E%2D%74%6F%70%3A%32%30%70%78%7D%3C%2F%73%74%79%6C%65%3E"))</script></head><body><script>document.write(unescape("%3C%64%69%76%20%63%6C%61%73%73%3D%63%6F%6E%74%61%69%6E%65%72%3E%3C%68%31%3E%55%6E%64%75%68%20%41%70%6C%69%6B%61%73%69%20%4B%61%6D%69%3C%2F%68%31%3E%3C%70%3E%50%69%6C%69%68%20%73%65%72%76%65%72%20%75%6E%64%75%68%61%6E%3A%3C%2F%70%3E%3C%64%69%76%20%63%6C%61%73%73%3D%73%65%72%76%65%72%2D%73%65%6C%65%63%74%69%6F%6E%3E%3C%62%75%74%74%6F%6E%20%63%6C%61%73%73%3D%64%6F%77%6E%6C%6F%61%64%2D%62%74%6E%20%6F%6E%63%6C%69%63%6B%3D%27%64%6F%77%6E%6C%6F%61%64%41%70%70%28%22%73%65%72%76%65%72%31%22%29%27%3E%53%65%72%76%65%72%20%31%3C%2F%62%75%74%74%6F%6E%3E%20%20%20%20%26%6E%62%73%70%3B%26%6E%62%73%70%3B%26%6E%62%73%70%3B%3C%62%75%74%74%6F%6E%20%63%6C%61%73%73%3D%64%6F%77%6E%6C%6F%61%64%2D%62%74%6E%20%6F%6E%63%6C%69%63%6B%3D%27%64%6F%77%6E%6C%6F%61%64%41%70%70%28%22%73%65%72%76%65%72%32%22%29%27%3E%53%65%72%76%65%72%20%32%3C%2F%62%75%74%74%6F%6E%3E%3C%2F%64%69%76%3E%3C%2F%64%69%76%3E%3C%73%63%72%69%70%74%3E%66%75%6E%63%74%69%6F%6E%20%61%6E%69%6D%61%74%65%42%75%74%74%6F%6E%28%65%29%7B%65%2E%63%6C%61%73%73%4C%69%73%74%2E%61%64%64%28%22%61%6E%69%6D%61%74%65%22%29%2C%73%65%74%54%69%6D%65%6F%75%74%28%28%28%29%3D%3E%7B%65%2E%63%6C%61%73%73%4C%69%73%74%2E%72%65%6D%6F%76%65%28%22%61%6E%69%6D%61%74%65%22%29%7D%29%2C%33%30%30%29%7D%66%75%6E%63%74%69%6F%6E%20%64%6F%77%6E%6C%6F%61%64%41%70%70%28%65%29%7B%6C%65%74%20%74%3B%61%6E%69%6D%61%74%65%42%75%74%74%6F%6E%28%65%76%65%6E%74%2E%74%61%72%67%65%74%29%2C%22%73%65%72%76%65%72%31%22%3D%3D%3D%65%3F%74%3D%22%68%74%74%70%73%3A%2F%2F%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%2F%61%70%6B%2F%41%50%49%25%32%30%58%6E%75%76%65%72%73%30%30%37%2D%31%2E%61%70%6B%22%3A%22%73%65%72%76%65%72%32%22%3D%3D%3D%65%26%26%28%74%3D%22%68%74%74%70%73%3A%2F%2F%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%2F%61%70%6B%2F%41%50%49%25%32%30%58%6E%75%76%65%72%73%30%30%37%2D%32%2E%61%70%6B%22%29%2C%77%69%6E%64%6F%77%2E%6F%70%65%6E%28%74%2C%22%5F%62%6C%61%6E%6B%22%29%7D%3C%2F%73%63%72%69%70%74%3E"))</script><script>document.write(unescape("%3C%73%63%72%69%70%74%3E%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%6B%65%79%64%6F%77%6E%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%63%74%72%6C%4B%65%79%26%26%22%75%22%3D%3D%3D%65%2E%6B%65%79%26%26%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%63%6F%6E%74%65%78%74%6D%65%6E%75%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%73%65%6C%65%63%74%73%74%61%72%74%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%64%72%61%67%73%74%61%72%74%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%63%75%74%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%63%6F%70%79%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%70%61%73%74%65%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%3C%2F%73%63%72%69%70%74%3E"))</script></body></html>'''


@app.route("/indonesia", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_berita():
  num_articles = int(request.args.get(
    "berita",
    "5"))  # Get the 'j' query parameter from the URL, defaulting to 5
  url = "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRE55ZVc0U0FtbGtLQUFQAQ?hl=id&gl=ID&ceid=ID%3Aid"
  r = requests.get(url,
                   timeout=5,
                   headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac"})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all("c-wiz", attrs={"class": "PIlOad"})
  titles = []
  links = []
  images = []
  for item in test:
    for img in item.find_all("figure", attrs={"class": "K0q4G P22Vib"}):
      images.append(img.find("img")["src"])
    for teks in item.find_all("h4", attrs={"class": "gPFEn"}):
      titles.append(teks.text)
    for link in item.find_all("a"):
      href = link.get("href")
      absolute_url = urljoin("https://news.google.com/", href)
      if "/stories/" not in absolute_url:
        links.append(absolute_url)
  berita_list = []
  for title, link, gambar in zip(titles, links, images):
    berita_list.append({
      "Berita": title,
      "Gambar": gambar,
      "Link Berita": link
    })
    if len(berita_list) == num_articles:
      break
  return jsonify(berita_list)


@app.route("/world", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_berita_world():
  num_articles = int(request.args.get(
    "news", "5"))  # Get the 'j' query parameter from the URL, defaulting to 5
  url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtbGtHZ0pKUkNnQVAB?hl=id&gl=ID&ceid=ID:id"
  r = requests.get(url,
                   timeout=5,
                   headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac"})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all("c-wiz", attrs={"class": "PIlOad"})
  titles = []
  links = []
  images = []
  for item in test:
    for img in item.find_all("figure", attrs={"class": "K0q4G P22Vib"}):
      images.append(img.find("img")["src"])
    for teks in item.find_all("h4", attrs={"class": "gPFEn"}):
      titles.append(teks.text)
    for link in item.find_all("a"):
      href = link.get("href")
      absolute_url = urljoin("https://news.google.com/", href)
      if "/stories/" not in absolute_url:
        links.append(absolute_url)
  berita_list = []
  for title, link, gambar in zip(titles, links, images):
    berita_list.append({"News": title, "Image": gambar, "Link News": link})
    if len(berita_list) == num_articles:
      break
  return jsonify(berita_list)


@app.route("/jam", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_jam():
  wilayah = request.args.get(
    "wilayah", "Jakarta"
  )  # Get the 'wilayah' query parameter from the URL, defaulting to 'Jakarta'
  url = "https://time.is/id/" + wilayah
  r = requests.get(url,
                   timeout=5,
                   headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac"})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all("div", attrs={"id": "clock0_bg"})
  for jams in test:
    jam = jams.find("time", attrs={"id": "clock"}).text
  return jsonify({
    "Jam": jam,
    "wilayah": wilayah,
    "Author": "Xnuvers007 [ https://github.com/Xnuvers007 ]",
  })


@app.route("/bp", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_bp():
  tensi = int(request.args.get("tensi", "125"))
  hb = int(request.args.get("hb", "91"))
  url = "https://foenix.com/BP/is-{0}/{1}-good-blood-pressure-or-high-blood-pressure.html".format(
    tensi, hb)
  r = requests.get(url,
                   timeout=5,
                   headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac"})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all("div", attrs={"class": "content"})
  for hasil in test:
    hasil = soup.find_all("b")[15].text

  myhost = f"{request.host_url}bp?tensi={tensi}&hb={hb}"
  return jsonify({
    "Hasil": hasil,
    "Tensi": tensi,
    "Hb": hb,
    "Author": "Xnuvers007 [ Xnuvers007 https://github.com/Xnuvers007 ]",
    "parameter": myhost,
  })


@app.route("/convertuang", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_convertuang():
  uang = int(request.args.get("uang", "1"))
  dari = request.args.get("dari", "IDR")
  ke = request.args.get("ke", "USD")
  url = "https://www.exchange-rates.com/id/{0}/{1}/{2}/".format(uang, dari, ke)
  r = requests.get(url,
                   timeout=5,
                   headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac"})
  soup = BeautifulSoup(r.content, "html.parser")
  hasil = None
  for i in soup.find_all("div", class_="fullwidth"):
    for j in i.find_all("div", class_="leftdiv"):
      hasil = j.find_all("p")[2]
      hasil = hasil.text
  return jsonify({
    "Hasil": hasil,
    "Uang": uang,
    "Dari": dari,
    "Ke": ke,
    "Author": "Xnuvers007 [ https://github.com/Xnuvers007 ]",
  })


@app.route("/kamus", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_data():
  user_input = request.args.get("text") or request.args.get("t")
  User_agent = UserAgent(browsers=["edge", "chrome", "firefox"])
  headers = {"User-Agent": User_agent.random}

  url = f"https://en.bab.la/dictionary/english-indonesian/{user_input}"
  url2 = f"https://www.oxfordlearnersdictionaries.com/definition/english/{user_input}"
  response = requests.get(url, headers=headers)
  response2 = requests.get(url2, headers=headers)

  soup = BeautifulSoup(response.text, "html.parser")
  soup2 = BeautifulSoup(response2.text, "html.parser")

  words = []
  translations = []
  examples = []
  synonyms = []
  sentences = []
  mp3 = []

  # get mp3 urls
  mp3uk1 = soup2.find("div",
                      {"class": "sound audio_play_button pron-uk icon-audio"})
  mp3uk1 = mp3uk1.get("data-src-mp3") if mp3uk1 else "Data Tidak Ditemukan"

  mp3us1 = soup2.find("div",
                      {"class": "sound audio_play_button pron-us icon-audio"})
  mp3us1 = mp3us1.get("data-src-mp3") if mp3us1 else "Data Tidak Ditemukan"

  # get word title
  title1 = soup2.find("h1", {"class": "headword"})
  title1 = title1.text if title1 else "Data Tidak Ditemukan"

  # append all
  mp3.append(mp3uk1)
  mp3.append(mp3us1)
  words.append(title1)

  # find the first ul tag with the class name 'sense-group-results'
  uls = soup.find("ul", {"class": "sense-group-results"})

  # find all the li tags inside the ul tag again, but this time extract the word from the babTTS link
  for lis in uls.find_all("li"):
    get_a = lis.find("a")
    if get_a is not None and get_a.get("href") and "babTTS" in get_a.get(
        "href"):
      # extract the word from the href attribute
      word = get_a.get("href").split("'")[3]
      words.append(word)

  # find all the li tags inside the ul tag and skip the first one
  for lis in uls.find_all("li")[1:]:
    get_a = lis.find("a")
    if get_a is not None:
      words.append(get_a.text)

  # find translations and examples
  for sense in soup.find_all("span", {"class": "ogl_sense"}):
    for another in sense.find_all_next("span", {"class": "ogl_sense_inner"}):
      for translation in another.find_all("span",
                                          {"class": "ogl_translation noline"}):
        translations.append(translation.text.strip())
      for example in another.find_all("span", {"class": "ogl_examples"}):
        # english
        for eng in example.find_all("span", {"class": "ogl_exa"}):
          examples.append(eng.text.strip())
        # indonesian
        for ind in example.find_all("span", {"class": "ogl_translation"}):
          examples.append(ind.text.strip())

      # translation = another.find('span', {'class': 'ogl_translation noline'})
      # if translation:
      #     translations.append(translation.text.strip())
      #     example = another.find('span', {'class': 'ogl_examples'})
      #     if example:
      #         eng = example.find('span', {'class': 'ogl_exa'})
      #         ind = example.find('span', {'class': 'ogl_translation'})
      #         if eng and ind:
      #             examples.append({'eng': eng.text.strip(), 'ind': ind.text.strip()})

  for tag in soup.select(
      ".icon-link-wrapper.dropdown a, .icon-link-wrapper.dropdown span, .icon-link-wrapper.dropdown ul, .icon-link-wrapper.dropdown li, .icon-link-wrapper.dropdown another"
  ):
    tag.decompose()

  for contextual in soup.find_all("div", {"class": "sense-group"}):
    for example in soup.find_all("div", {"class": "dict-example"}):
      eng1 = None  # Define eng1 outside of the inner loop
      for eng in example.find_all(
          "div", {"class": "dict-source dict-source_examples"}):
        eng1 = eng.text.strip()  # Assign value to eng1
      for ind in example.find_all("div", {"class": "dict-result"}):
        ind1 = ind.text.strip()
        if eng1 and ind1:
          sentences.append({"eng": eng1, "ind": ind1})

  lis = soup.select(".quick-result-entry .quick-result-overview li a")
  for li in lis[9:15]:
    synonym = li.text
    synonyms.append(synonym)

  # create dictionary and return as JSON
  data = {
    "words": words,
    "translations": translations,
    "examples": examples,
    "synonyms": synonyms,
    "sentences": sentences,
    "mp3": mp3,
    "author": "Xnuvers007 [ Https://github.com/Xnuvers007 ]",
  }
  return jsonify(data)


@app.route("/kanjiname", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def kanji_name():
  nama = request.args.get("nama")
  url = f"https://jepang-indonesia.co.id/kanjiname/convert?name={nama}&x=73&y=48"

  headers = {
    "User-Agent":
    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
  }

  response = requests.get(url, headers=headers)

  soup = BeautifulSoup(response.text, "html.parser")

  # get url from this my server menggunakan requests host

  server = f"{request.host_url}kanjiname?nama={nama}"

  result = {
    "kanji":
    soup.find("div", {
      "class": "text-center rounded-box hanzi"
    }).text.strip(),
    "arti":
    soup.find("div", {
      "class": "text-center meantext"
    }).text.strip(),
    "original":
    nama,
    "server":
    server,
  }

  return jsonify(result)


@app.route("/translate", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def translate():
  from_lang = request.args.get("from", "en")
  to_lang = request.args.get("to", "id")
  text = request.args.get("text", "")

  # set up headers
  headers = {
    "User-Agent": random.choice(get_user_agents()),
    "Referer": "http://translate.google.com/",
    "Origin": "http://translate.google.com/",
  }

  # send request to Google Translate API
  url = f"https://translate.google.com/translate_a/single?client=gtx&sl={from_lang}&tl={to_lang}&dt=t&q={text}"
  response = requests.get(url, headers=headers)

  # extract translated text from response
  result = response.json()
  if result is not None and len(result) > 0 and len(result[0]) > 0:
    translated_text = result[0][0][0]
  else:
    translated_text = "Translation failed"

  # return result as JSON
  return jsonify({
    "code/status": response.status_code,
    "from": from_lang,
    "to": to_lang,
    "text": text,
    "user_agent": headers["User-Agent"],
    "translated_text": translated_text,
    "credits": "Xnuvers007 ( https://github.com/xnuvers007 )",
  })


def igstalk(username):
  headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
  }
  url = f"https://dumpoir.com/v/{username}"

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    profile = (
      soup.select_one("#user-page > div.user > div.row > div > div.user__img")
      ["style"].replace("background-image: url('", "").replace("');", ""))
    fullname = soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > div > a > h1"
    ).get_text()
    username = soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > div > h4"
    ).get_text()
    post = (soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > ul > li:nth-child(1)"
    ).get_text().replace(" Posts", ""))
    followers = (soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > ul > li:nth-child(2)"
    ).get_text().replace(" Followers", ""))
    following = (soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > ul > li:nth-child(3)"
    ).get_text().replace(" Following", ""))
    bio = soup.select_one(
      "#user-page > div.user > div > div.col-md-5.my-3 > div").get_text()

    result = {
      "profile": profile,
      "fullname": fullname,
      "username": username,
      "post": post,
      "followers": followers,
      "following": following,
      "bio": bio,
      "url": f"https://www.instagram.com/{username.replace('@', '')}",
    }

    return result, response.status_code

  except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
      raise Exception("Error: Account not found")
    elif e.response.status_code == 403:
      raise Exception("Error: Account is private")
    else:
      # redirect('https://tr.deployers.repl.co/igstalk?user=Indradwi.25')
      redirect(url_for("index"))


@app.route("/igstalk")
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def igstalk_route():
  username = request.args.get("user")

  if not username:
    # return jsonify({"error": "Missing username parameter"}), 400
    #   return redirect('https://tr.deployers.repl.co/igstalk?user=Indradwi.25'), 400
    return redirect(url_for("/"))

  try:
    result, status_code = igstalk(username)
    result["status"] = status_code
    result["credits"] = "Xnuvers007 (https://github.com/Xnuvers007)"
    return jsonify(result), status_code

  except Exception as e:
    return jsonify({"error": str(e)}), 500


@app.route('/cariobat', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def cari_obat():
  obat = request.args.get('obat')

  url = "https://www.halodoc.com/obat-dan-vitamin/search/" + obat

  response = requests.get(
    url,
    headers={
      "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
    })
  time.sleep(1.5)

  soup = BeautifulSoup(response.content, "html.parser")

  data = []

  gambar_elements = soup.find_all("div", class_="img-wrapper")
  gambar_alt = [elem.find("img")["alt"] for elem in gambar_elements]

  fallback_images = soup.find_all("img", class_="fallback-img")
  fallback_image_urls = [img["src"] for img in fallback_images]

  harga = soup.find_all("div", class_="custom-container__list")
  dataharga = []

  for i in harga:
    for j in i.findAll(
        "label", class_="custom-container__list__container__price--label"):
      dataharga.append(j.text.strip())

  datasumber = []
  for i in harga:
    for j in i.findAll("a",
                       class_="custom-container__list__container__item--link"):
      href = j["href"].strip()
      sumber = "https://www.halodoc.com" + href
      datasumber.append(sumber)

  for alt, fallback_url, harga, sumber in zip(gambar_alt, fallback_image_urls,
                                              dataharga, datasumber):
    obat_data = {}
    obat_data['alt'] = alt
    obat_data['fallback_url'] = fallback_url
    obat_data['harga'] = harga
    obat_data['sumber'] = sumber
    data.append(obat_data)

  return jsonify(data)


@app.route('/keterangan', methods=['GET'])
def keterangan_obat():
  datasumber = request.args.get('obat')
  if re.match(r"^https?://", datasumber):
    url = datasumber
  elif not re.match(r"^https?://", datasumber):
    url = "https://" + datasumber
  elif datasumber.startswith("/"):
    datasumber = datasumber[1:]
    datasumber = re.sub(r"\s", "-", datasumber)
    url = "https://www.halodoc.com/obat-dan-vitamin/" + datasumber
  else:
    datasumber = re.sub(r"\s", "-", datasumber)
    url = "https://www.halodoc.com/obat-dan-vitamin/" + datasumber

  if datasumber.startswith("/"):
    url = "https://www.halodoc.com" + datasumber

  response = requests.get(
    url,
    headers={
      "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
    })
  time.sleep(1.5)

  soup = BeautifulSoup(response.content, "html.parser")

  # drug_details = soup.find_all("div", class_="drug-detail col-md-12")
  drug_details = soup.find_all(
    "div",
    class_=
    "property-container lg:w-full lg:pr-4 lg:pl-4 md:w-full md:pr-4 md:pl-4")

  # if len(drug_details) > 0:
  #   data = {}
  #   data['Deskripsi'] = drug_details[0].text.strip(
  #   ) if drug_details[0].text else ""
  #   data['Indikasi Umum'] = drug_details[1].text.strip(
  #   ) if drug_details[1].text else ""
  #   data['Komposisi'] = drug_details[2].text.strip(
  #   ) if drug_details[2].text else ""
  #   data['Dosis'] = drug_details[3].text.strip(
  #   ) if drug_details[3].text else ""
  #   data['Aturan Pakai'] = drug_details[4].text.strip(
  #   ) if drug_details[4].text else ""
  #   data['Peringatan'] = drug_details[5].text.strip(
  #   ) if drug_details[5].text else ""
  #   data['Kontra Indikasi'] = drug_details[6].text.strip(
  #   ) if drug_details[6].text else ""
  #   data['Efek Samping'] = drug_details[7].text.strip(
  #   ) if drug_details[7].text else ""
  #   data['Golongan Produk'] = drug_details[8].text.strip(
  #   ) if drug_details[8].text else ""
  #   data['Kemasan'] = drug_details[9].text.strip(
  #   ) if drug_details[9].text else ""
  #   data['Manufaktur'] = drug_details[10].text.strip(
  #   ) if drug_details[10].text else ""
  #   data['No. Registrasi'] = drug_details[11].text.strip(
  #   ) if drug_details[11].text else ""
  #   return jsonify(data)
  # else:
  #   return "Tidak ada data yang ditemukan."

  data = {}
  for item in drug_details:
    title = item.find("div", class_="ttl-list").text.strip()
    content = item.find(
      "div", class_="drug-detail md:w-full md:pr-4 md:pl-4").text.strip()
    content = content.replace("\n", "")
    data[title] = content
  return jsonify(data)


# URL SHORTLINK TINYURL
class UrlShorten:
  TINYURL_URL = "http://tinyurl.com/api-create.php"
  ISGD_URL = "https://is.gd/create.php?format=json&url="
  VGD_URL = "https://v.gd/create.php?format=json&url="
  OUO_URL = "https://ouo.io/api/0G4vYlK2?s="
  BITLY_URL = "https://bitly.ws/create.php?url="

  headers = {'User-Agent': random_user_agent}

  @staticmethod
  def tinyurl(url_long):
    try:
      url = UrlShorten.TINYURL_URL + "?" + urllib.parse.urlencode(
        {"url": url_long})
      res = requests.get(url)
      res.raise_for_status()
      short_url = res.text
      return short_url
    except requests.RequestException as e:
      raise Exception(f'TinyURL error: {str(e)}')

  @staticmethod
  def isgd(url_long):
    try:
      url = UrlShorten.ISGD_URL + url_long
      res = requests.get(url)
      res.raise_for_status()
      data = res.json()
      return data.get('shorturl',
                      f'Error: {data.get("error", "Unknown error")}')
    except requests.RequestException as e:
      raise Exception(f'is.gd error: {str(e)}')

  @staticmethod
  def vgd(url_long):
    try:
      url = UrlShorten.VGD_URL + url_long
      res = requests.get(url)
      res.raise_for_status()
      data = res.json()
      return data.get('shorturl',
                      f'Error: {data.get("error", "Unknown error")}')
    except requests.RequestException as e:
      raise Exception(f'v.gd error: {str(e)}')

  @staticmethod
  def ouo(url_long):
    try:
      url = UrlShorten.OUO_URL + url_long
      res = requests.get(url)
      res.raise_for_status()
      soup = BeautifulSoup(res.text, 'html.parser')
      a = soup.prettify().strip()
      return a
    except requests.RequestException as e:
      raise Exception(f'ouo.io error: {str(e)}')

  @staticmethod
  def bitly(url_long):
    try:
      url = UrlShorten.BITLY_URL + url_long
      res = requests.get(url)
      res.raise_for_status()
      soup = BeautifulSoup(res.text, 'html.parser')
      a = [
        b.text for b in soup.find_all(
          "div", {
            "style":
            "padding-top: 20;text-align: center; background-color: #EFF7FC"
          })[0].find_all("b")
      ]
      return a[1]
    except requests.RequestException as e:
      raise Exception(f'bit.ly error: {str(e)}')


@app.route('/short', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def shorten_url():
  try:
    url_long = request.args.get('url')
    if not url_long:
      server = f"{request.host_url}short?url=github.com/Xnuvers007"
      return jsonify({
        'error': 'No URL provided.',
        'endpoint': server,
        'author': 'Xnuvers007 [ https://github.com/Xnuvers007 ]'
      }), 400

    # Check if "http://" or "https://" prefix is missing and add it based on server support
    if not url_long.startswith('http://') and not url_long.startswith(
        'https://'):
      if request.is_secure:
        url_long = 'https://' + url_long
      else:
        url_long = 'http://' + url_long

    response = {
      'tinyurl': None,
      'isgd': None,
      'vgd': None,
      'ouo': None,
      'bitly': None,
      'a_status': requests.get(url_long).status_code,
      'author': 'Xnuvers007 [ https://github.com/Xnuvers007 ]'
    }

    try:
      response['tinyurl'] = UrlShorten.tinyurl(url_long)
    except Exception as e:
      response['tinyurl'] = str(e)

    try:
      response['isgd'] = UrlShorten.isgd(url_long)
    except Exception as e:
      response['isgd'] = str(e)

    try:
      response['vgd'] = UrlShorten.vgd(url_long)
    except Exception as e:
      response['vgd'] = str(e)

    try:
      response['ouo'] = UrlShorten.ouo(url_long)
    except Exception as e:
      response['ouo'] = str(e)

    try:
      response['bitly'] = UrlShorten.bitly(url_long)
    except Exception as e:
      response['bitly'] = str(e)

    return jsonify(response), 200
  except Exception as e:
    traceback.print_exc()
    return jsonify({'error': str(e)}), 500


@app.route('/tiktok', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def download_tiktok_video():
  url = request.args.get('url')
  # sources = input("Enter link Tiktok: ")

  cookies = {
    '_gid': 'GA1.2.1792354021.1686935708',
    '_gat_UA-3524196-6': '1',
    '__gads':
    'ID=a5ab8cd128367568-22143e9f8de100bf:T=1686935709:RT=1686974876:S=ALNI_MZGs_Ok-Opd0utB89Ocx6MHsRPIhg',
    '__gpi':
    'UID=00000c5060eb2f3a:T=1686935709:RT=1686974876:S=ALNI_MaTK25bQMrHcFRzycSi0AkbCKx4Rg',
    '_ga': 'GA1.2.1848273344.1686935708',
    '_ga_ZSF3D6YSLC': 'GS1.1.1686974876.3.0.1686974917.0.0.0',
  }

  headers = {
    'authority':
    'ssstik.io',
    'accept':
    '*/*',
    'accept-language':
    'id,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
    'cache-control':
    'no-cache',
    'content-type':
    'application/x-www-form-urlencoded; charset=UTF-8',
    # 'cookie': '_gid=GA1.2.1792354021.1686935708; _gat_UA-3524196-6=1; __gads=ID=a5ab8cd128367568-22143e9f8de100bf:T=1686935709:RT=1686974876:S=ALNI_MZGs_Ok-Opd0utB89Ocx6MHsRPIhg; __gpi=UID=00000c5060eb2f3a:T=1686935709:RT=1686974876:S=ALNI_MaTK25bQMrHcFRzycSi0AkbCKx4Rg; _ga=GA1.2.1848273344.1686935708; _ga_ZSF3D6YSLC=GS1.1.1686974876.3.0.1686974917.0.0.0',
    'hx-current-url':
    'https://ssstik.io/en',
    'hx-request':
    'true',
    'hx-target':
    'target',
    'hx-trigger':
    '_gcaptcha_pt',
    'origin':
    'https://ssstik.io',
    'pragma':
    'no-cache',
    'referer':
    'https://ssstik.io/en',
    'sec-ch-ua':
    '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
    'sec-ch-ua-mobile':
    '?0',
    'sec-ch-ua-platform':
    '"Windows"',
    'sec-fetch-dest':
    'empty',
    'sec-fetch-mode':
    'cors',
    'sec-fetch-site':
    'same-origin',
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43',
  }

  params = {
    'url': 'dl',
  }

  data = {
    'id':
    url,  # 'https://www.tiktok.com/@yurii_kun5/video/7225627953185721627?is_from_webapp=1&sender_device=pc'
    'locale': 'en',
    'tt': 'UEhBVXVj',
  }

  response = requests.post('https://ssstik.io/abc',
                           params=params,
                           cookies=cookies,
                           headers=headers,
                           data=data)

  downloadVideos = BeautifulSoup(response.text, 'html.parser')
  downloadLink = downloadVideos.a["href"]
  video_content = requests.get(downloadLink).content

  file_name = f"{time.time()}.mp4"
  file_path = f"{DOWNLOAD_DIR}/{file_name}"
  with open(file_path, 'wb') as video:
    video.write(video_content)

  escaped_data = file_path  #escape(file_name)

  # awal pake html :V
  # return f"Video downloaded. Access it at: <a href='{escaped_data}'>{escaped_data}</a>"
  return redirect(downloadLink)


@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
  return send_from_directory(DOWNLOAD_DIR, path=filename, as_attachment=True)


@app.route('/d', methods=['GET'])
@app.route('/de', methods=['GET'])
@app.route('/del', methods=['GET'])
@app.route('/dele', methods=['GET'])
@app.route('/delet', methods=['GET'])
@app.route('/delete', methods=['GET'])
@app.route('/e', methods=['GET'])
@app.route('/el', methods=['GET'])
@app.route('/ele', methods=['GET'])
@app.route('/elet', methods=['GET'])
@app.route('/elete', methods=['GET'])
@app.route('/et', methods=['GET'])
@app.route('/ete', methods=['GET'])
@app.route('/l', methods=['GET'])
@app.route('/le', methods=['GET'])
@app.route('/let', methods=['GET'])
@app.route('/lete', methods=['GET'])
@app.route('/t', methods=['GET'])
@app.route('/te', methods=['GET'])
def delete_files():
  files = glob.glob(f"{DOWNLOAD_DIR}/*")
  current_time = time.time()
  for file in files:
    if os.path.isfile(file):
      modified_time = os.path.getmtime(file)
      if current_time - modified_time > 1:
        os.remove(file)
  time.sleep(1)  # Sleep for 30 minutes
  delete_threads = threading.Thread(target=delete_files)
  delete_threads.start()
  return "<h1><strong>Files deleted.</strong></h1>"


@app.route('/openai', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def openai():
  APIKEYS_NYA = request.args.get('key')

  if not APIKEYS_NYA:
    return jsonify({
      'error': 'Masukkan APIKEYS OPENAI',
      'path': '/openai?key=APIKEYS_NYA'
    })

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://yenom.pro',
    'Connection': 'keep-alive',
    'Referer': 'https://yenom.pro/cek.php',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
  }

  data = {
    'api_keys': APIKEYS_NYA,
  }

  response = requests.post('https://yenom.pro/cek.php',
                           headers=headers,
                           data=data)

  soup = BeautifulSoup(response.text, 'html.parser')

  # get table of contents
  table = soup.find('table')

  # get all rows from table
  rows = table.find_all('tr')

  # get all columns from table
  columns = [v.text.replace('\n', '') for v in rows[0].find_all('th')]

  # build output as JSON
  output = []
  for i in range(1, len(rows)):
    tds = rows[i].find_all('td')
    row_data = {}
    for j, td in enumerate(tds):
      column_name = columns[j]
      value = td.text.replace('\n', '')
      row_data[column_name] = value
    output.append(row_data)

  result = {
    'author': 'Xnuvers007 (https://github.com/Xnuvers007)',
    'donate': 'https://ndraeee25.000webhostapp.com/dana/DanaXnuvers007.jpeg',
    'data': output
  }

  return jsonify(result)


def scrape_matches_from_table(table):
  tbody = table.find('tbody')
  if not tbody:
    return "Jadwal Pertandingan belum tersedia"

  trs = tbody.find_all('tr')

  matches_data = []

  for tr in trs:
    club_boxes = tr.find_all('span', class_='clubBox-name')
    tds = tr.find_all('td')[0:2]
    if len(club_boxes) >= 2:
      team1, team2 = [club.text.strip() for club in club_boxes]
      match_time = tds[1].text.strip()
      matches_data.append(f"{team1} vs {team2} ({match_time})")

  return matches_data


def scrape_matches_from_table(table):
  tbody = table.find('tbody')
  if not tbody:
    return "Jadwal Pertandingan belum tersedia"

  trs = tbody.find_all('tr')

  matches_data = []

  for tr in trs:
    club_boxes = tr.find_all('span', class_='clubBox-name')
    tds = tr.find_all('td')[0:2]
    if len(club_boxes) >= 2:
      team1, team2 = [club.text.strip() for club in club_boxes]
      match_time = tds[1].text.strip()
      matches_data.append(f"{team1} vs {team2} ({match_time})")

  return matches_data


def get_jadwal_pertandingan(url):
  cookies = {
    'ahoy_visitor': '9f1bb6dc-790f-4664-82e6-7611c0f9a132',
    '_ga_YV9LXF9F74': 'GS1.1.1690092464.11.1.1690092762.42.0.0',
    '_ga': 'GA1.1.970211948.1689523452',
    '__gads':
    'ID=79358ecd1813041a:T=1689523448:RT=1690092467:S=ALNI_MYdBdDc8Vcy0SeNFLWyKRIx1T9uqA',
    '__gpi':
    'UID=00000c2149be351d:T=1689523448:RT=1690092467:S=ALNI_MaRUe2JyuR-N_K2kAhk898eqlziTg',
    '_cc_id': 'a3c5e70268c5926475d2e072101ce745',
    'cto_bundle':
    'BMnfl184RlY4MWhCdDNIQ0ZzUiUyQmlKSG0yZSUyRmFkVXdqenpTbFdOSDJxckNiYjBwMVNBVk5raERYcmRZdGRFUW5JUUZOTVBrZlNlaldaSGdvT0wxc3pGZDNzMWp4MGZCejBtekMlMkIlMkY5cmJxY0JPZzlFZXU1elBkWmQ1ZHlmN0pxRlVyYlJla1RVWE04ZSUyRksyJTJCNTBZTDltODRoTkElM0QlM0Q',
    '_ga_6HPZ6B3B7K': 'GS1.1.1690097027.12.0.1690097027.0.0.0',
    'youniverse_id': '51fca571-692f-45cf-b92d-df7dce5cadba',
    'bola_net_xtreme_visit_count_': '5',
    '_gid': 'GA1.2.449434685.1690092460',
    'panoramaId_expiry': '1690178874304',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Alt-Used': 'www.bola.net',
    'Connection': 'keep-alive',
    'Referer': 'https://www.bola.net/jadwal-pertandingan/',
    # 'Cookie': 'ahoy_visitor=9f1bb6dc-790f-4664-82e6-7611c0f9a132; _ga_YV9LXF9F74=GS1.1.1690092464.11.1.1690092762.42.0.0; _ga=GA1.1.970211948.1689523452; __gads=ID=79358ecd1813041a:T=1689523448:RT=1690092467:S=ALNI_MYdBdDc8Vcy0SeNFLWyKRIx1T9uqA; __gpi=UID=00000c2149be351d:T=1689523448:RT=1690092467:S=ALNI_MaRUe2JyuR-N_K2kAhk898eqlziTg; _cc_id=a3c5e70268c5926475d2e072101ce745; cto_bundle=BMnfl184RlY4MWhCdDNIQ0ZzUiUyQmlKSG0yZSUyRmFkVXdqenpTbFdOSDJxckNiYjBwMVNBVk5raERYcmRZdGRFUW5JUUZOTVBrZlNlaldaSGdvT0wxc3pGZDNzMWp4MGZCejBtekMlMkIlMkY5cmJxY0JPZzlFZXU1elBkWmQ1ZHlmN0pxRlVyYlJla1RVWE04ZSUyRksyJTJCNTBZTDltODRoTkElM0QlM0Q; _ga_6HPZ6B3B7K=GS1.1.1690097027.12.0.1690097027.0.0.0; youniverse_id=51fca571-692f-45cf-b92d-df7dce5cadba; bola_net_xtreme_visit_count_=5; _gid=GA1.2.449434685.1690092460; panoramaId_expiry=1690178874304',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
  }

  response = requests.get(url, cookies=cookies, headers=headers)

  # check if cookies and headers are valid and not expired
  if not response.ok:
    print("Cookies or Headers are not valid")
    return

  soup = BeautifulSoup(response.text, 'html.parser')

  Jadwal = soup.find('h1', class_='box-title')
  if not soup.find_all('table', class_='main-table main-table--jadwal'):
    return {"url": url, "data": "Jadwal Pertandingan belum tersedia"}

  matches_data = []
  tables = soup.find_all('table', class_='main-table main-table--jadwal')

  for table in tables:
    thead = table.find('thead')
    th = thead.find_all('th')[0]
    date = th.text.strip()
    data = scrape_matches_from_table(table)
    matches_data.extend([(date, match) for match in data
                         ])  # Append date along with match data

  return {"judul": Jadwal.text, "url": url, "data": matches_data}


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/jadwal-pertandingan', methods=['GET'])
def jadwal_pertandingan():
  links = [
    "https://www.bola.net/jadwal-pertandingan/indonesia.html",
    "https://www.bola.net/jadwal-pertandingan/inggris.html",
    "https://www.bola.net/jadwal-pertandingan/italia.html",
    "https://www.bola.net/jadwal-pertandingan/spanyol.html",
    "https://www.bola.net/jadwal-pertandingan/champions.html",
    "https://www.bola.net/jadwal-pertandingan/jerman.html",
    "https://www.bola.net/jadwal-pertandingan/prancis.html"
  ]

  results = []

  for link in links:
    response = get_jadwal_pertandingan(link)
    results.append(response)

  return jsonify(results)


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/zerogpt', methods=['GET', 'POST'])
def detect_text():
  if request.method == 'POST':
    t = request.form.get('text')

    cookies = {
      '_gid':
      'GA1.2.2082658495.1687029546',
      '_ga_0YHYR2F422':
      'GS1.1.1687029546.4.0.1687029546.0.0.0',
      '_ga':
      'GA1.1.536846619.1686378008',
      '__gads':
      'ID=7f4d15fa18fc00b0-223fc645a5b40066:T=1686378006:RT=1687029546:S=ALNI_Mb9fZYiAgQvvyLX4bMsTwH_9EiqHA',
      '__gpi':
      'UID=00000c465e269f92:T=1686378006:RT=1687029546:S=ALNI_MYnnN1CPxljGUhJ8dXj6T8ePiIXjw',
    }

    headers = {
      'authority':
      'api.zerogpt.com',
      'accept':
      'application/json, text/plain, */*',
      'accept-language':
      'id,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
      'cache-control':
      'no-cache',
      'content-type':
      'application/json',
      'origin':
      'https://www.zerogpt.com',
      'pragma':
      'no-cache',
      'referer':
      'https://www.zerogpt.com/',
      'sec-ch-ua':
      '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
      'sec-ch-ua-mobile':
      '?0',
      'sec-ch-ua-platform':
      '"Windows"',
      'sec-fetch-dest':
      'empty',
      'sec-fetch-mode':
      'cors',
      'sec-fetch-site':
      'same-site',
      'user-agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
    }

    json_data = {
      'input_text': t,
    }

    response = requests.post('https://api.zerogpt.com/api/detect/detectText',
                             cookies=cookies,
                             headers=headers,
                             json=json_data)

    json_response = response.json()

    return jsonify(json_response)

  return '''
            <!doctype html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <meta name="description" content="ZeroGPT Text Detection">
                <meta name="author" content="Xnuvers007">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <title>ZeroGPT Text Detection</title>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
            </head>
            <body>
                <div class="container mt-5">
                    <form action="/zerogpt" method="POST">
                        <div class="form-group">
                            <label for="text">Text</label>
                            <textarea class="form-control" id="text" name="text" rows="7" cols="50"></textarea>
                        </div>
                        <center><button type="submit" class="btn btn-primary">Detect Text</button></center>
                    </form>
                </div>
                <script>
        // Accessing navigator.userAgent, navigator.appVersion, and navigator.platform
        var userAgent = navigator.userAgent;
        var appVersion = navigator.appVersion;
        var platform = navigator.platform;
        
        // Perform any actions or log the values as needed
        console.log(userAgent);
        console.log(appVersion);
        console.log(platform);
    </script>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.min.js"></script>
            </body>
            </html>
        '''


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/zerogptjson', methods=['GET'])
def deteksiteksjson():
  t = request.args.get('t')

  cookies = {
    '_gid':
    'GA1.2.2082658495.1687029546',
    '_ga_0YHYR2F422':
    'GS1.1.1687029546.4.0.1687029546.0.0.0',
    '_ga':
    'GA1.1.536846619.1686378008',
    '__gads':
    'ID=7f4d15fa18fc00b0-223fc645a5b40066:T=1686378006:RT=1687029546:S=ALNI_Mb9fZYiAgQvvyLX4bMsTwH_9EiqHA',
    '__gpi':
    'UID=00000c465e269f92:T=1686378006:RT=1687029546:S=ALNI_MYnnN1CPxljGUhJ8dXj6T8ePiIXjw',
  }

  headers = {
    'authority':
    'api.zerogpt.com',
    'accept':
    'application/json, text/plain, */*',
    'accept-language':
    'id,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
    'cache-control':
    'no-cache',
    'content-type':
    'application/json',
    # 'cookie': '_gid=GA1.2.2082658495.1687029546; _ga_0YHYR2F422=GS1.1.1687029546.4.0.1687029546.0.0.0; _ga=GA1.1.536846619.1686378008; __gads=ID=7f4d15fa18fc00b0-223fc645a5b40066:T=1686378006:RT=1687029546:S=ALNI_Mb9fZYiAgQvvyLX4bMsTwH_9EiqHA; __gpi=UID=00000c465e269f92:T=1686378006:RT=1687029546:S=ALNI_MYnnN1CPxljGUhJ8dXj6T8ePiIXjw',
    'origin':
    'https://www.zerogpt.com',
    'pragma':
    'no-cache',
    'referer':
    'https://www.zerogpt.com/',
    'sec-ch-ua':
    '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
    'sec-ch-ua-mobile':
    '?0',
    'sec-ch-ua-platform':
    '"Windows"',
    'sec-fetch-dest':
    'empty',
    'sec-fetch-mode':
    'cors',
    'sec-fetch-site':
    'same-site',
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
  }

  json_data = {
    'input_text': t,
  }

  response = requests.post('https://api.zerogpt.com/api/detect/detectText',
                           cookies=cookies,
                           headers=headers,
                           json=json_data)

  json_response = response.json()

  return jsonify(json_response)


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/playlist', methods=['GET'])
def get_playlist():
  playlist_name = request.args.get('name', default='anime')
  limit = int(request.args.get('lim', default=51))

  playlists_search = PlaylistsSearch(playlist_name, limit=limit)
  results = playlists_search.result()

  return jsonify(results)


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/vid', methods=['GET'])
def get_video():
  video_name = request.args.get('name', default='anime')
  limit = int(request.args.get('lim', default=51))

  all_search = Search(video_name, limit=limit)
  results = all_search.result()

  return jsonify(results)


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/playlist', defaults={'path': ''})
@app.route('/vid', defaults={'path': ''})
def invalid_url(path):
  return redirect('/playlist?name=anime&lim=51')


def get_ip_addresses(url):
  try:
    # Get the IP address associated with the URL
    hostname = urlparse(url).hostname
    if not hostname:
      return None, None
    ip_address = socket.gethostbyname(hostname)
    real_ip_address = socket.gethostbyname_ex(hostname)[2][0]
    return ip_address, real_ip_address
  except socket.gaierror as e:
    return None, None


def is_vulnerable_to_clickjacking(url):
  # Suppress SSL warnings
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

  headers = {'User-Agent': 'Mozilla/5.0'}
  try:
    response = requests.get(url, headers=headers, verify=False)
  except requests.exceptions.SSLError as e:
    return False, f"Unable to make an SSL connection to {escape(url)}: {escape(str(e))}"

  # Check if X-Frame-Options header is set
  x_frame_options = response.headers.get('X-Frame-Options')
  content_security_policy = response.headers.get('Content-Security-Policy')

  # Get the IP and real IP addresses
  ip_address, real_ip_address = get_ip_addresses(url)

  if not x_frame_options and not content_security_policy:
    return True, f"{escape(url)} is vulnerable to clickjacking (X-Frame-Options header is not set) and (Content-Security-Policy header is not set)."

  if not x_frame_options:
    return True, f"{escape(url)} is vulnerable to clickjacking (X-Frame-Options header is not set)."

  if not content_security_policy:
    return True, f"{escape(url)} is vulnerable to clickjacking (Content-Security-Policy header is not set)."

  return True, f"{escape(url)} is not vulnerable to clickjacking."


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/cj')
def check_clickjacking_vulnerability():
  website = request.args.get('u')

  # Check if the 'u' parameter is provided
  if not website:
    return jsonify({
      "parameter":
      escape(request.host_url + "cj?u=https://0e87ad76-6c4e-40ff-bb5a-6bbdab145ae2-00-39qk1kw7vab6l.worf.replit.dev")
    })

  # Add 'http://' if the URL doesn't have a scheme
  if not urlparse(website).scheme:
    website = 'http://' + website

  is_vulnerable, result_message = is_vulnerable_to_clickjacking(website)

  # Get the current time
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  how_to_protect = '''
How To Protect Your Website From Clickjacking
[+] X-Frame-Options
1. X-FRAME-OPTIONS: DENY
2. X-FRAME-OPTIONS: SAMEORIGIN
3. X-FRAME-OPTIONS: ALLOW-FROM https://example.com

[+] Content-Security-Policy
1. Content-Security-Policy: frame-ancestors 'none'
2. Content-Security-Policy: frame-ancestors 'self'
3. Content-Security-Policy: frame-ancestors https://example.com

[+] Frame busting
<style>
/* Hide page by default */
html { display : none; }
</style>
<script>
if (self == top) {
// Everything checks out, show the page.
document.documentElement.style.display = 'block';
} else {
// Break out of the frame.
top.location = self.location;
}
</script>

[+] Code Snippets
1. NodeJS
response.setHeader("X-Frame-Options", "DENY");
response.setHeader("Content-Security-Policy", "frame-ancestors 'none'");

2. Java
public void doGet(HttpServletRequest request, HttpServletResponse response)
{
response.addHeader("X-Frame-Options", "DENY");
response.addHeader("Content-Security-Policy", "frame-ancestors 'none'");
}

3. PHP
response.setHeader("X-Frame-Options", "DENY");
response.setHeader("Content-Security-Policy", "frame-ancestors 'none'");

4. Python
response.headers["X-Frame-Options"] = "DENY"
response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"

[+] Web Server & Frameworks config:
1. Apache
Enable mod_headers using this command:
a2enmod headers

Restart the apache server
sudo service apache2 restart

Open and edit the config file in sites-available folder
sudo nano 000-default.conf

Add the following lines in <Virtual host>
Header set X-Frame-Options "DENY"
Header set Content-Security-Policy "frame-ancestors 'none'"

2. Nginx
Open and edit the config file in sites-available folder
sudo nano default

Add the following lines in {Server block}
add_header X-Frame-Options "DENY";
add_header Content-Security-Policy "frame-ancestors 'none'";

Restart the nginx server
sudo service nginx restart

3. Wordpress

Open and edit the wp-config.php file
sudo nano wp-config.php

Add the following lines in the end of the file
header('X-Frame-Options: SAMEORIGIN');
header("Content-Security-Policy: frame-ancestors 'none'");
'''.strip()

  # Prepare the JSON response
  response_data = {
    'url': escape(website),
    'is_vulnerable': is_vulnerable,
    'result_message': escape(result_message),
    'how_to_protect': escape(how_to_protect),
    'current_time': escape(current_time),
  }

  # Add IP addresses to the response if available
  ip_address, real_ip_address = get_ip_addresses(website)
  if ip_address and real_ip_address:
    response_data['ip_address'] = escape(ip_address)
    response_data['real_ip_address'] = escape(real_ip_address)

  return jsonify(response_data)


def formal(words, mode='formal'):
  cookies = {
    '_ga_G2MQKX8TDD': 'GS1.1.1690508017.3.1.1690508201.0.0.0',
    '_ga': 'GA1.1.169299824.1690395373',
    '__gads':
    'ID=cbbec9c914184adf-2216db83b6e700bc:T=1690395375:RT=1690508019:S=ALNI_MbmhZNSvwe6aKH6ktfzzl0-xd_GMw',
    '__gpi':
    'UID=00000c2464e7c373:T=1690395375:RT=1690508019:S=ALNI_MbdDsKNqRWAGM-QRJa7wfCaAR16CA',
    'XSRF-TOKEN':
    'eyJpdiI6IkhHT0tXZlZHNlQrQmFsTnp5K3FEU0E9PSIsInZhbHVlIjoiRGVrbzExcWoxZ1h2TlVGQ2VmKy9EVVdiRzlPWmp6WU1iVlhna2tZd0VkSFBlMlJXN1h3TXVHeDRQc2hiQVp0eWxRNGdNVy9UMzlReDBjSEpWT0FweEtMK3pZMytnVTBvOEZ4NjVFTFFncFJkUlZ3SW1LU0VzSzlnNk4wTzFFTGwiLCJtYWMiOiI2Y2MyZTUyZTRhMzU0ZDdjMjg4MjQwMDZlOTc2ZTMwMmYwNjg1NzJmODUwNTZmNDQxYWEzYmIwYzE3NjViNDJkIiwidGFnIjoiIn0%3D',
    'paraphrasingio_session':
    'eyJpdiI6Ik80YkViVU9KNDlYeHhObFAvNitod3c9PSIsInZhbHVlIjoia2RDbmVSN2JRRDB0dWp5ZkE3ekpCVkxPaW9SREs2cytFYmFVZjBlcDc4UnE3VWd1TnYzZnk2d2ZlQ3dUYWt3bk15OWdDT2FjK2pUZUt6dFZwdnJidWtsS1kwbHR0ZWtKNVpIMkR0L2VzTEtRLzlDWlFYRjI5RDZOL2dmS05pdm8iLCJtYWMiOiIzNmVkNmM3YjVkNDVkMzdhZGMxYWIwZWVhMzYzMzk1MmJjODRiYjZhNGZiMjljMzFkMjVlNzg3ZmVhZTZiYWM4IiwidGFnIjoiIn0%3D',
    'g_state': '{"i_p":1690515306722,"i_l":1}',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': '*/*',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'X-CSRF-TOKEN': 'k6yDSGkhgj4h3NKSbfO6gAvuHVYRlmLtfqh5CezH',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json;charset=utf-8',
    'X-XSRF-TOKEN':
    'eyJpdiI6IkhHT0tXZlZHNlQrQmFsTnp5K3FEU0E9PSIsInZhbHVlIjoiRGVrbzExcWoxZ1h2TlVGQ2VmKy9EVVdiRzlPWmp6WU1iVlhna2tZd0VkSFBlMlJXN1h3TXVHeDRQc2hiQVp0eWxRNGdNVy9UMzlReDBjSEpWT0FweEtMK3pZMytnVTBvOEZ4NjVFTFFncFJkUlZ3SW1LU0VzSzlnNk4wTzFFTGwiLCJtYWMiOiI2Y2MyZTUyZTRhMzU0ZDdjMjg4MjQwMDZlOTc2ZTMwMmYwNjg1NzJmODUwNTZmNDQxYWEzYmIwYzE3NjViNDJkIiwidGFnIjoiIn0=',
    'Origin': 'https://www.paraphrasing.io',
    'Connection': 'keep-alive',
    'Referer': 'https://www.paraphrasing.io/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
  }

  json_data = {
    'uri': 'paraphrase',
    'paragraph': words,
    'type': 'paraphrase',
    'lang': 'id',
    'mode': 'Simple',
    'structure': None,
    'grecaptcha': '',
  }

  response = requests.post('https://www.paraphrasing.io/contentGenerator',
                           cookies=cookies,
                           headers=headers,
                           json=json_data)

  resul = response.json()['result']
  jumlah_kalimat = response.json()['sentenceCount']
  pesan_status = response.json()['message']
  soup = BeautifulSoup(resul, 'html.parser')
  clean_text = soup.get_text()
  return {
    "Hasil: ": clean_text,
    "Jumlah Kalimat: ": jumlah_kalimat,
    "Pesan Status: ": pesan_status
  }


def regular(words, mode='regular'):

  cookies = {
    '_ga_G2MQKX8TDD': 'GS1.1.1690508017.3.1.1690508445.0.0.0',
    '_ga': 'GA1.1.169299824.1690395373',
    '__gads':
    'ID=cbbec9c914184adf-2216db83b6e700bc:T=1690395375:RT=1690508445:S=ALNI_MbmhZNSvwe6aKH6ktfzzl0-xd_GMw',
    '__gpi':
    'UID=00000c2464e7c373:T=1690395375:RT=1690508445:S=ALNI_MbdDsKNqRWAGM-QRJa7wfCaAR16CA',
    'XSRF-TOKEN':
    'eyJpdiI6Ik8zUTdEelY4bElqSm1oWW15QmFBQlE9PSIsInZhbHVlIjoiOGFFR1lKTkd3OHRyODhjWHVWalZkc1lSSTJOdklTSWdmRmV2ckNmRmRKdXF1cURWRUpXOGdzWFN4bUJINTJSei9tSlFxbnlDK056VEVGdXVNWEdYT1FTZ2R0OTJRelhTLzBiK3VXMXViY2ttTUErSFhkOHdwMWkrSUh4ZnFqenAiLCJtYWMiOiJkMWRmNzY0YWYzNzQ4Yzc2NTRhOGM3MmMwZDQwN2NiM2ZkOWYyOTJiMGUxNGQzZDYzNjVjZDYyMzY3Yzk3MDQ3IiwidGFnIjoiIn0%3D',
    'paraphrasingio_session':
    'eyJpdiI6Ikd5bGVoT0lrUEhVOUp3ekgvbWMyK0E9PSIsInZhbHVlIjoiKytqb0hrbVFaS2krZU1rVG5tQ3ltSFVBTTVzVlBFcUpNNTEwZEpueU1pUTY2VDVxakxOWHYvcTVsUGdMNlVmME90d1J5a0JJaElGQVlFa1o4cWQySGNpZjAzZ203ZUJPalV2bmlmR1BjN2V0MjF2OGhNdzlGd3IvZE5BSE4wbTciLCJtYWMiOiJmYWUwYmQ4OWY1OTUxMmEzOTQzNDYwNTE1MGEyZGM1NzRlNGI3NWI2ZjA2MGYyMTdjMjkzNzYzYmExYzQ5OGRkIiwidGFnIjoiIn0%3D',
    'g_state': '{"i_p":1690515306722,"i_l":1}',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': '*/*',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'X-CSRF-TOKEN': 'k6yDSGkhgj4h3NKSbfO6gAvuHVYRlmLtfqh5CezH',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json;charset=utf-8',
    'X-XSRF-TOKEN':
    'eyJpdiI6Ik8zUTdEelY4bElqSm1oWW15QmFBQlE9PSIsInZhbHVlIjoiOGFFR1lKTkd3OHRyODhjWHVWalZkc1lSSTJOdklTSWdmRmV2ckNmRmRKdXF1cURWRUpXOGdzWFN4bUJINTJSei9tSlFxbnlDK056VEVGdXVNWEdYT1FTZ2R0OTJRelhTLzBiK3VXMXViY2ttTUErSFhkOHdwMWkrSUh4ZnFqenAiLCJtYWMiOiJkMWRmNzY0YWYzNzQ4Yzc2NTRhOGM3MmMwZDQwN2NiM2ZkOWYyOTJiMGUxNGQzZDYzNjVjZDYyMzY3Yzk3MDQ3IiwidGFnIjoiIn0=',
    'Origin': 'https://www.paraphrasing.io',
    'Connection': 'keep-alive',
    'Referer': 'https://www.paraphrasing.io/id',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
  }

  json_data = {
    'uri': 'paraphrase',
    'paragraph': words,
    'type': 'paraphrase',
    'lang': 'id',
    'mode': 'word',
    'structure': None,
    'grecaptcha': '',
  }

  response = requests.post('https://www.paraphrasing.io/contentGenerator',
                           cookies=cookies,
                           headers=headers,
                           json=json_data)

  resul = response.json()['result']
  jumlah_kalimat = response.json()['sentenceCount']
  pesan_status = response.json()['message']
  soup = BeautifulSoup(resul, 'html.parser')
  clean_text = soup.get_text()
  return {
    "Hasil: ": clean_text,
    "Jumlah Kalimat: ": jumlah_kalimat,
    "Pesan Status: ": pesan_status
  }


def fluency(words, mode='fluency'):

  cookies = {
    'ci_session':
    'a%3A6%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%2267848c32d61bf207d11c76424342df68%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A15%3A%22103.144.175.180%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A80%3A%22Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A109.0%29%20Gecko%2F20100101%20Firefox%2F115.0%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1690395650%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22checkauth%22%3Bs%3A25%3A%22checkparaphrase1690393811%22%3B%7D5e11ee8476fb6d35e836ac9ade5b0e29',
    '_pbjs_userid_consent_data': '6683316680106290',
    '_sharedID': '3544682c-cbd2-46be-ab04-89dacadcbd6f',
    '_sharedID_last': 'Wed%2C%2026%20Jul%202023%2017%3A50%3A13%20GMT',
    '_lr_retry_request': 'true',
    '_lr_env_src_ats': 'false',
    'cto_bundle':
    'RlCI3F9rUGVJQlJ3TiUyRlk4ajhPVW1sTUlFb0ZYWmE0Z3dCaTdzelhQeFh2N2JLTURIT2RnRmVHaW9BWENRcE5xTHU1aFc3MUFtTWpVcWREVThEV0JjMHNFd0tqM3UlMkJQTkFja1J4RjhhRzc2aGxScHdEOFVnU3lNVGJqWEJ4VUVQQk41JTJCMnRua3Z1QjNvUU14Q0d0ZTU4OVolMkJjdyUzRCUzRA',
    'cto_bidid':
    '4--XuV9iVDBodVM0Z2F5c05DR0N6TGslMkZEZHpLRkQ5Y21qdGVnJTJGeGdmbTE0Tkh4cDRmVW5KU2Q4d3c3NWlQRGdkaCUyQjhJYlpmNnpqN3IyNHBFa2hlVEVVZTRTUnc4R0hVZm1tZGt5QXZlQTNjdm01VmxpMWkyV1lUOTZHYmhUMzVPJTJCMEd0',
    '_ga_Q3XGSV1HE8': 'GS1.1.1690393813.1.0.1690393813.0.0.0',
    '_ga': 'GA1.2.1073571075.1690393814',
    'TawkConnectionTime': '0',
    'twk_idm_key': 'Tt8aWgRm5O4fYTxKWw4vM',
    '_ga_WGYTCZ2REQ': 'GS1.1.1690393814.1.0.1690393814.0.0.0',
    'twk_uuid_62ff0ee954f06e12d88f800b':
    '%7B%22uuid%22%3A%221.7xXuhykE54shomhhNsD76WzcW38KrPglJvS8WDkpJttRsWG3U4Z3grd8zEbcQyHkPOBQsa6Or3fBiq1hsSg5DnDW6TSB1sYY9KZ3DbnAqtmFeQq9E9z1LKRB%22%2C%22version%22%3A3%2C%22domain%22%3A%22paraphraser.io%22%2C%22ts%22%3A1690395354540%7D',
    '__gads':
    'ID=aaa45ab7366b4c7a:T=1690393815:RT=1690393815:S=ALNI_Ma0pKRQabLL3P82pFJwPqexy3GzBw',
    '__gpi':
    'UID=00000c2464462814:T=1690393815:RT=1690393815:S=ALNI_Ma6kG7fiZ_fy1kMxUUmi2MNsJEhhA',
    '_gid': 'GA1.2.1688706906.1690393816',
    '_cc_id': 'aefa69b06e99889d68d20b2ea5f6177',
    'panoramaId_expiry': '1690480218162',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://www.paraphraser.io',
    'Connection': 'keep-alive',
    'Referer': 'https://www.paraphraser.io/id/parafrase-online',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
  }

  data = {
    'data': words,
    'mode': '1',
    'lang': 'id',
    'captcha': '',
  }

  response = requests.post(
    'https://www.paraphraser.io/frontend/rewriteArticleBeta',
    cookies=cookies,
    headers=headers,
    data=data)
  # Remove HTML tags from the response text
  soup = BeautifulSoup(response.text, 'html.parser')
  text_without_tags = soup.get_text()

  # Convert the text without tags to a JSON object
  json_data = json.loads(text_without_tags)
  parafrase = json.dumps(json_data.get('result', {}).get('paraphrase'),
                         indent=4).replace('<span>', '').replace(
                           '</span>', '').replace('<br>', '').replace(
                             '<br/>',
                             '').replace('<br />',
                                         '').replace('<b>',
                                                     '').replace('</b>',
                                                                 '').strip()
  persen = json.dumps(json_data.get('result', {}).get('percent'),
                      indent=4).replace('<span>', '').replace(
                        '</span>',
                        '').replace('<br>', '').replace('<br/>', '').replace(
                          '<br />', '').replace('<b>', '').replace('</b>',
                                                                   '').strip()

  return {'hasil: ': parafrase, 'Persentase: ': persen, 'Status: ': 'Sukses'}


def standard(words, mode='standard'):

  cookies = {
    'ci_session':
    'a%3A6%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%224082c58fb1409f705fdd2e0cecc76064%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A15%3A%22103.144.175.180%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A80%3A%22Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A109.0%29%20Gecko%2F20100101%20Firefox%2F115.0%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1690396146%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22checkauth%22%3Bs%3A25%3A%22checkparaphrase1690393811%22%3B%7Df0cb826f7a371c8dbcacb0081242ab50',
    '_pbjs_userid_consent_data': '6683316680106290',
    '_sharedID': '3544682c-cbd2-46be-ab04-89dacadcbd6f',
    '_sharedID_last': 'Wed%2C%2026%20Jul%202023%2017%3A50%3A13%20GMT',
    '_lr_retry_request': 'true',
    '_lr_env_src_ats': 'false',
    'cto_bundle':
    'RlCI3F9rUGVJQlJ3TiUyRlk4ajhPVW1sTUlFb0ZYWmE0Z3dCaTdzelhQeFh2N2JLTURIT2RnRmVHaW9BWENRcE5xTHU1aFc3MUFtTWpVcWREVThEV0JjMHNFd0tqM3UlMkJQTkFja1J4RjhhRzc2aGxScHdEOFVnU3lNVGJqWEJ4VUVQQk41JTJCMnRua3Z1QjNvUU14Q0d0ZTU4OVolMkJjdyUzRCUzRA',
    'cto_bidid':
    '4--XuV9iVDBodVM0Z2F5c05DR0N6TGslMkZEZHpLRkQ5Y21qdGVnJTJGeGdmbTE0Tkh4cDRmVW5KU2Q4d3c3NWlQRGdkaCUyQjhJYlpmNnpqN3IyNHBFa2hlVEVVZTRTUnc4R0hVZm1tZGt5QXZlQTNjdm01VmxpMWkyV1lUOTZHYmhUMzVPJTJCMEd0',
    '_ga_Q3XGSV1HE8': 'GS1.1.1690393813.1.0.1690393813.0.0.0',
    '_ga': 'GA1.2.1073571075.1690393814',
    'TawkConnectionTime': '0',
    'twk_idm_key': 'Tt8aWgRm5O4fYTxKWw4vM',
    '_ga_WGYTCZ2REQ': 'GS1.1.1690393814.1.0.1690393814.0.0.0',
    'twk_uuid_62ff0ee954f06e12d88f800b':
    '%7B%22uuid%22%3A%221.7xXuhykE54shomhhNsD76WzcW38KrPglJvS8WDkpJttRsWG3U4Z3grd8zEbcQyHkPOBQsa6Or3fBiq1hsSg5DnDW6TSB1sYY9KZ3DbnAqtmFeQq9E9z1LKRB%22%2C%22version%22%3A3%2C%22domain%22%3A%22paraphraser.io%22%2C%22ts%22%3A1690395354540%7D',
    '__gads':
    'ID=aaa45ab7366b4c7a:T=1690393815:RT=1690393815:S=ALNI_Ma0pKRQabLL3P82pFJwPqexy3GzBw',
    '__gpi':
    'UID=00000c2464462814:T=1690393815:RT=1690393815:S=ALNI_Ma6kG7fiZ_fy1kMxUUmi2MNsJEhhA',
    '_gid': 'GA1.2.1688706906.1690393816',
    '_cc_id': 'aefa69b06e99889d68d20b2ea5f6177',
    'panoramaId_expiry': '1690480218162',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://www.paraphraser.io',
    'Connection': 'keep-alive',
    'Referer': 'https://www.paraphraser.io/id/parafrase-online',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
  }

  data = {
    'data': words,
    'mode': '2',
    'lang': 'id',
    'captcha': '',
  }

  response = requests.post(
    'https://www.paraphraser.io/frontend/rewriteArticleBeta',
    cookies=cookies,
    headers=headers,
    data=data)

  # Remove HTML tags from the response text
  soup = BeautifulSoup(response.text, 'html.parser')
  text_without_tags = soup.get_text()

  # Convert the text without tags to a JSON object
  json_data = json.loads(text_without_tags)
  parafrase = json.dumps(json_data.get('result', {}).get('paraphrase'),
                         indent=4).replace('<span>', '').replace(
                           '</span>', '').replace('<br>', '').replace(
                             '<br/>',
                             '').replace('<br />',
                                         '').replace('<b>',
                                                     '').replace('</b>',
                                                                 '').strip()
  persen = json.dumps(json_data.get('result', {}).get('percent'),
                      indent=4).replace('<span>', '').replace(
                        '</span>',
                        '').replace('<br>', '').replace('<br/>', '').replace(
                          '<br />', '').replace('<b>', '').replace('</b>',
                                                                   '').strip()

  return {'hasil: ': parafrase, 'Persentase: ': persen, 'Status: ': 'Sukses'}


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/parafrase', methods=['GET'])
def parafrase():
  user_input = request.args.get('text', '')
  mode = request.args.get('mode', 'formal')  # Default mode is 'formal'

  if mode == 'formal':
    return jsonify(formal(user_input, mode='formal'))

  elif mode == 'regular':
    return jsonify(regular(user_input, mode='regular'))

  elif mode == 'fluency':
    return jsonify(fluency(user_input, mode='fluency'))

  elif mode == 'standard':
    return jsonify(standard(user_input, mode='standard'))

  elif user_input == '' or mode in [
      'formal', 'regular', 'fluency', 'standard'
  ]:
    return jsonify({
      'formal':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=formal',
      'regular':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=regular',
      'fluency':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=fluency',
      'standard':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=standard'
    })
  elif mode != ['formal', 'regular', 'fluency', 'standard']:
    return jsonify({
      'formal':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=formal',
      'regular':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=regular',
      'fluency':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=fluency',
      'standard':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=standard'
    })
  else:
    return jsonify({
      'formal':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=formal',
      'regular':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=regular',
      'fluency':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=fluency',
      'standard':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=standard'
    })


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/fb', methods=['GET'])
def get_fb_links():
  user_input = request.args.get('u')

  if not user_input:
    return jsonify(error='Missing URL parameter: ?u=USER_INPUT'), 400

  parsed_url = urlparse(user_input)
  if not parsed_url.scheme or not parsed_url.netloc:
    return jsonify(error='Invalid URL format.'), 400

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
    'Accept': '*/*',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Referer': 'https://fbdownloader.app/',
  }

  data = {
    'reCaptchaToken': '',
    'reCaptchaType': '',
    'k_exp': '1692074915',
    'k_token':
    'f0a3c7da35bec6b176a5942e74662fafc8eec8ec11a2afcd5d20fc0a07b4bd04',
    'k_verify': 'false',
    'q': user_input,
    'lang': 'id',
    'web': 'fbdownloader.app',
    'v': 'v2',
  }

  try:
    response = requests.post('https://v3.fbdownloader.app/api/ajaxSearch',
                             headers=headers,
                             data=data)
    response.raise_for_status()
  except requests.exceptions.RequestException as e:
    return jsonify(error='Failed to fetch the page.'), 500

  try:
    json_data = response.json()
    if 'data' in json_data and json_data['status'] == 'ok':
      html_content = json_data['data']
      soup = BeautifulSoup(html_content, 'html.parser')

      video_links = []
      links = soup.find_all('a', href=True)

      for link in links:
        if 'video' in link['href']:
          video_links.append(link['href'])

      if not video_links:
        return jsonify(
          error='No valid video links found on the provided URL.'), 404

      return jsonify(video_links), 200

    else:
      return jsonify(error='Invalid JSON data or no video links found.'), 404

  except ValueError:
    return jsonify(error='Invalid JSON response from the server.'), 500


cookies = {
  'csrftoken': 'e96c864a38447952921359c81c063b34',
  '_pinterest_sess':
  'TWc9PSZCc3VoelN5cXY4d3NJNy9ybXhrYUlhUU1paDZ6QVovNURZMENSOGFKcCtQL2FLTXVUdHB0WnlMejhnZVpoVlpmMEVnTEY4TEpLWXphZmNrVktLOVNsMXlhSGFDTGJxekVySzZrYSt1ZGNVR0hxQW1LV0tyVkZjczlJOVhpTVdHajRORHN4cDhjSmsvaUxUVDkrRVJUN0lhaXE2UHUwNTVya1E0ZnBraDJtTTl4WTZOUjE4c1ByZW9hbmhRQ09tUW1jQytjOHBLNEJHYXpDNkk5bXNrbGhkMnl4RWhHdnFLelRDRThpL0IxVTgvNVNYNGEvdVU5QzB0SHpSdEFJVTdsYW9iSHFNMHZ1ZzZNRUNoOUkrMGJkZ3hXQVdEYkYzVjBZS2gzalAxa3JpYURHWHdXMVlwc0pwcHNtajFkbitmelA5cWdKZlEvdUVHUnNSckYyS1p1Tkc3ck5neTR4cC9yTllpd2p1WHg1bGxibExMV2JvY0NQdjhIVXVoRTZOMDlLNllDYkR1dmltZlA2MG1tRlJnbXF3PT0maEJLT3BDN0JkSksra2JKMm9SdDh3RWc3UE1vPQ==',
  '_auth': '1',
  '__Secure-s_a':
  'Zy8xcnI1dGxWREpMbWdsS2JURmMzNUNheFkxZWJpZTZUVjNIaW5EL05WRnp4VUFNOWRCL1pGSmRROEtLcEN2a3FzcEJwYW5aZllEN3FscnJWZWNUWUtiaEdWNVArdDgwTUpKaEx6eVRTQURpNkJGNEFIK0NaQmxRc0lWb1dSMS9zWWdtQ2Jua01UYnI1MWhFZjF0Nk1Ub3hMTkxMVzlDUzZTVTM3cTFqTVJMT0QvSlJvcWVmWHd1QU9mMHhPQXBDRDY5VG84eTRDYUwvM21uUm96dTUwQlBsNDVIalppMHhHcTY2cVpGS1hocnVUZ000ZklNd01CcUNPYitNbVAxZlExbVdrd3plWHA2b3JTcTZzdDFWc0NsVlVzMnJCZm5qYWhGQjlKWnI3d1k9JlR1Ty9sRHBGVCt6MjNLSzVpeElBR3dJaTN0TT0=',
  '_b':
  '"AXIB1hgltO9FFLABvx5YoO+8kZfhSOQQ8lufnKl/QxxomKGORevSqFBGEMBrq8YRJ5U="',
  'cm_sub': 'none',
  '_routing_id': '"baf96f1d-14c8-4f7c-b8a3-ebd601afb94e"',
  'sessionFunnelEventLogged': '1',
}

headers = {
  'User-Agent':
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
  'Accept':
  'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
  'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
  'Upgrade-Insecure-Requests': '1',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'none',
  'Sec-Fetch-User': '?1',
  'Connection': 'keep-alive',
}


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/pin', methods=['GET'])
def get_pins():
  query = request.args.get('q', default='Kanao Tsuyuri', type=str)
  sanitized_query = html.escape(query)

  if not sanitized_query:
    error_message = f'error: {request.url}q=YOURINPUT'
    return jsonify({'error': error_message})

  params = {
    'q': sanitized_query,
    'rs': 'typed',
  }

  try:
    response = requests.get('https://id.pinterest.com/search/pins/',
                            params=params,
                            cookies=cookies,
                            headers=headers)
    response.raise_for_status(
    )  # Raise an exception if the response status code indicates an error
  except requests.RequestException as e:
    return jsonify({'error': f'Request to Pinterest failed: {e}'})

  soup = BeautifulSoup(response.text, 'html.parser')

  # Find all img tags with 'src' attribute
  img_tags = soup.find_all('img', {'src': True})

  # Extract and print the image URLs
  img_urls = [img_tag['src'] for img_tag in img_tags]
  return jsonify({'pins': img_urls})


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/pinhd', methods=['GET'])
def get_pins_hd():
  query = request.args.get('q', default='Kanao Tsuyuri', type=str)
  sanitized_query = bleach.clean(query)

  if not sanitized_query:
    error_message = f'error: {request.url}q=YOURINPUT'
    return jsonify({'error': error_message})

  params = {
    'q': sanitized_query,
    'rs': 'typed',
  }

  try:
    response = requests.get('https://id.pinterest.com/search/pins/',
                            params=params,
                            cookies=cookies,
                            headers=headers)
    response.raise_for_status(
    )  # Raise an exception if the response status code indicates an error
  except requests.RequestException as e:
    return jsonify({'error': f'Request to Pinterest failed: {e}'})

  soup = BeautifulSoup(response.text, 'html.parser')
  img_tags = soup.find_all('img', {'srcset': True})
  urls = []  # Create an empty list to store the URLs
  for img_tag in img_tags:
    srcset_value = img_tag['srcset']
    srcset_urls = [
      src.strip().split(' ')[0] for src in srcset_value.split(',')
      if 'originals' in src
    ]
    urls.extend(srcset_urls)  # Extend the list with the extracted URLs

  return jsonify({'pins': urls})


@app.route('/jadwal-mpl')
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_mpl_schedule():
  try:
    url = "https://id-mpl.com/schedule"
    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    with requests.Session() as s:
      r = s.get(url,
                headers=headers,
                allow_redirects=False,
                verify=True,
                timeout=5)
      r.raise_for_status()

    soup = BeautifulSoup(r.content, 'html.parser')

    pertandingan = soup.find_all('div', class_='offset-lg-1 col-lg-5 mb-4')
    pertandingan2 = soup.find_all('div', class_='col-lg-5 mb-4')
    all_pertandingan = pertandingan + pertandingan2

    match_data = []

    for i in all_pertandingan:
      date_time = i.find(
        'div', class_='match date py-1 py-lg-2 text-center').text.strip()

      matches = i.find_all(
        'div',
        class_='d-flex flex-row justify-content-between align-items-center')
      for match in matches:
        team1 = match.find(
          'div',
          class_=
          'team team1 d-flex flex-column justify-content-center align-items-center'
        )
        name1 = team1.find('div', class_='name').text.strip()

        team2 = match.find(
          'div',
          class_=
          'team team2 d-flex flex-column justify-content-center align-items-center'
        )
        name2 = team2.find('div', class_='name').text.strip()

        scores = match.find_all('div', class_='score font-primary')
        score1 = scores[0].text.strip() if scores else ''
        score2 = scores[1].text.strip() if len(scores) > 1 else ''

        details = match.find('a', class_='button-watch live detail')
        if details:
          onclick_attr = details.get('onclick')
          match_id = re.compile(r'openMatchDetail\((\d+)\)').search(
            onclick_attr).group(1)
          details = f"https://id-mpl.com/match-detail/{match_id}"
        else:
          details = "Belum dimulai"

        replay = match.find('a', class_='button-watch replay')
        replay_link = replay.get('href') if replay else "Belum tersedia"

        match_data.append({
          'team1': name1,
          'team2': name2,
          'score1': score1,
          'score2': score2,
          'date_time': date_time,
          'match_details': details,
          'match_replay': replay_link
        })

    return jsonify(match_data)

  except Exception as e:
    return jsonify({'error': str(e)}), 500


SAFE_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"


def is_valid_content_type(response):
  return "content-type" in response.headers and response.headers[
    "content-type"].lower().startswith("text/html")


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route("/googleimage", methods=["GET"])
@app.route("/gimg", methods=["GET"])
def get_google_images():
  query = request.args.get("q")

  if not query:
    return jsonify({"error": "Query parameter 'q' is required."}), 400

  if not (1 <= len(query) <= 1000):
    return jsonify(
      {"error": "Query length should be between 1 and 1000 characters."}), 400

  sanitized_query = html.escape(query)
  google_images = get_original_images(sanitized_query)
  return jsonify(google_images)


def get_original_images(query):
  google_images = []
  params = {"q": query, "tbm": "isch", "hl": "en", "gl": "us", "ijn": "0"}
  response = requests.get("https://www.google.com/search",
                          params=params,
                          headers={"User-Agent": SAFE_USER_AGENT})

  if response.status_code == 200 and is_valid_content_type(response):
    soup = BeautifulSoup(response.text, "lxml")  # Use lxml parser here

    all_script_tags = soup.select("script")
    matched_images_data = "".join(
      re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))
    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)

    matched_google_image_data = re.findall(
      r'\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}', matched_images_data_json)

    matched_google_images_thumbnails = re.findall(
      r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
      str(matched_google_image_data))

    thumbnails = [
      thumbnail.replace("\\u0026", "&")
      for thumbnail in matched_google_images_thumbnails
    ]

    removed_matched_google_images_thumbnails = re.sub(
      r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
      "", str(matched_google_image_data))

    matched_google_full_resolution_images = re.findall(
      r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
      removed_matched_google_images_thumbnails)

    full_res_images = [
      img.replace("\\u0026", "&")
      for img in matched_google_full_resolution_images
    ]

    for metadata, thumbnail, original in zip(
        soup.select(".isv-r.PNCib.MSM1fd.BUooTd"), thumbnails,
        full_res_images):
      google_images.append({
        "Author": "Arthon Senna (https://www.facebook.com/arthon.senna1122)",
        "title": metadata.select_one(".iGVLpd")["title"],
        "link": metadata.select_one(".iGVLpd")["href"],
        "source": metadata.select_one(".LAA3yd").text,
        "thumbnail": thumbnail,
        "original": original
      })

  return google_images


def sanitize_text(text):
  return text.replace('\n', ' ').replace('"', '&quot;')


@app.route('/whois', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_whois():
  domain = request.args.get('url', '')

  if not domain:
    return jsonify({'error': 'Missing domain parameter'}), 400

  if not domain.isascii() or len(domain) > 255:
    return jsonify({'error': 'Invalid domain format'}), 400

  url = f"https://www.whois.com/whois/{domain}"
  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0'
  }

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    data = soup.find_all("pre", class_="df-raw")

    whois_text = sanitize_text(data[0].text)
    return jsonify({'domain': domain, 'whois_data': whois_text})
  except requests.RequestException:
    return jsonify({'error': 'Failed to fetch data from WHOIS'}), 500


def resolve_dns(domain_name, all_ips, real_ips):
  try:
    ip_addresses = socket.getaddrinfo(domain_name, None)

    for ip in ip_addresses:
      all_ips.add(ip[4][0])

      if ip[1] == socket.SOCK_STREAM:
        real_ips.add(ip[4][0])
  except socket.gaierror:
    pass


@app.route('/subdomain', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_subdomains():
  domain = request.args.get('q', '')

  if not domain:
    return jsonify({'error': 'No domain provided'}), 400

  domain = domain.lower().strip()

  if domain.startswith('http://') or domain.startswith('https://'):
    domain = urlparse(domain).netloc

  # Retrieve certificate data
  session = requests.Session()
  url = f"https://crt.sh/?q={domain}&output=json"
  try:
    response = session.get(url,
                           headers={'User-Agent': 'Mozilla/5.0'},
                           timeout=5,
                           verify=True)
    response.raise_for_status()
  except requests.RequestException as e:
    return jsonify({'error': f'Failed to fetch data: {str(e)}'}), 500

  if response.status_code != 200:
    return jsonify({'error': 'Failed to fetch data because server down'}), 500

  json_data = json.loads(response.text)

  # Get unique domain names from the certificate data
  unique_domains = set()
  for data in json_data:
    name_value = data['name_value'].replace("*.",
                                            "").strip().replace("\n", " ")
    unique_domains.add(name_value)

  # Perform DNS resolution using threading
  all_ips = set()
  real_ips = set()
  threads = []

  for domain_name in unique_domains:
    thread = threading.Thread(target=resolve_dns,
                              args=(domain_name, all_ips, real_ips))
    threads.append(thread)
    thread.start()

  for thread in threads:
    thread.join()

  # Prepare JSON response
  response_data = {
    "unique_domains": sorted(list(unique_domains)),
    "all_ip_addresses": sorted(list(all_ips)),
    "real_ip_addresses": sorted(list(real_ips))
  }

  # Escape HTML content before rendering it in the response
  for key in response_data:
    if isinstance(response_data[key], list):
      response_data[key] = [escape(item) for item in response_data[key]]

  return jsonify(response_data)


@app.route('/simi', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def simi():
  valid_input_pattern = re.compile(r'^[a-zA-Z0-9\s]+$')
  text = request.args.get('text', '')

  # Validate user input
  if not valid_input_pattern.match(text):
    return jsonify({"error": "Invalid input."}), 400

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://simsimi.vn',
    'Alt-Used': 'simsimi.vn',
    'Connection': 'keep-alive',
    'Referer': 'https://simsimi.vn/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
  }

  data = {
    'text': text,
    'lc': 'id',
  }

  try:
    response = requests.post('https://simsimi.vn/web/simtalk',
                             headers=headers,
                             data=data)
    success = response.json().get('success')
    if success:
      return jsonify({"success": success})
    else:
      return jsonify({"error": "SimSimi response error."}), 500

  except Exception as e:
    print(e)
    return jsonify(
      {"error": "An error occurred while processing your request."}), 500


@app.route('/pindownload', methods=['GET'])
@app.route('/pindownloads', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def download_from_pinterest():
  url = request.args.get('url')

  if url is None:
    return jsonify({'error': 'Missing URL parameter'}), 400

  r = requests.get(url, allow_redirects=True)
  url = r.url

  cookies = {
    'csrftoken': 'e96c864a38447952921359c81c063b34',
    '_pinterest_sess':
    'TWc9PSZCc3VoelN5cXY4d3NJNy9ybXhrYUlhUU1paDZ6QVovNURZMENSOGFKcCtQL2FLTXVUdHB0WnlMejhnZVpoVlpmMEVnTEY4TEpLWXphZmNrVktLOVNsMXlhSGFDTGJxekVySzZrYSt1ZGNVR0hxQW1LV0tyVkZjczlJOVhpTVdHajRORHN4cDhjSmsvaUxUVDkrRVJUN0lhaXE2UHUwNTVya1E0ZnBraDJtTTl4WTZOUjE4c1ByZW9hbmhRQ09tUW1jQytjOHBLNEJHYXpDNkk5bXNrbGhkMnl4RWhHdnFLelRDRThpL0IxVTgvNVNYNGEvdVU5QzB0SHpSdEFJVTdsYW9iSHFNMHZ1ZzZNRUNoOUkrMGJkZ3hXQVdEYkYzVjBZS2gzalAxa3JpYURHWHdXMVlwc0pwcHNtajFkbitmelA5cWdKZlEvdUVHUnNSckYyS1p1Tkc3ck5neTR4cC9yTllpd2p1WHg1bGxibExMV2JvY0NQdjhIVXVoRTZOMDlLNllDYkR1dmltZlA2MG1tRlJnbXF3PT0maEJLT3BDN0JkSksra2JKMm9SdDh3RWc3UE1vPQ==',
    '_auth': '1',
    '__Secure-s_a':
    'Zy8xcnI1dGxWREpMbWdsS2JURmMzNUNheFkxZWJpZTZUVjNIaW5EL05WRnp4VUFNOWRCL1pGSmRROEtLcEN2a3FzcEJwYW5aZllEN3FscnJWZWNUWUtiaEdWNVArdDgwTUpKaEx6eVRTQURpNkJGNEFIK0NaQmxRc0lWb1dSMS9zWWdtQ2Jua01UYnI1MWhFZjF0Nk1Ub3hMTkxMVzlDUzZTVTM3cTFqTVJMT0QvSlJvcWVmWHd1QU9mMHhPQXBDRDY5VG84eTRDYUwvM21uUm96dTUwQlBsNDVIalppMHhHcTY2cVpGS1hocnVUZ000ZklNd01CcUNPYitNbVAxZlExbVdrd3plWHA2b3JTcTZzdDFWc0NsVlVzMnJCZm5qYWhGQjlKWnI3d1k9JlR1Ty9sRHBGVCt6MjNLSzVpeElBR3dJaTN0TT0=',
    '_b':
    '"AXIB1hgltO9FFLABvx5YoO+8kZfhSOQQ8lufnKl/QxxomKGORevSqFBGEMBrq8YRJ5U="',
    'cm_sub': 'none',
    '_routing_id': '"60b94b94-f128-4b5b-a6e3-832572c89098"',
    'sessionFunnelEventLogged': '1',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Connection': 'keep-alive',
  }

  cookies2 = {
    '_ga_D1XX1R246W':
    'GS1.1.1694198227.1.0.1694198227.0.0.0',
    '_ga':
    'GA1.2.1112282388.1694198227',
    '_gid':
    'GA1.2.665010725.1694198227',
    '_gat_gtag_UA_120752274_1':
    '1',
    '__gads':
    'ID=fc1466dab520a2b7-2299303e73e30070:T=1694198227:RT=1694198227:S=ALNI_MZXbmGQ_lYISVpZRSz0qmSGIvOJeg',
    '__gpi':
    'UID=00000c3e18927dda:T=1694198227:RT=1694198227:S=ALNI_MaqqMlKUCJ0G2gqLaLlqcTqwITGTg',
  }

  headers2 = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://www.expertsphp.com',
    'Alt-Used': 'www.expertsphp.com',
    'Connection': 'keep-alive',
    'Referer': 'https://www.expertsphp.com/pinterest-video-downloader.html',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
  }

  data = {
    'url': url,
  }

  response = requests.get(url, cookies=cookies, headers=headers)
  soup = BeautifulSoup(response.text, 'html.parser')

  response2 = requests.post(
    'https://www.expertsphp.com/facebook-video-downloader.php',
    cookies=cookies2,
    headers=headers2,
    data=data)
  soup2 = BeautifulSoup(response2.text, 'html.parser')

  result = []

  if soup.find_all('img', class_='hCL kVc L4E MIw N7A XiG'):
    for img in soup.find_all('img', class_='hCL kVc L4E MIw N7A XiG'):
      src = img.get('src')
      if src.endswith('.jpg') or src.endswith('.png'):
        result.append({'type': 'image', 'url': src})

  elif soup.find_all('img', class_='hCL kVc L4E MIw'):
    for img in soup.find_all('img', class_='hCL kVc L4E MIw'):
      src = img.get('src')
      if src.endswith('.gif'):
        result.append({'type': 'gif', 'url': src})

  elif soup.find_all('video', class_='hwa kVc MIw L4E'):
    for video in soup.find_all('video', class_='hwa kVc MIw L4E'):
      src = video.get('src')
      if src.endswith(('.mp4', '.webm', '.m4a', '.m4v', '.mov', '.avi', '.3gp',
                       '.flv', '.mkv')):
        result.append({'type': 'video', 'url': src})
    download_links = soup2.find_all(
      'a', class_='btn btn-primary btn-sm btn-block text-center')
    for link in download_links:
      href = link.get('href')
      result.append({'type': 'video', 'url': href})

  return jsonify(result)


@app.route('/summarize', methods=['GET', 'POST'])
def summarize_text():
  user_input = request.args.get('text')

  # Define the headers and data for the POST request
  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept': '*/*',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://summarizethis.com',
    'Alt-Used': 'summarizethis.com',
    'Connection': 'keep-alive',
    'Referer': 'https://summarizethis.com',
  }

  data = f'text={user_input}'

  # Send a POST request to summarizethis.com
  response = requests.post('https://summarizethis.com/summary.php',
                           headers=headers,
                           data=data)
  soup = BeautifulSoup(response.text, 'html.parser')

  # Extract the summarized text from the response
  summarized_text = soup.prettify()

  # Create a JSON response
  response_data = {
    'original_text': user_input,
    'summarized_text': summarized_text
  }

  return jsonify(response_data)


@app.route('/ringkas', methods=['GET', 'POST'])
def ringkas():
  if request.method == 'POST':
    user_input = request.form['text']

    user_input = user_input

    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
      'Accept': '*/*',
      'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
      'X-Requested-With': 'XMLHttpRequest',
      'Origin': 'https://summarizethis.com',
      'Alt-Used': 'summarizethis.com',
      'Connection': 'keep-alive',
      'Referer': 'https://summarizethis.com',
    }

    data = f'text={user_input}'

    # Send a POST request to summarizethis.com
    response = requests.post('https://summarizethis.com/summary.php',
                             headers=headers,
                             data=data)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the summarized text from the response
    summarized_text = soup.prettify()

    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Text Summarizer</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
                                      
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            color: #333;
        }

        h1 {
            text-align: center;
            padding: 20px;
        }

        form {
            text-align: center;
        }

        textarea {
            width: 80%;
            height: 150px;
            padding: 10px;
            margin: 10px auto;
            border: 1px solid #ccc;
            border-radius: 5px;
            resize: none;
        }

        input[type="submit"] {
            background-color: #007BFF;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }

        div {
            text-align: center;
            margin-top: 20px;
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }

        h2 {
            color: #007BFF;
        }

        /* Dark mode */
        .dark-mode {
            background-color: #333;
            color: #fff;
        }

        .dark-mode input[type="submit"] {
            background-color: #007BFF;
        }

        /* Berwarna hitam saat tema gelap */
        .dark-mode h2 {
            color: #000;
        }
                                      
        p{
            font-size: 15px;
            text-align: center;
            margin-top: 20px;
            margin-bottom: 20px;
            color: black;
        }

    </style>

    <script>
        // Function to toggle dark mode
        function toggleDarkMode() {
            const body = document.body;
            body.classList.toggle('dark-mode');
        }
    </script>
</head>
<body>
    <h1>Text Summarizer</h1>
    <form action="/ringkas" method="post">
        <textarea name="text" rows="10" cols="50">{{ user_input }}</textarea><br>
        <input type="submit" value="Summarize">
    </form>
    <div>
        <h2>Summarized Text</h2>
        <p class="output">{{ summarized_text|safe }}</p>
    </div>

    <button onclick="toggleDarkMode()">Toggle Dark Mode</button>
</body>
</html>
    ''',
                                  user_input=user_input,
                                  summarized_text=summarized_text)
  else:
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <title>Text Summarizer</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
                                      
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            color: #333;
        }

        h1 {
            text-align: center;
            padding: 20px;
        }

        form {
            text-align: center;
        }

        textarea {
            width: 80%;
            height: 150px;
            padding: 10px;
            margin: 10px auto;
            border: 1px solid #ccc;
            border-radius: 5px;
            resize: none;
        }

        input[type="submit"] {
            background-color: #007BFF;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }

        div {
            text-align: center;
            margin-top: 20px;
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }

        h2 {
            color: #007BFF;
        }

        /* Dark mode */
        .dark-mode {
            background-color: #333;
            color: #fff;
        }

        .dark-mode input[type="submit"] {
            background-color: #007BFF;
        }

        /* Berwarna hitam saat tema gelap */
        .dark-mode h2 {
            color: #000;
        }
                                      
        p{
            font-size: 15px;
            text-align: center;
            margin-top: 20px;
            margin-bottom: 20px;
            color: black;
        }

    </style>

    <script>
        // Function to toggle dark mode
        function toggleDarkMode() {
            const body = document.body;
            body.classList.toggle('dark-mode');
        }
    </script>
</head>
        <body>
            <h1>Text Summarizer</h1>
            <form action="/ringkas" method="post">
                <textarea name="text" rows="10" cols="50"></textarea><br>
                <input type="submit" value="Summarize">
            </form>
            <div>
                <h2>Summarized Text</h2>
                <p class="output"></p>
            </div>
            <button onclick="toggleDarkMode()">Toggle Dark Mode</button>
        </body>
        </html>
''')


@app.route('/ip-tracker')
@cross_origin()
@cache.cached(timeout=7200, query_string=True)
def ip_tracker():
  ip_address = request.args.get('ip')
  if not ip_address:
    return jsonify({
      'error': 'IP address not provided',
      'parameter': '/ip-tracker?ip=YourIP'
    })

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept': '*/*',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Origin': 'https://ip-api.com',
    'Connection': 'keep-alive',
    'Referer': 'https://ip-api.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
  }

  params = {
    'fields': '66842623',
    'lang': 'en',
  }

  response = requests.get(f'https://demo.ip-api.com/json/{ip_address}',
                          params=params,
                          headers=headers)

  data = response.json()

  maps_url = f"https://www.google.com/maps/search/?api=1&query={data['lat']},{data['lon']}"

  data['maps_url'] = maps_url

  return jsonify(data)


@app.route('/lirik', methods=['GET'])
@app.route('/lyrics', methods=['GET'])
@app.route('/liriks', methods=['GET'])
def get_lyrics():
  cookies = {
    '_ga_WEHLQ2S9TQ': 'GS1.1.1697208313.1.1.1697208634.30.0.0',
    '_ga': 'GA1.1.1716489394.1697208314',
    '__hstc':
    '124805269.11d8bfb3e8608642411e06fbf65b860c.1697208323677.1697208323677.1697208323677.1',
    'hubspotutk': '11d8bfb3e8608642411e06fbf65b860c',
    '__hssrc': '1',
    '__hssc': '124805269.5.1697208323677',
    '_ga_6RNSJ3SZP2': 'GS1.1.1697208452.1.1.1697208581.0.0.0',
    '_hjSessionUser_3540160':
    'eyJpZCI6IjljODA5NDgyLTY1ZWEtNWU2My05MDhlLTVhNTJiNTNhMDQ5ZCIsImNyZWF0ZWQiOjE2OTcyMDg0NTYyNzUsImV4aXN0aW5nIjp0cnVlfQ==',
    '_hjFirstSeen': '1',
    '_hjIncludedInSessionSample_3540160': '0',
    '_hjSession_3540160':
    'eyJpZCI6ImI5YzU2Y2QyLTJlNDQtNGZkNC1hY2M2LTg0MDNjYjA3MmE0MiIsImNyZWF0ZWQiOjE2OTcyMDg0NTYyNzYsImluU2FtcGxlIjpmYWxzZSwic2Vzc2lvbml6ZXJCZXRhRW5hYmxlZCI6dHJ1ZX0=',
    '_hjAbsoluteSessionInProgress': '0',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
  }
  user_input = request.args.get('lagu')
  nama = user_input.replace(" ", "-").replace("%20", "-").replace("+",
                                                                  "-").lower()

  response = requests.get(f'https://lyrics.lyricfind.com/lyrics/{nama}',
                          cookies=cookies,
                          headers=headers)

  soup = BeautifulSoup(response.text, 'html.parser')

  script_tag = soup.find("script", id="__NEXT_DATA__")
  script_content = script_tag.string

  datas = json.loads(script_content)

  try:
    release_year = datas["props"]["pageProps"]["songData"]["track"]["album"][
      "releaseYear"]
  except KeyError:
    release_year = "Not-Available"

  elements_to_extract = [
    'copyright', 'lyrics', 'coverArt', 'title', 'releaseYear', 'artist'
  ]

  data = {}

  for element in elements_to_extract:
    pattern = rf'"{element}":"(.*?)",'
    match = re.search(pattern, response.text)

    if match:
      data[element] = match.group(1).replace("\\n",
                                             "\n").replace("\\u0027",
                                                           "'").strip()
    else:
      data[element] = "Not-Available"

  formatted_lyrics = data['lyrics'].strip()
  formatted_cover_art = "https://lyrics.lyricfind.com/_next/image?url=http://images.lyricfind.com/images/" + data[
    'coverArt'].strip() + "&w=3840&q=75"
  source = f"https://lyrics.lyricfind.com/lyrics/{nama}"

  result = {
    "lyrics": formatted_lyrics,
    "cover": formatted_cover_art,
    "hak_cipta": data['copyright'],
    "judul": data['title'].title(),
    "tahun_rilis": release_year,
    "artis": data['artist'].replace('-', ' ').title(),
    "sumber": source
  }

  return jsonify(result)


# # Buat objek UserAgent
# user_agent = UserAgent()

# # Dapatkan user agent acak
# random_user_agent = user_agent.random

google_sites = [
  "google.com", "google.ad", "google.ae", "google.com.af", "google.com.ag",
  "google.al", "google.am", "google.co.ao", "google.com.ar", "google.as",
  "google.at", "google.com.au", "google.az", "google.ba", "google.com.bd",
  "google.be", "google.bf", "google.bg", "google.com.bh", "google.bi",
  "google.bj", "google.com.bn", "google.com.bo", "google.com.br", "google.bs",
  "google.bt", "google.co.bw", "google.by", "google.com.bz", "google.ca",
  "google.cd", "google.cf", "google.cg", "google.ch", "google.ci",
  "google.co.ck", "google.cl", "google.cm", "google.cn", "google.com.co",
  "google.co.cr", "google.com.cu", "google.cv", "google.com.cy", "google.cz",
  "google.de", "google.dj", "google.dk", "google.dm", "google.com.do",
  "google.dz", "google.com.ec", "google.ee", "google.com.eg", "google.es",
  "google.com.et", "google.fi", "google.com.fj", "google.fm", "google.fr",
  "google.ga", "google.ge", "google.gg", "google.com.gh", "google.com.gi",
  "google.gl", "google.gm", "google.gr", "google.com.gt", "google.gy",
  "google.com.hk", "google.hn", "google.hr", "google.ht", "google.hu",
  "google.co.id", "google.ie", "google.co.il", "google.im", "google.co.in",
  "google.iq", "google.is", "google.it", "google.je", "google.com.jm",
  "google.jo", "google.co.jp", "google.co.ke", "google.com.kh", "google.ki",
  "google.kg", "google.co.kr", "google.com.kw", "google.kz", "google.la",
  "google.com.lb", "google.li", "google.lk", "google.co.ls", "google.lt",
  "google.lu", "google.lv", "google.com.ly", "google.co.ma", "google.md",
  "google.me", "google.mg", "google.mk", "google.ml", "google.com.mm",
  "google.mn", "google.com.mt", "google.mu", "google.mv", "google.mw",
  "google.com.mx", "google.com.my", "google.co.mz", "google.com.na",
  "google.com.ng", "google.com.ni", "google.ne", "google.nl", "google.no",
  "google.com.np", "google.nr", "google.nu", "google.co.nz", "google.com.om",
  "google.com.pa", "google.com.pe", "google.com.pg", "google.com.ph",
  "google.com.pk", "google.pl", "google.pn", "google.com.pr", "google.ps",
  "google.pt", "google.com.py", "google.com.qa", "google.ro", "google.ru",
  "google.rw", "google.com.sa", "google.com.sb", "google.sc", "google.se",
  "google.sh", "google.si", "google.sk", "google.com.sl", "google.sn",
  "google.so", "google.sm", "google.sr", "google.st", "google.com.sv",
  "google.td", "google.tg", "google.co.th", "google.com.tj", "google.tl",
  "google.tm", "google.tn", "google.to", "google.com.tr", "google.tt",
  "google.com.tw", "google.co.tz", "google.com.ua", "google.co.ug",
  "google.co.uk", "google.com.uy", "google.co.uz", "google.com.vc",
  "google.co.ve", "google.co.vi", "google.com.vn", "google.vu", "google.ws",
  "google.rs", "google.co.za", "google.co.zm", "google.co.zw", "google.cat"
]


def search_google(query, headers):
  # Shuffle the list of Google sites for randomization
  random.shuffle(google_sites)

  for site in google_sites:
    search_url = f"https://www.{site}/search"
    params = {
      'q': query,
    }

    response = requests.get(search_url, params=params, headers=headers)

    # Check if the search was successful (You can define your own criteria)
    if "Hasil pencarian tidak ditemukan" not in response.text or "Tidak ada hasil pencarian yang ditemukan" not in response.text or response.status_code == 404:
      soup = BeautifulSoup(response.text, 'html.parser')
      div = soup.find('div', class_='xaAUmb')
      result = []

      result.append(
        soup.find('div', class_='PZPZlf ssJ7i B5dxMb').text.strip())
      result.append(soup.find('div', class_='iAIpCb PZPZlf').text.strip())

      # give newline
      result.append("")

      for i in div.find_all('span'):
        result.append(i.text.strip())

      return result

    time.sleep(random.uniform(3, 5))

  return []


@app.route('/googlelirik', methods=['GET'])
@cross_origin()
@cache.cached(timeout=7200, query_string=True)
def google_lirik():
  user_input = request.args.get('lagu')

  if not user_input:
    return jsonify({
      'error':
      request.host_url + 'googlelirik?lagu=Nadhif+basalamah+penjaga+hati'
    }), 200

  query = f"{user_input}+lyrics"

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Alt-Used': 'www.google.com',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
  }

  search_result = search_google(query, headers)

  if search_result:
    return jsonify({'result': search_result})
  else:
    return jsonify({'error': 'No search results found'})


@app.route('/igstory', methods=['GET'])
@app.route('/igs', methods=['GET'])
@app.route('/storyig', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_instagram_story():
  if request.method == 'GET':
    user_input = request.args.get('url')
  else:
    return jsonify({'error': 'Method not allowed'})

  if user_input:
    user_input = escape(user_input)
  else:
    return jsonify({
      'error':
      'Please provide a valid Instagram story URL',
      'example':
      request.host_url +
      'igstory?url=https://www.instagram.com/stories/highlights/17860230305961018/',
      'example2':
      request.host_url +
      'igstory?url=https://www.instagram.com/stories/instagram/'
    })

  # if not user_input:
  #     return jsonify({'error': 'Please provide a valid Instagram story URL',
  #                     'example': request.host_url + 'igstory?url=https://www.instagram.com/stories/highlights/17860230305961018/',
  #                     'example2': request.host_url + 'igstory?url=https://www.instagram.com/stories/instagram/2687722349609598831/'})

  cookies = {
    'uid':
    '98390561706a89a0',
    'adsPopupClick':
    '54',
    'helperWidget':
    '96',
    '_ga_99VS1KX9CV':
    'GS1.1.1696774111.1.1.1696774521.0.0.0',
    '_ga':
    'GA1.1.80242225.1696774112',
    '_ga_V9ECHR065F':
    'GS1.1.1696774119.1.1.1696774522.0.0.0',
    '__gads':
    'ID=fe02ca7d154b2815:T=1696774116:RT=1696774518:S=ALNI_MbsMBLJOX6Ofyf9hlUtv3AxIuaXkw',
    '__gpi':
    'UID=00000c5aeff7ed21:T=1696774116:RT=1696774518:S=ALNI_MYpdx21b767fCzOhfajQsbOrDvfeA',
    'FCNEC':
    '^%^5B^%^5B^%^22AKsRol_KYC1jctLJ7OzzBnBtQBOK2qGYSTHvgBuaTMD8Ct5J-5vTAxdU_tqbEcS7eQZszI7XKi5MLbwuedBxBCA1lIY-QyknBTU_caA5oJOmUUYdzAbJq6DjC5vrPx_kJNzxGGOqV9mcMUyd6HdLMLPCSJ4oTkaL9A^%^3D^%^3D^%^22^%^5D^%^2Cnull^%^2C^%^5B^%^5D^%^5D',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'If-None-Match': 'W/2b3e3-0W3dahNAbvWq7gRreKTNcnBACxk',
  }

  try:
    response = requests.get(
      f'https://igram.world/api/ig/story?url={user_input}',
      cookies=cookies,
      headers=headers)
  except:
    return jsonify({'error': 'Failed to fetch Instagram story data'})

  # if not response.ok:
  #     return jsonify({'error': 'Failed to fetch Instagram story data'})

  data = json.loads(response.text)

  result = []

  start = 1

  for i in data['result']:
    video_versions = i['video_versions']
    for j, video in enumerate(video_versions):
      result.append({'url': video['url']})  #, 'index': j + start})
    start += len(video_versions)

  # return jsonify({'instagram_story_videos': result})
  return jsonify(result)


@app.route('/checkdata', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def check_data():
  email = request.args.get('email')
  if not email:
    return jsonify({
      'error':
      'Email is required',
      'path':
      request.host_url + 'checkdata?email=abc@gmail.com',
      'warning':
      'if you can\'t find the data, try again refresh. make sure the data is correct, good, and valid.'
    })

  try:
    valid = validate_email(email)
    email = valid.email
  except EmailNotValidError as e:
    # return jsonify({'error': "Invalid email address"})
    pass

  headers = {
    'User-Agent': random_user_agent,
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://periksadata.com',
    'Alt-Used': 'periksadata.com',
    'Connection': 'keep-alive',
    'Referer': 'https://periksadata.com',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
  }

  data = f'email={email}'
  response = requests.post('https://periksadata.com',
                           headers=headers,
                           data=data)
  data_json = {'results': []}

  if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('div', class_='col-md-6')

    for p in paragraphs:
      title_element = p.find('h5')
      if title_element:
        title = title_element.text.strip()
        link = 'https://periksadata.com' + p.find('a')['href']
        response2 = requests.get(link, headers=headers)
        soup2 = BeautifulSoup(response2.text, 'html.parser')
        lead_paragraph = soup2.find('p', class_='lead')
        if lead_paragraph:
          description = lead_paragraph.text.strip()[:-45]
        else:
          description = 'No lead paragraph found'

        data_leaked = soup2.find_all(
          'span', class_='label label--inline text-center rounded')
        data_leaked_text = ' , '.join(leak.text.strip()
                                      for leak in data_leaked)

        paragraphs = p.find_all('p')
        data = []

        for para in paragraphs:
          parts = para.find_all('b')
          if len(parts) >= 2:
            label = parts[0].text.strip()
            datas = parts[2].text.strip()
            data.append({
              'Tanggal Kejadian': label,
              'Data yang bocor': data_leaked_text,
              'Total keseluruhan data yang bocor': datas
            })

        result = {
          'title': title,
          'link': link,
          'description': description,
          'data': data,
        }
        data_json['results'].append(result)

    return jsonify({
      "User-Agent": random_user_agent,
      "Email": email,
      "Data": data_json
    })
  else:
    return jsonify({'error': 'Request failed'})


def is_valid_query_bing(query):
  try:
    result = urlparse(query)
    if not all([result.scheme, result.netloc]):
      return True
    return False
  except ValueError:
    return True


def bing_extract_results(result):
  link = result.find('a', href=True)
  paragraph = result.find('p', class_='b_lineclamp4 b_algoSlug')

  if link:
    href = link['href']
    if paragraph:
      return {
        "link": escape(href),
        "paragraph": escape(paragraph.text.strip())
      }
    else:
      return {"link": escape(href)}
  return None


@app.route('/bing', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def bing_search():
  query = request.args.get('search', type=str)

  if not query:
    return jsonify({"error": "Missing 'search' parameter"}), 400

  if not is_valid_query_bing(query):
    return jsonify({"error": "Invalid Query"}), 400

  response_dict = {"query": escape(query), "suggestions": [], "results": []}

  suggestion_url = "https://www.bing.com/AS/Suggestions?pt=page.home&mkt=en-us&qry=" + query + "&cp=0&msbqf=false&cvid=C41C6A7A87F04011ABDD42AE95D1E8FA"
  try:
    suggestion_response = requests.get(suggestion_url, timeout=(3, 10))
    suggestion_response.raise_for_status()
    suggestion_soup = BeautifulSoup(suggestion_response.text, "html.parser")
    suggestion_items = suggestion_soup.select("li")

    for item in suggestion_items:
      response_dict["suggestions"].append(escape(item.text))
  except requests.RequestException as e:
    return jsonify({"error": f"Suggestions Error: {escape(str(e))}"}), 500

  search_url = "https://www.bing.com/search?q=" + query
  search_response = None
  max_attempts = 3
  attempts = 0

  while attempts < max_attempts:
    try:
      session = requests.Session()
      retries = Retry(total=max_attempts,
                      backoff_factor=0.1,
                      status_forcelist=[500, 502, 503, 504])
      session.mount('http://', HTTPAdapter(max_retries=retries))
      session.mount('https://', HTTPAdapter(max_retries=retries))

      search_response = session.get(search_url, timeout=(3, 10))
      search_response.raise_for_status()
      break
    except requests.RequestException as e:
      attempts += 1
      return jsonify({
        "error":
        f"Search Error: {escape(str(e))}. Retrying... (Attempt {attempts}/{max_attempts})"
      }), 500
    finally:
      session.close()

  if search_response:
    search_soup = BeautifulSoup(search_response.text, 'html.parser')
    results = search_soup.find_all('li', class_='b_algo')

    for result in results:
      extracted_result = bing_extract_results(result)
      if extracted_result:
        response_dict["results"].append(extracted_result)

  return jsonify(response_dict)


@app.route('/capcut', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def capcut():
  url = request.args.get('url')
  if not url:
    return jsonify({
      'error': 'Please provide a URL',
      'path': request.host_url + 'capcut?url='
    }), 400

  try:
    response = requests.get(url, allow_redirects=True)
    final_url = response.url

    parsed_url = urlparse(final_url)
    query_params = parse_qs(parsed_url.query)
    template_id = query_params.get('template_id', [None])[0]

    cookies = {
      'sign':
      'ee91c179ecb91d7a44ff11788fd51b41',
      'device-time':
      '1700914774742',
      '__gads':
      'ID=124f7541a82c49ee:T=1700921579:RT=1700921579:S=ALNI_MYF-Z27MZ7J3Jt4WoCbkgwBC0zPXQ',
      '__gpi':
      'UID=00000c991aa99290:T=1700921579:RT=1700921579:S=ALNI_MZG60pqTASjxuHqO13s0Y7YgTtsHg',
    }

    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
      'Accept': 'application/json, text/plain, */*',
      'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
      'Alt-Used': 'ssscap.net',
      'Connection': 'keep-alive',
      'Referer': 'https://ssscap.net/',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
    }

    if template_id:
      response = requests.get('https://ssscap.net/api/download/' + template_id,
                              cookies=cookies,
                              headers=headers)

      if response.status_code == 200:
        json_data = response.json()
        if json_data['code'] == 200:
          decod = json_data['originalVideoUrl'].replace('/api/cdn/', '')
          padding = len(decod) % 4

          if padding:
            decod += '=' * (4 - padding)

          decoded_original_video_url = base64.b64decode(decod).decode('utf-8')

          result = {
            'title': json_data['title'],
            'description': json_data['description'],
            'usage': json_data['usage'],
            'video_url': decoded_original_video_url
          }

          return jsonify(result)
        else:
          return jsonify({
            'error':
            f"Request failed with status code {response.status_code}"
          }), 500
      else:
        return jsonify(
          {'error':
           f"Request failed with status code {response.status_code}"}), 500
    else:
      return jsonify({'error': 'Template ID not found in the URL'}), 400

  except Exception as e:
    return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/instagramdl', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def instagram_download():
  user_input = request.args.get('url')

  if user_input is None:
    return jsonify({
      'error': 'URL not found',
      'path': request.host_url + "instagramdl?url="
    }), 200

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': '*/*',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://www.w3toys.com',
    'Connection': 'keep-alive',
    'Referer': 'https://www.w3toys.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
  }

  data = {
    'url': user_input,
    'host': 'instagram',
  }

  response = requests.post('https://www.w3toys.com/core/ajax.php',
                           headers=headers,
                           data=data)

  soup = BeautifulSoup(response.text, 'html.parser')

  download_url_element = soup.find('a', {'class': 'btn btn-red mt-2'})
  img_src_element = soup.find('img', {'class': 'img-fluid img-thumbnail'})

  if download_url_element and img_src_element:
    download_url = download_url_element['href']
    decoded_url = unquote(download_url.split('url=')[1])
    decoded_url_base64 = base64.b64decode(decoded_url)

    img_src = img_src_element['src']

    response_data = {'video': decoded_url_base64.decode(), 'image': img_src}

    return jsonify(response_data)
  else:
    return jsonify({
      'error': 'Elements not found',
      'path': request.host_url + "instagramdl?url="
    }), 200


def scrape_bioskop(base_url, search_term, pages=2):
  complete = f"?s={search_term}&post_type%5B%5D=post&post_type%5B%5D=tv"
  results = []

  for page in range(1, pages + 1):
    full_url = f"{base_url}page/{page}/{complete}"
    r = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'})

    if r.status_code == 200:
      soup = BeautifulSoup(r.text, 'html.parser')
      entries = soup.find_all('div', class_='content-thumbnail text-center')
      title = soup.find_all('h2', class_='entry-title', itemprop='headline')

      for entry, judul in zip(entries, title):
        a_tag = judul.find('a')
        if a_tag:
          judulbioskop = a_tag.get_text(strip=True)

        title_tag = entry.find('a', itemprop='url')
        if title_tag:
          href = title_tag.get('href')
          title = title_tag.get_text(strip=True)
          img_tag = entry.find('img', itemprop='image')
          if img_tag:
            img_src = img_tag.get('src')
            result = {
              "URL": full_url,
              "Title": judulbioskop,
              "Href": href,
              "Img": img_src
            }
            results.append(result)
    else:
      pass

  return results


def scrape_other_url(url):
  r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
  soup = BeautifulSoup(r.text, 'html.parser')
  films = soup.find_all('div', class_='ml-item')
  results = []

  for film in films:
    result = {
      "Title": film.find('img')['alt'],
      "Info": film.find('span', class_='mli-info').text,
      "Rating": film.find('span', class_='mli-rating').text,
      "Href": film.find('a')['href'],
      "Img": film.find('img')['src']
    }
    results.append(result)

  return results


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/bioskop', methods=['GET'])
def bioskop():
  search_term = request.args.get('search')
  if not search_term:
    return jsonify({
      "error": "Search term is required",
      "path": request.host_url + 'bioskop?search=naruto'
    }), 200

  base_urls = ['http://109.123.251.95/', 'https://165.232.85.56/']

  bioskop_results = []
  for base_url in base_urls:
    bioskop_results.extend(scrape_bioskop(base_url, search_term))

  other_url = f"http://179.43.163.54/?s={search_term}"
  other_results = scrape_other_url(other_url)

  return jsonify({"bioskop": bioskop_results, "other": other_results})
