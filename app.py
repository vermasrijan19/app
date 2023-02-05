from flask import Flask
from flask import Flask, request
from markupsafe import escape
from flask_cors import CORS
from skimage import io
from sewar.full_ref import ssim
from html2image import Html2Image
import json
from datetime import datetime

app = Flask(__name__)
CORS(app, resources=r'/*', headers='Content-Type')


def returnScore(hCF1, hCF2):
    hti = Html2Image(size=(400, 300))
    img1 = io.imread(
        hti.screenshot(html_file=hCF1, save_as='created_css_img.png')[0])
    img2 = io.imread(
        hti.screenshot(html_file=hCF2, save_as='created_css_img_correct.png')[0])
    similarity = ssim(img1, img2)
    # print(similarity[0])
    score = (similarity[0]) * 100
    print("score is ", round(score, 4))
    return score


def crtHTML(html, css):
    return str("<!DOCTYPE html><html> <head><style>" + str(css) +
               "</style></head>" + '<body style="width:400px;height:300px">' +
               str(html) + "</body>" + "</html>")


def update_json_file(file_path, user_name, question_no, score, time_of_upload):
    # Load the existing data.json file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except:
        data = {}

    # Check if the test name already exists
    if user_name in data:
        # If it exists, update the corresponding question score and time of upload
        data[user_name][question_no] = [score, time_of_upload]
    else:
        # If it does not exist, create a new entry for the test name with the question score and time of upload
        data[user_name] = {question_no: [score, time_of_upload]}

    # Dump the updated data to the data.json file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


@app.route('/')
def index():
    return 'Hello from Flask!'


@app.route('/test/<post_id>')
def testdata(post_id):
    return f'Test data: {escape(post_id)}'


@app.route("/process_html", methods=["POST"])
def process_html():
    html = request.get_json().get("html")
    processed_html = html
    return {"processed_html": processed_html}


@app.route("/chkaccuracy", methods=["POST"])
def chk_accuracy():
    user = str(request.get_json().get("username"))
    html = str(request.get_json().get("htmlin"))
    css = str(request.get_json().get("cssin"))
    q = str(request.get_json().get("qno"))
    html1 = str(request.get_json().get("htmlex"))
    css1 = str(request.get_json().get("cssex"))
    gvn = crtHTML(html, css)
    exp = crtHTML(html1, css1)
    score = returnScore(gvn, exp)
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    update_json_file("data.json", user, q, score, current_time)
    return {"user": user, "score": score}
app = Flask(__name__)



if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0',port=8080)
