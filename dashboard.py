from flask import Flask, render_template, request, redirect, url_for, session,blueprints,Blueprint
import random
import csv
import os
import math
import requests
from middleware.auth_middleware import login_required

dash = Blueprint('dash', __name__)

@dash.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@dash.route('/set-choice', methods=['POST'])
@login_required
def set_choice():
    session['choice'] = request.form.get('choice')
    print(session["choice"])
    if(session['choice'] == 'sustainability'):
        return redirect(url_for('sustain.sustainability'))
    if(session['choice'] == 'genai'):
        return redirect(url_for('AI.GenAI'))