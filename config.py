"""Create config file for the project."""
import markdown

PORT = 80
DEBUG = False
AUTO_RELOAD = True

# SOCIAL MEDIA LINK :)
SOCIAL_MEDIA = {
  "telegram": "https://s.id/1LRRU",  # False or url to your telegram
  "facebook": "https://s.id/1LRqw",  # False or url to your facebook
  "instagram": "https://s.id/1LRS0",  # False or url to your instagram
  "github": "https://s.id/1LRSf",  # False or url to your github
}

APP_TITLE = "API"
APP_DESCRIPTION = "API ini dibuat untuk mempermudah dalam mengambil data dari website."

AUTHOR_NAME = "Xnuvers007"
AUTHOR_NAME2 = "IhsanDevs"
AUTHOR_LINK = "https://github.com/Xnuvers007"
AUTHOR_LINK2 = "https://github.com/IhsanDevs"

CHANGELOG = [
  "perbaikan fitur keterangan obat [29/08/2023]",
  "penambahan fitur whois domain [30/08/2023]",
  "Penambahan fitur subdomain finder checker [30/08/2023]",
  "Penambahan fitur simsimi [03/09/2023]",
  "Penambahan fitur Pinterest Images/Videos/Gifs downloader [09/09/2023] 02:00 WIB [MENGGUNAKAN URL seperti ini https://id.pinterest.com/pin/28006828927067496]",
  "Penambahan Fitur Summarize text [09/09/2023] 15:47 WIB",
  "Penambahan Fitur pencarian/tracking Alamat IP atau IP address atau Internet Protocol",
  "Tiktok Downloader langsung download tanpa pencet link [13/10/2023]",
  "Penambahan fitur Lirik lagu [13/10/2023] CATATAN: ADA BEBERAPA LIRIK LAGU YANG TIDAK BISA, DIKARENAKAN ATURAN REPLIT",
  "Penambahan fitur lirik lagu versi pertama (lebih bagus dari sebelumnya yaitu versi 2). [14/10/2023] 2:37 WIB.",
  "Penambahan fitur download sorotan/cerita Instagram seseorang (syarat harus publik account).",
  "Penambahan fitur untuk mendeteksi Data/Email yang bocor di deepweb/darkweb [07/11/2023]",
  "Update fitur shortlink url yang tadinya hanya tinyurl, sekarang ada bitly, isgd, ouo, vgd.",
  "Penambahan Fitur Pencarian Bing.",
  "penambahan fitur capcut dan instagram downloader [26/11/2023]",
  "Penambahan fitur pencarian film bioskop [17/12/2023]"
]

GALERIES = [
  {
    "image": "https://i.ibb.co/gMptW7w/1.webp",
    "link": {
      "href": "https://gtmetrix.com/reports/tr.deployers.repl.co/3PiRf2GP/",
      "text": "Lihat Hasil GTMetrix DESKTOP",
    },
    "description": False,
  },
  {
    "image": "https://i.ibb.co/ydbyBhV/2.webp",
    "link": {
      "href":
      "https://pagespeed.web.dev/analysis/https-tr-deployers-repl-co/ekypysxvaa?form_factor=mobile",
      "text": "Lihat Hasil PageSpeed Insights MOBILE",
    },
    "description": False,
  },
  {
    "image": "https://i.ibb.co/8d26vYv/4.webp",
    "link": {
      "href":
      "https://pagespeed.web.dev/analysis/https-tr-deployers-repl-co/ekypysxvaa?form_factor=desktop",
      "text": "Lihat Hasil PageSpeed Insights DESKTOP",
    },
    "description": False,
  },
  {
    "image": "https://i.ibb.co/bv4RtJZ/3.webp",
    "link": {
      "href": "https://www.debugbear.com/test/website-speed/aVgrP5ip/overview",
      "text": "Lihat Hasil DebugBear MOBILE",
    },
    "description": False,
  },
  {
    "image": "https://i.ibb.co/7jT5r76/5.webp",
    "link": {
      "href": "https://www.debugbear.com/test/website-speed/oPoks49H/overview",
      "text": "Lihat Hasil DebugBear DESKTOP",
    },
    "description": False,
  },
  {
    "image":
    "https://i.ibb.co/Jt96t7N/7.webp",
    "link": {
      "href":
      "https://jupyter.xnuvers007.repl.co/notebooks/tr.deployers.repl.co.ipynb",
      "text": "Lihat hasil Jupyter (password = xnuvers007), tekan see more",
    },
    "description":
    markdown.markdown("""
        import requests

        url = "https://tr.deployers.repl.co"

        while True:
            response = requests.get(url,headers={"User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.162 Mobile Safari/537.36"})
            response2 = requests.get(url,headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"})

            print("Android: ",response.elapsed.total_seconds())
            print("Desktop: ",response2.elapsed.total_seconds())"""),
  },
]

