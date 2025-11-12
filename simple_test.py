from flask import Flask, render_template

app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
    print("INDEX CALLED")
    return "<h1>Simple HTML Works</h1>"

@app.route('/template')
def template():
    print("TEMPLATE CALLED")
    return render_template('index.html')

if __name__ == '__main__':
    print("Starting simple test server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
