import dowser
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/divine')
def divine():
    sd = dowser.StringsDowser()
    strings_list, list_of_files = sd.define_water()
    undivined = sd.divining_ground_water(strings_list, list_of_files)
    return render_template('index.html', output=undivined)


if __name__ == '__main__':
    app.run()
