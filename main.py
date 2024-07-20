# # import config as conf
# # from routes import app

# # if __name__ == "__main__":
# #     app.run(debug=conf.DEBUG, port=conf.PORT, host="0.0.0.0")

# import config as conf
# from routes import app
# from threading import Thread

# def run():
#   app.run(debug=conf.DEBUG, port=conf.PORT, host="0.0.0.0")

# # def keep_alive():
# #   t = Thread(target=run)
# #   t.start()

# if __name__ == "__main__":
#   t = Thread(target=run)
#   t.start()

#
#import config as conf
#from routes import app
#from threading import Thread

#def run():
#    app.run(debug=conf.DEBUG, port=conf.PORT, host="0.0.0.0")

#if __name__ == "__main__":
#    t1 = Thread(target=run)
#    t2 = Thread(target=run)

#    t1.start()
#    t2.start()

import config as conf
from routes import app
from threading import Thread

def run_flask():
    app.run(debug=conf.DEBUG, port=conf.PORT, host="0.0.0.0")

@app.after_request
def add_header(response):
    response.headers['Connection'] = 'keep-alive'
    return response

if __name__ == "__main__":
    t1 = Thread(target=run_flask)
    t2 = Thread(target=run_flask)

    t1.start()
    t2.start()
  