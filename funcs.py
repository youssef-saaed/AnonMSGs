from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import HTTPException
from datetime import datetime
import sqlite3
from random import randint
from functools import wraps
import os

def apology(code, msg):
    return render_template("apology.html", error_code=code, error_msg=msg), code

def login_required(f):
    @wraps(f)
    def func(*args,**kwargs):
        if session.get("user_id") is None:
            return redirect("/Login")
        return f(*args, **kwargs)
    return func

def sqliteQuery(conn, *args):
    db = conn.cursor()
    return db.execute(*args)
