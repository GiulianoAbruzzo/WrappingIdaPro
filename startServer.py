import os
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename

#modifica la path di dove saranno caricati i file
UPLOAD_FOLDER = 'C:\Users\Giuliano\Desktop\UploadingFiles'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'out'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nessun file')
        file = request.files['file']
        if file.filename == '':
            flash('Nessun file selezionato')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "Il file e' stato uploadato correttamente, i file al momento nel server sono:\n" + uploaded_file()

@app.route('/uploads', methods=['GET'])
def uploaded_file():
    tree=""
    try: lst = os.listdir(UPLOAD_FOLDER)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
                tree+=name+"\n"
    return tree

if __name__ == "__main__":
    app.run(debug=True)