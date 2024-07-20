from flask import redirect, url_for
import requests, random, hashlib, time


def generate_visitor_id():
    timestamp = str(time.time())
    md5_hash = hashlib.md5(timestamp.encode()).hexdigest()
    return md5_hash


def generate_cookie(visitor_id):
    timestamp = str(time.time())
    sha1_hash = hashlib.sha1((timestamp + visitor_id).encode()).hexdigest()
    return sha1_hash
