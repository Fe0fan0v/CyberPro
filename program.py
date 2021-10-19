from flask import redirect, render_template, Flask, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'


@app.route('/', methods=["GET", 'POST'])
def v():
    if request.method == "POST":
        print(request.form['lst'])
    return render_template('file.html')


if __name__ == '__main__':
    app.run('localhost', 8800)
