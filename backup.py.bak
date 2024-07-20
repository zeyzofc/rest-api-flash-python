from flask import Flask, request, jsonify, redirect, url_for, make_response
from flask_caching import Cache
from flask_cors import CORS, cross_origin
import requests, random, hashlib, time, urllib, traceback, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fake_useragent import UserAgent
from datetime import datetime, timedelta

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

cache = Cache(app,
              config={
                'CACHE_TYPE': 'simple',
                'CACHE_DEFAULT_TIMEOUT': 3600
              })


# read user agents from file and cache it
@cache.memoize()
def get_user_agents():
  with open('user_agents.txt', 'r') as f:
    return [line.strip() for line in f.readlines()]


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
  return redirect(url_for('index'))


def generate_visitor_id():
  timestamp = str(time.time())
  md5_hash = hashlib.md5(timestamp.encode()).hexdigest()
  return md5_hash


def generate_cookie(visitor_id):
  timestamp = str(time.time())
  sha1_hash = hashlib.sha1((timestamp + visitor_id).encode()).hexdigest()
  return sha1_hash


@app.route('/kanjiname', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def kanji_name():
  nama = request.args.get('nama')
  url = f"https://jepang-indonesia.co.id/kanjiname/convert?name={nama}&x=73&y=48"

  headers = {
    'User-Agent':
    'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'
  }

  response = requests.get(url, headers=headers)

  soup = BeautifulSoup(response.text, 'html.parser')

  # get url from this my server menggunakan requests host

  server = f"{request.host_url}kanjiname?nama={nama}"

  result = {
    'kanji':
    soup.find('div', {
      'class': 'text-center rounded-box hanzi'
    }).text.strip(),
    'arti':
    soup.find('div', {
      'class': 'text-center meantext'
    }).text.strip(),
    'original':
    nama,
    'server':
    server
  }

  return jsonify(result)


@app.route('/translate', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def translate():
  from_lang = request.args.get('from', 'en')
  to_lang = request.args.get('to', 'id')
  text = request.args.get('text', '')

  # set up headers
  headers = {
    'User-Agent': random.choice(get_user_agents()),
    'Referer': 'http://translate.google.com/',
    'Origin': 'http://translate.google.com/'
  }

  # send request to Google Translate API
  url = f'https://translate.google.com/translate_a/single?client=gtx&sl={from_lang}&tl={to_lang}&dt=t&q={text}'
  response = requests.get(url, headers=headers)

  # extract translated text from response
  result = response.json()
  if result is not None and len(result) > 0 and len(result[0]) > 0:
    translated_text = result[0][0][0]
  else:
    translated_text = 'Translation failed'

  # return result as JSON
  return jsonify({
    'code/status': response.status_code,
    'from': from_lang,
    'to': to_lang,
    'text': text,
    'user_agent': headers['User-Agent'],
    'translated_text': translated_text,
    'credits': 'Xnuvers007 ( https://github.com/xnuvers007 )'
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

    profile = soup.select_one(
      "#user-page > div.user > div.row > div > div.user__img"
    )["style"].replace("background-image: url('", "").replace("');", "")
    fullname = soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > div > a > h1"
    ).get_text()
    username = soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > div > h4"
    ).get_text()
    post = soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > ul > li:nth-child(1)"
    ).get_text().replace(" Posts", "")
    followers = soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > ul > li:nth-child(2)"
    ).get_text().replace(" Followers", "")
    following = soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > ul > li:nth-child(3)"
    ).get_text().replace(" Following", "")
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
      "url": f"https://www.instagram.com/{username.replace('@', '')}"
    }

    return result, response.status_code

  except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
      raise Exception("Error: Account not found")
    elif e.response.status_code == 403:
      raise Exception("Error: Account is private")
    else:
      # redirect('https://tr.deployers.repl.co/igstalk?user=Indradwi.25')
      redirect(url_for('index'))


@app.route('/igstalk')
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def igstalk_route():
  username = request.args.get('user')

  if not username:
    # return jsonify({"error": "Missing username parameter"}), 400
    #   return redirect('https://tr.deployers.repl.co/igstalk?user=Indradwi.25'), 400
    return redirect(url_for('/'))

  try:
    result, status_code = igstalk(username)
    result["status"] = status_code
    result["credits"] = "Xnuvers007 (https://github.com/Xnuvers007)"
    return jsonify(result), status_code

  except Exception as e:
    return jsonify({"error": str(e)}), 500


