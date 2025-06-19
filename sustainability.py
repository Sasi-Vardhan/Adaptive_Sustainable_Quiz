from flask import Flask, render_template, request, redirect, url_for, session,blueprints,Blueprint
import random
import csv
import os
import math
import requests
from middleware.auth_middleware import login_required

sustain=Blueprint("sustain",__name__)

@sustain.route('/sustainability')
@login_required
def sustainability():
    return render_template("index.html")
    # session.clear()
    # return redirect(url_for('quiz'))
