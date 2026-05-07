import os
from flask import url_for, Blueprint, render_template

main_bp = Blueprint('main', __name__)
basedir = os.path.abspath(os.path.dirname('templates'))
IMAGES_DIR = os.path.join(basedir, 'templates/index.html')


@main_bp.route('/', defaults={'path':''})
def index(path):
    # return send_from_directory(app.static_folder,'index.html')    
    return render_template('index.html')