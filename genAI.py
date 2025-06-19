from flask import Flask, render_template, request, redirect, url_for, session,blueprints,Blueprint
import random
import csv
import os
import math
import requests
from middleware.auth_middleware import login_required

AI=Blueprint("AI",__name__)

@AI.route('/genAI',methods=['get','post'])
@login_required
def GenAI():
    return render_template("genAI.html")