API_SERVICES = [{
  "name":
  "Bing Search",
  "description":
  "Parameter untuk melakukan pencarian BING",
  "parameters": [{
    "name": "search",
    "type": "string",
    "required": True
  }],
  "url":
  "/bing?search=kanao%20tsuyuri"
},{
  "name": "Bioskop Search",
  "description": "Parameter untuk melakukan pencarian film bioskop.",
  "parameters": [{
    "name": "search",
    "type": "string",
    "required": True
  }],
  "url": "/bioskop?search=avengers%20endgame"  
}, {
  "name":
  "Blood Pressure",
  "description":
  "Parameter untuk tekanan darah sistolik dan diastolik, serta denyut jantung.",
  "parameters": [
    {
      "name": "tensi",
      "type": "integer",
      "required": True
    },
    {
      "name": "hb",
      "type": "integer",
      "required": True
    },
  ],
  "url":
  "/bp?tensi=125&hb=91",
}, {
  "name": "Bola",
  "description": "API Website untuk melihat jadwal pertandingan Bola.",
  "url": "/jadwal-pertandingan",
}, {
  "name":
  "Capcut Downloader",
  "description":
  "Untuk mendownload video dari capcut.",
  "parameters": [{
    "name": "url",
    "type": "string",
    "required": True
  }],
  "url":
  "/capcut?url=https://www.capcut.com/t/Zs82ASjAk/"
}, {
  "name":
  "Check Data Email",
  "description":
  "Melakukan pengecekan data yang bocor di dalam deepweb/darkweb, input berupa email. (Data tidak disimpan).",
  "parameters": [{
    "name": "email",
    "type": "string",
    "required": True
  }],
  "url":
  "/checkdata",
}, {
  "name":
  "Checker APIKEY Openai (ChatGPT)",
  "description":
  "Melakukan Pengecekan Pada APIKEY Openai (data apikey tidak disimpan).",
  "parameters": [
    {
      "name": "key",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/openai?key=YOUR_APIKEY",
}, {
  "name":
  "Clickjacking/Clickjacker",
  "description":
  "Melakukan pengecekan Kerentanan / Kelemahan pada suatu website dengan metode pemeriksaan clickjacking.",
  "parameters": [{
    "name": "u",
    "type": "string",
    "required": True
  }],
  "url":
  "/cj?u=",
}, {
  "name":
  "Convert Uang",
  "description":
  "Pengkonversi Uang. Masukkan paramter yang ingin di konversi.",
  "parameters": [
    {
      "name": "uang",
      "type": "integer",
      "required": True
    },
    {
      "name": "dari",
      "type": "string",
      "required": True
    },
    {
      "name": "ke",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/convertuang?uang=1&dari=usd&ke=idr",
}, {
  "name":
  "Facebook Downloader",
  "description":
  "Parameter untuk mendownload Video dari platform yang bernama Facebook.",
  "parameters": [{
    "name": "u",
    "type": "string",
    "required": True
  }],
  "url":
  "/fb?u=LINKKAMU"
}, {
  "name":
  "Google Images",
  "description":
  "Parameter untuk mendapatkan link/tautan gambar yang dihasilkan oleh google",
  "parameters": [{
    "name": "q",
    "type": "string",
    "required": True
  }],
  "url":
  "/gimg?q=naruto"
}, {
  "name":
  "Google News Indonesia",
  "description":
  "Parameter untuk jumlah berita yang ingin ditampilkan.",
  "parameters": [
    {
      "name": "berita",
      "type": "integer",
      "required": True
    },
  ],
  "url":
  "/indonesia?berita=5",
}, {
  "name":
  "Google News World",
  "description":
  "Parameter untuk jumlah berita yang ingin ditampilkan.",
  "parameters": [
    {
      "name": "news",
      "type": "integer",
      "required": True
    },
  ],
  "url":
  "/world?news=5",
}, {
  "name":
  "Google Translate",
  "description":
  "Parameter untuk teks yang ingin diterjemahkan, bahasa asal, dan bahasa tujuan.",
  "parameters": [
    {
      "name": "dari",
      "type": "string",
      "required": True
    },
    {
      "name": "ke",
      "type": "string",
      "required": True
    },
    {
      "name": "text",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/translate?from=en&to=id&text=hello,%20im%20Xnuvers007,%20Im%20the%20developer",
}, {
  "name":
  "Instagram Downloader",
  "description":
  "Parameter untuk mendownload postingan video/cerita Instagram. (Public Account)",
  "parameters": [{
    "name": "url",
    "type": "string",
    "required": True
  }],
  "url":
  "/instagramdl?url=https://www.instagram.com/reel/C0EEgMNSSHw/?igshid=MzY1NDJmNzMyNQ==",
}, {
  "name":
  "Instagram Stalk",
  "description":
  "Parameter untuk username Instagram yang ingin di-stalk.",
  "parameters": [
    {
      "name": "user",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/igstalk?user=Indradwi.25",
}, {
  "name":
  "Instagram Story",
  "description":
  "Parameter untuk mendownload sorotan/cerita akun instagram seseorang (harus akun publik).",
  "parameters": [
    {
      "name": "url",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/igstory?url=https://www.instagram.com/stories/instagram/",
}, {
  "name":
  "IP Tracker",
  "description":
  "Paramter untuk melakukan tracking terhadap alamat IP. bisa menggunakan alamat ip, bisa juga dengan domain/alamat website contoh: 8.8.8.8 atau bisa juga google.com",
  "parameters": [
    {
      "name": "ip",
      "type": "str",
      "required": True
    },
  ],
  "url":
  "/ip-tracker?ip=8.8.8.8"
}, {
  "name":
  "Jam",
  "description":
  "Parameter untuk wilayah atau lokasi yang ingin diperoleh informasi waktu.",
  "parameters": [
    {
      "name": "wilayah",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/jam?wilayah=jakarta",
}, {
  "name":
  "Kamus",
  "description":
  "Penerjemah kata. Masukkan text yang ingin diterjemahkan",
  "parameters": [
    {
      "name": "text",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/kamus?text=sleep",
}, {
  "name":
  "Keterangan Obat",
  "description":
  "Parameter untuk nama obat yang ingin diperoleh keterangannya",
  "parameters": [
    {
      "name": "obat",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/keterangan?obat=/obat-dan-vitamin/flunarizine-10-mg-20-tablet/",
}, {
  "name":
  "Lirik/Lyrics Lagu versi 1 (Terbaru)",
  "description":
  "Parameter untuk mencari Lirik dari sebuah lagu berdasarkan nama penyanyi dan judul lagunya.",
  "parameters": [
    {
      "name": "lagu",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/googlelirik?lagu=Nadhif basalamah penjaga hati",
}, {
  "name":
  "Lirik/Lyrics Lagu versi 2",
  "description":
  "Parameter untuk mencari lirik lagu. CATATAN: ADA BEBERAPA LIRIK LAGU YANG TIDAK BISA, DIKARENAKAN ATURAN REPLIT",
  "parameters": [
    {
      "name": "lagu",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/lirik?lagu=anggi marito tak segampang itu",
}, {
  "name":
  "Nama Kanji",
  "description":
  "Parameter untuk nama yang ingin diterjemahkan.",
  "parameters": [
    {
      "name": "nama",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/kanjiname?nama=Jokowi%20Widodo",
}, {
  "name": "MPL-ID Schedule (Jadwal)",
  "description": "Parameter untuk melihat jadwal MPL-ID yang tersedia",
  "url": "/jadwal-mpl"
}, {
  "name":
  "Obat Halodoc",
  "description":
  "Parameter untuk nama obat/nama penyakit yang ingin dicari untuk obatnya",
  "parameters": [
    {
      "name": "obat",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/cariobat?obat=pusing",
}, {
  "name":
  "Parafrase Checker",
  "description":
  "Parameter Untuk melakukan parafrase pada sebuah kalimat agar bertujuan mudah dipahami dan tidak memperboros kata",
  "parameters": [{
    "name": "teks",
    "type": "string",
    "required": True
  }, {
    "name": "mode",
    "type": "string",
    "required": True
  }],
  "url":
  "/parafrase?teks=&mode="
}, {
  "name":
  "Pinterest",
  "description":
  "Parameter untuk mendownload/melihat gambar dari pinterest. gambar yang ditampilkan banyak akan tetapi ukuran low",
  "parameters": [{
    "name": "q",
    "type": "string",
    "required": True
  }],
  "url":
  "/pin?q=Naruto"
}, {
  "name":
  "Pinterest Downloader (Images/Videos/Gif multiple)",
  "description":
  "Parameter untuk mendownload sebuah gambar yang banyak atau mendownload video maupun gif yang berasal dari pinterest dengan memasukan URL/Link. Syarat url yang salah = https://pin.it/5FR5y4A . url yang benar = https://id.pinterest.com/pin/28006828927067496",
  "parameters": [{
    "name": "url",
    "type": "string",
    "required": True
  }],
  "url":
  "/pindownload?url=https://id.pinterest.com/pin/798966790152483753"
}, {
  "name":
  "Pinterest HD",
  "description":
  "Parameter untuk mendownload/melihat gambar dari pinterest. gambar yang ditampilkan sedikit akan tetapi ukuran HD",
  "parameters": [{
    "name": "q",
    "type": "string",
    "required": True
  }],
  "url":
  "/pinhd?q=Naruto"
}, {
  "name":
  "Ringkas teks / Text summarizer",
  "description":
  "Parameter untuk meringkas sebuah teks yang panjang menjadi sedikit [versi JSON]",
  "parameters": [{
    "name": "text",
    "type": "string",
    "required": True
  }],
  "url":
  "/summarize?text=MasukanTeksPanjang"
}, {
  "name": "Ringkas teks 2/ Text summarizer 2",
  "description":
  "Parameter untuk meringkas sebuah teks yang panjang menjadi sedikit [versi HTML]",
  "url": "/ringkas"
}, {
  "name":
  "Short URL",
  "description":
  "Parameter untuk memperpendek URL/Link yang sangat panjang",
  "parameters": [
    {
      "name": "url",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/short?url=github.com/xnuvers007",
}, {
  "name":
  "Simsimi (simi simi)",
  "description":
  "Parameter untuk berbicara dengan simsimi.",
  "parameters": [{
    "name": "text",
    "type": "string",
    "required": True
  }],
  "url":
  "/simi?text=HALO+SIMI"
}, {
  "name":
  "Subdomain Finder/Checker",
  "description":
  "Parameter untuk melihat subdomain dari domain utama si target.",
  "parameters": [{
    "name": "q",
    "type": "string",
    "required": True
  }],
  "url":
  "/subdomain?q=lazada.co.id"
}, {
  "name":
  "Tiktok Downloader",
  "description":
  "Parameter untuk mendownload video di Tiktok",
  "parameters": [
    {
      "name": "url",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/tiktok?url=https://www.tiktok.com/@yurii_kun5/video/7225627953185721627?is_from_webapp=1"
}, {
  "name":
  "Whois",
  "description":
  "WHOIS adalah sistem yang memberikan informasi tentang kepemilikan, pendaftaran, dan detail teknis suatu domain di internet. Ini membantu orang mengetahui siapa pemiliknya, kapan didaftarkan, serta informasi lainnya.",
  "parameters": [{
    "name": "url",
    "type": "string",
    "required": True
  }],
  "url":
  "/whois?url=lazada.co.id"
}, {
  "name":
  "Youtube Playlist",
  "description":
  "melakukan pencarian video berdasarkan playlist youtube yang ada",
  "parameters": [{
    "name": "name",
    "type": "string",
    "required": True
  }, {
    "name": "lim",
    "type": "integer",
    "required": True
  }],
  "url":
  "/playlist?name=Kanao Tsuyuri&lim=15"
}, {
  "name":
  "Youtube Search",
  "description":
  "melakukan pencarian video berdasarkan pencarian youtube yang anda cari",
  "parameters": [{
    "name": "name",
    "type": "string",
    "required": True
  }, {
    "name": "lim",
    "type": "integer",
    "required": True
  }],
  "url":
  "/vid?name=Kanao Tsuyuri&lim=15"
}, {
  "name": "ZeroGPT-1",
  "description":
  "Alat/AI pengecek apakah kata tersebut terbuat dari AI atau tidak",
  "url": "/zerogpt"
}, {
  "name":
  "ZeroGPT-2",
  "description":
  "Alat/AI ke 2 dari ZeroGPT-1, pengecek apakah kata tersebut dibuat oleh AI atau tidak",
  "parameters": [
    {
      "name": "t",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/zerogptjson?t=MASUKAN+TEKSNYA+DISINI"
}]