#   return redirect(
#     '/translate?from=en&to=id&text=hello, im Xnuvers007, Im the developer')


@app.route('/')
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def index():
  visitor_id = generate_visitor_id()
  cookie = generate_cookie(visitor_id)
  # Mendapatkan tanggal saat ini
  current_date = datetime.now()

  # Menghitung tanggal kadaluwarsa (7 hari dari tanggal saat ini)
  expiration_date = current_date + timedelta(days=7)
  response = make_response('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- HTML Meta Tags -->
<meta name="description" content="Website penyedia layanan data APIs JSON">
<meta property="og:description" content="Website penyedia layanan data APIs JSON">
<meta property="og:title" content="APIs Website">
    <meta name="description" content="API">
    <meta name="keywords" content="API">
    <meta name="author" content="Xnuvers007">
    <meta name="og:author" content="Xnuvers007">
    <meta property="og:video" content="https://l.top4top.io/m_27030310v1.mp4">


<!-- Google / Search Engine Tags-->
<meta itemprop="name" content="Xnuvers007">
<meta itemprop="description" content="Website penyedia layanan data APIs JSON">
<meta itemprop="image" content="https://t4.ftcdn.net/jpg/03/22/95/69/360_F_322956978_9ESBVewTYdhSu9G6qf2JazX9tUsdh53g.jpg">
<meta property="og:image" content="https://t4.ftcdn.net/jpg/03/22/95/69/360_F_322956978_9ESBVewTYdhSu9G6qf2JazX9tUsdh53g.jpg">
<link rel="icon" href="https://t4.ftcdn.net/jpg/03/22/95/69/360_F_322956978_9ESBVewTYdhSu9G6qf2JazX9tUsdh53g.jpg" type="image/x-icon">

<!-- Facebook Meta Tags-->
<meta property="og:url" content="https://tr.deployers.repl.co">
<meta property="og:type" content="website">

<!-- Twitter Meta Tags-->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="APIs Website">
<meta name="twitter:description" content="Website penyedia layanan data APIs JSON">
<meta name="twitter:image" content="https://t4.ftcdn.net/jpg/03/22/95/69/360_F_322956978_9ESBVewTYdhSu9G6qf2JazX9tUsdh53g.jpg">
<!-- Meta Tags Generated via https://github.com/Xnuvers007/Meta-Generator -->

    
    <meta property="og:title" content="API Documentation">
    <title>API</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet" crossorigin="anonymous">
    <style>
        body {
            background-color: #f8f9fa;
            color: #212529;
        }
        pre {
            background-color: #f8f8f8;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
        }

        .dark-mode pre,
        .dark-mode code
        {
            background-color: #212529;
            color: #f8f9fa;
        }

        code {
            font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
            font-size: 14px;
            color: #333;
        }
                
        .dark-mode th,
        .dark-mode td {
            color: #f8f9fa;
        }

        .container {
            text-align: center;
            margin-top: 100px;
        }

        h1 {
            margin-bottom: 20px;
        }

        p {
            margin-bottom: 10px;
        }

        ul {
            text-align: left;
            padding-left: 0;
        }

        ul li {
            list-style-type: none;
            margin-bottom: 10px;
        }

        .dark-mode {
            background-color: #212529;
            color: #f8f9fa;
        }

        .toggle-container {
            margin-top: 20px;
            text-align: center;
        }

        .toggle-label {
            margin-right: 10px;
        }
    .image-container {
        display: none;
    }

    .show-image .table-responsive {
        display: none;
    }

    .show-image .image-container {
        display: block;
    }

    .show-image .show-image-btn {
        display: none;
    }

    .show-table .table-responsive {
        display: block;
    }

    .show-table .image-container {
        display: none;
    }

    .show-table .show-image-btn {
        display: block;
    }

    @media (max-width: 576px) {
        .container {
            margin-top: 50px;
        }

        h2 {
            font-size: 24px;
        }

        .table-responsive {
            overflow-x: auto;
        }
    }
      .custom-list {
    list-style-type: none; /* Remove default numbering/bullets */
    counter-reset: my-counter; /* Initialize custom counter */
    padding-left: 0; /* Remove default indentation */
  }

  .custom-list li {
    counter-increment: my-counter; /* Increment custom counter */
    margin-bottom: 0.5em; /* Optional: Adjust spacing between list items */
    color: green;
  }

  .custom-list li::before {
    content: counter(my-counter); /* Display custom counter */
    font-weight: bold; /* Optional: Adjust the appearance of the custom counter */
    margin-right: 0.5em; /* Optional: Adjust spacing between the counter and list item content */
  }
</style>
</head>
<body>
<div class="container">
        <h2>Watch Video</h2>
        <button id="playBtn" class="btn btn-primary">Watch Video</button>
        <br />
        <br />
        <video id="myVideo" width="303" height="360" controls>
            <source src="https://l.top4top.io/m_27030310v1.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <br />
        <h1>API</h1>
        <p>API ini dibuat oleh <a href="https://github.com/Xnuvers007">Xnuvers007</a>.</p>
        <p>API ini dibuat untuk mempermudah dalam mengambil data dari website.</p>
        <p style="color: green;">
        [3/6/2023] 9:42 <br />
        CHANGELOGS:
        <br />
        <ol class="custom-list">
          <li>menambahkan fitur memperpendek URL</li>
          <li>memperbaiki bug pada tampilan website</li>
        </ol>
        <p style="color: red;">
        [4/6/2023] 19:36 <br />
        CHANGELOGS:
        <br />
        <ol class="custom-list">
          <li>Menambahkan fitur cari obat</li>
          <li>Menambahkan fitur keterangan obat</li>
        </ol>
        </p>
        <div class="toggle-container">
            <label for="toggle-mode" class="toggle-label">Mode Gelap</label>
            <input type="checkbox" id="toggle-mode">
        </div>
    
        <br />

        <h2>Daftar API</h2>
        <button type="button" class="btn btn-primary" data-bs-toggle="collapse" data-bs-target="#websiteList" aria-expanded="false" aria-controls="websiteList">
            Tampilkan Daftar Website
        </button>
        <br />
        <div class="collapse" id="websiteList">
            <br />
            <ul>
                <center>
                    <li>
                        <a href="/kamus?text=eat" class="btn btn-primary">Kamus</a>
                    </li>
                    <li>
                        <a href="/convertuang?uang=1&dari=usd&ke=idr" class="btn btn-primary">Convert Uang</a>
                    </li>
                    <li>
                        <a href="/bp?tensi=125&hb=91" class="btn btn-primary">Blood Pressure</a>
                    </li>
                    <li>
                        <a href="/jam?wilayah=jakarta" class="btn btn-primary">Jam</a>
                    </li>
                    <li>
                        <a href="/world?news=5" class="btn btn-primary">Google News World</a>
                    </li>
                    <li>
                        <a href="/indonesia?berita=5" class="btn btn-primary">Google News Indonesia</a>
                    </li>
                    <li>
                        <a href="/translate?from=en&to=id&text=hello, im Xnuvers007, Im the developer" class="btn btn-primary">Translate</a>
                    </li>
                    <li>
                        <a href="/igstalk?user=Indradwi.25" class="btn btn-primary">Instagram Stalk</a>
                    </li>
                    <li>
                        <a href="/kanjiname?nama=Jokowi Widodo" class="btn btn-primary">Nama Kanji</a>
                    </li>
                    <li>
                        <a href="/short?url=github.com/xnuvers007" class="btn btn-primary">Short URL</a>
                    </li>
                    <li>
                        <a href="/cariobat?obat=pusing" class="btn btn-primary">Cari obat</a>
                    </li>
                    <li>
                        <a href="/keterangan?obat=/obat-dan-vitamin/flunarizine-10-mg-20-tablet/" class="btn btn-primary">Keterangan Obat</a>
                    </li>
                </center>
            </ul>
        </div>

        <br />

        <h2>Informasi Parameter</h2>
        <div class="table-responsive">
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>API</th>
                        <th>Parameter</th>
                        <th>Deskripsi</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Kamus</td>
                        <td>text</td>
                        <td>Parameter untuk kata yang ingin diterjemahkan.</td>
                    </tr>
                    <tr>
                        <td>Convert Uang</td>
                        <td>uang, dari, ke</td>
                        <td>Parameter untuk jenis uang yang ingin dikonversi dan mata uang asal serta tujuan.</td>
                    </tr>
                    <tr>
                        <td>Blood Pressure</td>
                        <td>tensi, hb</td>
                        <td>Parameter untuk tekanan darah sistolik dan diastolik, serta denyut jantung.</td>
                    </tr>
                    <tr>
                        <td>Jam</td>
                        <td>wilayah</td>
                        <td>Parameter untuk wilayah atau lokasi yang ingin diperoleh informasi waktu.</td>
                    </tr>
                    <tr>
                        <td>Google News World</td>
                        <td>news</td>
                        <td>Parameter untuk jumlah berita yang ingin ditampilkan.</td>
                    </tr>
                    <tr>
                        <td>Google News Indonesia</td>
                        <td>berita</td>
                        <td>Parameter untuk jumlah berita yang ingin ditampilkan.</td>
                    </tr>
                    <tr>
                        <td>Google Translate</td>
                        <td>dari, ke, text</td>
                        <td>Parameter untuk teks yang ingin diterjemahkan, bahasa asal, dan bahasa tujuan.</td>
                    </tr>
                    <tr>
                        <td>Instagram Stalk</td>
                        <td>user</td>
                        <td>Parameter untuk username Instagram yang ingin di-stalk.</td>
                    </tr>
                    <tr>
                        <td>Nama Kanji</td>
                        <td>nama</td>
                        <td>Parameter untuk nama yang ingin diterjemahkan.</td>
                    </tr>
                    <tr>
                        <td>Short URL </td>
                        <td>url</td>
                        <td>Parameter untuk memperpendek URL/Link yang sangat panjang</td>
                    </tr>
                    <tr>
                      <td>cari obat / medicine</td>
                      <td>obat</td>
                      <td>Parameter untuk mencari Obat, bisa diketikan penyakit atau obatnya</td>
                    </tr>
                    <tr>
                      <td>Keterangan obat / medicine</td>
                      <td>obat</td>
                      <td>Parameter untuk mencari keterangan mengenai fakta obat tersebut (gabungan dari <b>cari obat</b>)</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

<h2>Galeri Gambar</h2>
<div class="container">
    <div class="row">
        <div class="col-md-4">
            <img src="https://i.ibb.co/gMptW7w/1.webp" alt="Placeholder Image" class="img-fluid" loading="lazy">
            <a href="https://gtmetrix.com/reports/tr.deployers.repl.co/9hcirzN1/">Lihat Hasil GTMetrix DESKTOP</a>
        </div>
        <div class="col-md-4">
            <img src="https://i.ibb.co/ydbyBhV/2.webp" alt="Placeholder Image" class="img-fluid" loading="lazy">
            <a href="https://pagespeed.web.dev/analysis/https-tr-deployers-repl-co/ekypysxvaa?form_factor=mobile">Lihat Hasil PageSpeed Insights MOBILE</a>
        </div>
        <div class="col-md-4">
            <img src="https://i.ibb.co/8d26vYv/4.webp" alt="Placeholder Image" class="img-fluid" loading="lazy">
            <a href="https://pagespeed.web.dev/analysis/https-tr-deployers-repl-co/ekypysxvaa?form_factor=desktop">Lihat Hasil PageSpeed Insights DESKTOP</a>
        </div>
    </div>
    <div class="row">
        <div class="col-md-4">
            <img src="https://i.ibb.co/bv4RtJZ/3.webp" alt="Placeholder Image" class="img-fluid" loading="lazy">
            <a href="https://www.debugbear.com/test/website-speed/aVgrP5ip/overview">Lihat Hasil DebugBear MOBILE</a>
        </div>
        <div class="col-md-4">
            <img src="https://i.ibb.co/7jT5r76/5.webp" alt="Placeholder Image" class="img-fluid" loading="lazy">
            <a href="https://www.debugbear.com/test/website-speed/oPoks49H/overview">Lihat Hasil DebugBear DESKTOP</a>
        </div>
        <div class="col-md-4">
            <img src="https://i.ibb.co/Htzj1y6/6.webp" alt="Placeholder Image" class="img-fluid" loading="lazy">
            <br />
            <img src="https://i.ibb.co/Jt96t7N/7.webp" alt="Placeholder Image" class="img-fluid" loading="lazy">
            <br />
            <pre>
                <code>
import requests

url = "https://tr.deployers.repl.co"

while True:
    response = requests.get(url,headers={"User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.162 Mobile Safari/537.36"})
    response2 = requests.get(url,headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"})

    print("Android: ",response.elapsed.total_seconds())
    print("Desktop: ",response2.elapsed.total_seconds())
                </code>
            </pre>
        </div>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"
    crossorigin="anonymous"></script>
<script>
    const playBtn = document.getElementById('playBtn');
    const video = document.getElementById('myVideo');

    playBtn.addEventListener('click', function () {
        video.play();
    });
</script>
<script>
    const toggleModeCheckbox = document.getElementById('toggle-mode');
    const body = document.querySelector('body');

    toggleModeCheckbox.addEventListener('change', function () {
        if (this.checked) {
            body.classList.add('dark-mode');
        } else {
            body.classList.remove('dark-mode');
        }
    });
</script>
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
<script>
    $(document).ready(function() {
        var refreshTimeout; // Declare the variable here

        function refreshPage() {
            location.reload();
        }

        var refreshInterval = 60000;  // 1 minute in milliseconds

        setTimeout(refreshPage, refreshInterval);

        $(document).on('mousemove keypress', function() {
            clearTimeout(refreshTimeout);
            refreshTimeout = setTimeout(refreshPage, refreshInterval); // Assign the timeout ID to the variable
        });
    });
</script>
</body>
</html>
''')
  response.set_cookie(visitor_id,
                      value=cookie,
                      expires=expiration_date,
                      samesite='None',
                      secure=True)
  return response


@app.route('/indonesia', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_berita():
  num_articles = int(request.args.get(
    'berita',
    '5'))  # Get the 'j' query parameter from the URL, defaulting to 5
  url = "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRE55ZVc0U0FtbGtLQUFQAQ?hl=id&gl=ID&ceid=ID%3Aid"
  r = requests.get(url,
                   timeout=5,
                   headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac'})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all('c-wiz', attrs={'class': 'PIlOad'})
  titles = []
  links = []
  images = []
  for item in test:
    for img in item.find_all('figure', attrs={'class': 'K0q4G P22Vib'}):
      images.append(img.find('img')['src'])
    for teks in item.find_all('h4', attrs={'class': 'gPFEn'}):
      titles.append(teks.text)
    for link in item.find_all('a'):
      href = link.get('href')
      absolute_url = urljoin("https://news.google.com/", href)
      if '/stories/' not in absolute_url:
        links.append(absolute_url)
  berita_list = []
  for title, link, gambar in zip(titles, links, images):
    berita_list.append({
      'Berita': title,
      'Gambar': gambar,
      'Link Berita': link
    })
    if len(berita_list) == num_articles:
      break
  return jsonify(berita_list)


# URL SHORTLINK TINYURL
class UrlShortenTinyurl:
  URL = "http://tinyurl.com/api-create.php"

  @staticmethod
  def shorten(url_long):
    try:
      url = UrlShortenTinyurl.URL + "?" + urllib.parse.urlencode(
        {"url": url_long})
      res = requests.get(url)
      short_url = res.text
      return short_url
    except Exception as e:
      raise e


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

    short_url = UrlShortenTinyurl.shorten(url_long)
    return jsonify({
      'short_url': short_url,
      'status': 200,
      'author': 'Xnuvers007 [ https://github.com/Xnuvers007 ]'
    }), 200
  except Exception as e:
    traceback.print_exc()
    return jsonify({'error': 'An error occurred.'}), 500
    raise e


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

  drug_details = soup.find_all("div", class_="drug-detail col-md-12")

  if len(drug_details) > 0:
    data = {}
    data['Deskripsi'] = drug_details[0].text.strip(
    ) if drug_details[0].text else ""
    data['Indikasi Umum'] = drug_details[1].text.strip(
    ) if drug_details[1].text else ""
    data['Komposisi'] = drug_details[2].text.strip(
    ) if drug_details[2].text else ""
    data['Dosis'] = drug_details[3].text.strip(
    ) if drug_details[3].text else ""
    data['Aturan Pakai'] = drug_details[4].text.strip(
    ) if drug_details[4].text else ""
    data['Peringatan'] = drug_details[5].text.strip(
    ) if drug_details[5].text else ""
    data['Kontra Indikasi'] = drug_details[6].text.strip(
    ) if drug_details[6].text else ""
    data['Efek Samping'] = drug_details[7].text.strip(
    ) if drug_details[7].text else ""
    data['Golongan Produk'] = drug_details[8].text.strip(
    ) if drug_details[8].text else ""
    data['Kemasan'] = drug_details[9].text.strip(
    ) if drug_details[9].text else ""
    data['Manufaktur'] = drug_details[10].text.strip(
    ) if drug_details[10].text else ""
    data['No. Registrasi'] = drug_details[11].text.strip(
    ) if drug_details[11].text else ""
    return jsonify(data)
  else:
    return "Tidak ada data yang ditemukan."


@app.route('/world', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_berita_world():
  num_articles = int(request.args.get(
    'news', '5'))  # Get the 'j' query parameter from the URL, defaulting to 5
  url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtbGtHZ0pKUkNnQVAB?hl=id&gl=ID&ceid=ID:id"
  r = requests.get(url,
                   timeout=5,
                   headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac'})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all('c-wiz', attrs={'class': 'PIlOad'})
  titles = []
  links = []
  images = []
  for item in test:
    for img in item.find_all('figure', attrs={'class': 'K0q4G P22Vib'}):
      images.append(img.find('img')['src'])
    for teks in item.find_all('h4', attrs={'class': 'gPFEn'}):
      titles.append(teks.text)
    for link in item.find_all('a'):
      href = link.get('href')
      absolute_url = urljoin("https://news.google.com/", href)
      if '/stories/' not in absolute_url:
        links.append(absolute_url)
  berita_list = []
  for title, link, gambar in zip(titles, links, images):
    berita_list.append({'News': title, 'Image': gambar, 'Link News': link})
    if len(berita_list) == num_articles:
      break
  return jsonify(berita_list)


@app.route('/jam', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_jam():
  wilayah = request.args.get(
    'wilayah', 'Jakarta'
  )  # Get the 'wilayah' query parameter from the URL, defaulting to 'Jakarta'
  url = "https://time.is/id/" + wilayah
  r = requests.get(url,
                   timeout=5,
                   headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac'})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all('div', attrs={'id': 'clock0_bg'})
  for jams in test:
    jam = jams.find('time', attrs={'id': 'clock'}).text
  return jsonify({
    'Jam': jam,
    'wilayah': wilayah,
    'Author': 'Xnuvers007 [ https://github.com/Xnuvers007 ]'
  })


@app.route('/bp', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_bp():
  # i want it like this localhost:5000/bp?tensi=125&hb=91
  tensi = int(request.args.get('tensi', '125'))
  hb = int(request.args.get('hb', '91'))
  url = "https://foenix.com/BP/is-{0}/{1}-good-blood-pressure-or-high-blood-pressure.html".format(
    tensi, hb)
  r = requests.get(url,
                   timeout=5,
                   headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac'})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all('div', attrs={'class': 'content'})
  for hasil in test:
    hasil = soup.find_all('b')[15].text

  myhost = f"{request.host_url}bp?tensi={tensi}&hb={hb}"
  return jsonify({
    'Hasil': hasil,
    'Tensi': tensi,
    'Hb': hb,
    'Author': 'Xnuvers007 [ Xnuvers007 https://github.com/Xnuvers007 ]',
    'parameter': myhost
  })


@app.route('/convertuang', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_convertuang():
  uang = int(request.args.get('uang', '1'))
  dari = request.args.get('dari', 'IDR')
  ke = request.args.get('ke', 'USD')
  url = "https://www.exchange-rates.com/id/{0}/{1}/{2}/".format(uang, dari, ke)
  r = requests.get(url,
                   timeout=5,
                   headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac'})
  soup = BeautifulSoup(r.content, "html.parser")
  for i in soup.find_all('div', class_="fullwidth"):
    for j in i.find_all('div', class_="leftdiv"):
      hasil = j.find_all('p')[2]
      hasil = hasil.text
  return jsonify({
    'Hasil': hasil,
    'Uang': uang,
    'Dari': dari,
    'Ke': ke,
    'Author': 'Xnuvers007 [ https://github.com/Xnuvers007 ]'
  })


@app.route('/kamus', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_data():
  user_input = request.args.get('text')
  User_agent = UserAgent(browsers=['edge', 'chrome', 'firefox'])
  headers = {'User-Agent': User_agent.random}

  url = f'https://en.bab.la/dictionary/english-indonesian/{user_input}'
  url2 = f'https://www.oxfordlearnersdictionaries.com/definition/english/{user_input}'
  response = requests.get(url, headers=headers)
  response2 = requests.get(url2, headers=headers)

  soup = BeautifulSoup(response.text, 'html.parser')
  soup2 = BeautifulSoup(response2.text, 'html.parser')

  words = []
  translations = []
  examples = []
  synonyms = []
  sentences = []
  mp3 = []

  # get mp3 urls
  mp3uk1 = soup2.find('div',
                      {'class': 'sound audio_play_button pron-uk icon-audio'})
  mp3uk1 = mp3uk1.get('data-src-mp3') if mp3uk1 else 'Data Tidak Ditemukan'

  mp3us1 = soup2.find('div',
                      {'class': 'sound audio_play_button pron-us icon-audio'})
  mp3us1 = mp3us1.get('data-src-mp3') if mp3us1 else 'Data Tidak Ditemukan'

  # get word title
  title1 = soup2.find('h1', {'class': 'headword'})
  title1 = title1.text if title1 else 'Data Tidak Ditemukan'

  # append all
  mp3.append(mp3uk1)
  mp3.append(mp3us1)
  words.append(title1)

  # find the first ul tag with the class name 'sense-group-results'
  uls = soup.find('ul', {'class': 'sense-group-results'})

  # find all the li tags inside the ul tag again, but this time extract the word from the babTTS link
  for lis in uls.find_all('li'):
    get_a = lis.find('a')
    if get_a is not None and get_a.get('href') and 'babTTS' in get_a.get(
        'href'):
      # extract the word from the href attribute
      word = get_a.get('href').split("'")[3]
      words.append(word)

  # find all the li tags inside the ul tag and skip the first one
  for lis in uls.find_all('li')[1:]:
    get_a = lis.find('a')
    if get_a is not None:
      words.append(get_a.text)

  # find translations and examples
  for sense in soup.find_all('span', {'class': 'ogl_sense'}):
    for another in sense.find_all_next('span', {'class': 'ogl_sense_inner'}):
      for translation in another.find_all('span',
                                          {'class': 'ogl_translation noline'}):
        translations.append(translation.text.strip())
      for example in another.find_all('span', {'class': 'ogl_examples'}):
        # english
        for eng in example.find_all('span', {'class': 'ogl_exa'}):
          examples.append(eng.text.strip())
        # indonesian
        for ind in example.find_all('span', {'class': 'ogl_translation'}):
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
      '.icon-link-wrapper.dropdown a, .icon-link-wrapper.dropdown span, .icon-link-wrapper.dropdown ul, .icon-link-wrapper.dropdown li, .icon-link-wrapper.dropdown another'
  ):
    tag.decompose()

  for contextual in soup.find_all('div', {'class': 'sense-group'}):
    for example in soup.find_all('div', {'class': 'dict-example'}):
      eng1 = None  # Define eng1 outside of the inner loop
      for eng in example.find_all(
          'div', {'class': 'dict-source dict-source_examples'}):
        eng1 = eng.text.strip()  # Assign value to eng1
      for ind in example.find_all('div', {'class': 'dict-result'}):
        ind1 = ind.text.strip()
        if eng1 and ind1:
          sentences.append({'eng': eng1, 'ind': ind1})

  lis = soup.select('.quick-result-entry .quick-result-overview li a')
  for li in lis[9:15]:
    synonym = li.text
    synonyms.append(synonym)

  # create dictionary and return as JSON
  data = {
    'words': words,
    'translations': translations,
    'examples': examples,
    'synonyms': synonyms,
    'sentences': sentences,
    'mp3': mp3,
    'author': 'Xnuvers007 [ Https://github.com/Xnuvers007 ]'
  }
  return jsonify(data)


if __name__ == '__main__':
  app.run(debug=False, port=80, host='0.0.0.0')

# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup-
# from urllib.parse import urljoin
# import tkinter as tk

# app = Flask(__name__)
# root = tk.Tk()
# root.title("News App")

# @app.route('/indonesia', methods=['GET'])
# def get_berita():
#     num_articles = int(request.args.get('berita', '5'))  # Get the 'berita' query parameter from the URL, defaulting to 5
#     url = "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRE55ZVc0U0FtbGtLQUFQAQ?hl=id&gl=ID&ceid=ID%3Aid"
#     r = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac'})
#     soup = BeautifulSoup(r.content, "html.parser")
#     test = soup.find_all('c-wiz', attrs={'class': 'PIlOad'})
#     titles = []
#     links = []
#     images = []
#     for item in test:
#         for img in item.find_all('figure', attrs={'class': 'K0q4G P22Vib'}):
#             images.append(img.find('img')['src'])
#         for teks in item.find_all('h4', attrs={'class': 'gPFEn'}):
#             titles.append(teks.text)
#         for link in item.find_all('a'):
#             href = link.get('href')
#             absolute_url = urljoin("https://news.google.com/", href)
#             if '/stories/' not in absolute_url:
#                 links.append(absolute_url)
#     berita_list = []
#     for title, link, gambar in zip(titles, links, images):
#         berita_list.append({'Berita': title, 'Gambar': gambar, 'Link Berita': link})
#         if len(berita_list) == num_articles:
#             break
#     return jsonify(berita_list)

# @app.route('/world', methods=['GET'])
# def get_berita_world():
#     num_articles = int(request.args.get('news', '5'))  # Get the 'news' query parameter from the URL, defaulting to 5
#     url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtbGtHZ0pKUkNnQVAB?hl=id&gl=ID&ceid=ID:id"
#     r = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac'})
#     soup = BeautifulSoup(r.content, "html.parser")
#     test = soup.find_all('c-wiz', attrs={'class': 'PIlOad'})
#     titles = []
#     links = []
#     images = []
#     for item in test:
#         for img in item.find_all('figure', attrs={'class': 'K0q4G P22Vib'}):
#             images.append(img.find('img')['src'])
#         for teks in item.find_all('h4', attrs={'class': 'gPFEn'}):
#             titles.append(teks.text)
#         for link in item.find_all('a'):
#             href = link.get('href')
#             absolute_url = urljoin("https://news.google.com/", href)
#             if '/stories/' not in absolute_url:
#                 links.append(absolute_url)
#     berita_list = []
#     for title, link, gambar in zip(titles, links, images):
#         berita_list.append({'News': title, 'Image': gambar, 'Link News': link})
#         if len(berita_list) == num_articles:
#             break
#     return jsonify(berita_list)

# def start_flask_server():
#     import threading

#     def run_flask():
#         app.run(debug=False)

#     thread = threading.Thread(target=run_flask)
#     thread.start()

# def open_gui():
#     def get_indonesia_news():
#         num_articles = int(berita_entry.get())
#         response = requests.get(f"http://127.0.0.1:5000/indonesia?berita={num_articles}")
#         berita_list = response.json()
#         result_text.delete(1.0, tk.END)
#         for berita in berita_list:
#             result_text.insert(tk.END, f"Berita: {berita['Berita']}\n")
#             result_text.insert(tk.END, f"Gambar: {berita['Gambar']}\n")
#             result_text.insert(tk.END, f"Link Berita: {berita['Link Berita']}\n\n")

#     def get_world_news():
#         num_articles = int(news_entry.get())
#         response = requests.get(f"http://127.0.0.1:5000/world?news={num_articles}")
#         news_list = response.json()
#         result_text.delete(1.0, tk.END)
#         for news in news_list:
#             result_text.insert(tk.END, f"News: {news['News']}\n")
#             result_text.insert(tk.END, f"Image: {news['Image']}\n")
#             result_text.insert(tk.END, f"Link News: {news['Link News']}\n\n")

#     root.geometry("600x400")

#     berita_label = tk.Label(root, text="Indonesia News", font=("Arial", 16, "bold"))
#     berita_label.pack()

#     berita_frame = tk.Frame(root)
#     berita_frame.pack()

#     berita_label = tk.Label(berita_frame, text="Number of Articles:")
#     berita_label.pack(side=tk.LEFT)

#     berita_entry = tk.Entry(berita_frame)
#     berita_entry.pack(side=tk.LEFT)

#     berita_button = tk.Button(root, text="Get Indonesia News", command=get_indonesia_news)
#     berita_button.pack()

#     news_label = tk.Label(root, text="World News", font=("Arial", 16, "bold"))
#     news_label.pack()

#     news_frame = tk.Frame(root)
#     news_frame.pack()

#     news_label = tk.Label(news_frame, text="Number of Articles:")
#     news_label.pack(side=tk.LEFT)

#     news_entry = tk.Entry(news_frame)
#     news_entry.pack(side=tk.LEFT)

#     news_button = tk.Button(root, text="Get World News", command=get_world_news)
#     news_button.pack()

#     result_label = tk.Label(root, text="Result:", font=("Arial", 14, "bold"))
#     result_label.pack()

#     result_text = tk.Text(root, height=10, width=60)
#     result_text.pack()

#     root.mainloop()

# if __name__ == '__main__':
#     start_flask_server()
#     open_gui()
