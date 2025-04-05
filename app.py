from flask import Flask, request, send_from_directory, render_template, redirect, url_for
import os
import shutil
from datetime import datetime

UPLOAD_ROOT = 'uploads'
app = Flask(__name__)
app.config['UPLOAD_ROOT'] = UPLOAD_ROOT
os.makedirs(UPLOAD_ROOT, exist_ok=True)

# 📦 Speicherplatz anzeigen
def get_disk_usage(path):
    total, used, free = shutil.disk_usage(path)
    return {
        'total': round(total / (1024 ** 3), 2),
        'used': round(used / (1024 ** 3), 2),
        'free': round(free / (1024 ** 3), 2)
    }

# 📅 Aktuelles Datum als schöner Ordnername
def get_today_folder():
    date = datetime.now().strftime('%d-%B-%Y')
    all_months = {"January": "Jänner",
                  "February": "Februar",
                  "March": "März",
                  "April": "April",
                  "May": "Mai",
                  "June": "Juni",
                  "July": "Juli",
                  "August": "August",
                  "September": "September",
                  "October": "Oktober",
                  "November": "November",
                  "December": "Dezember"}
    date = date.replace(date.split("-")[1], all_months[date.split("-")[1]])
    return date



@app.route('/')
def index():
    usage = get_disk_usage(app.config['UPLOAD_ROOT'])
    all_files = []

    for date_folder in sorted(os.listdir(app.config['UPLOAD_ROOT']), reverse=True):
        full_path = os.path.join(app.config['UPLOAD_ROOT'], date_folder)
        if os.path.isdir(full_path):
            files = [
                (date_folder, f, round(os.path.getsize(os.path.join(full_path, f)) / (1024 ** 2), 2))
                for f in os.listdir(full_path)
            ]
            all_files.extend(files)

    return render_template('index.html', files=all_files, usage=usage)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename != '':
        folder = get_today_folder()
        target_folder = os.path.join(app.config['UPLOAD_ROOT'], folder)
        os.makedirs(target_folder, exist_ok=True)
        file.save(os.path.join(target_folder, file.filename))
    return redirect(url_for('index'))

@app.route('/download/<date>/<filename>')
def download_file(date, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_ROOT'], date), filename, as_attachment=True)

@app.route('/delete/<date>/<filename>', methods=['POST'])
def delete_file(date, filename):
    path = os.path.join(app.config['UPLOAD_ROOT'], date, filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
