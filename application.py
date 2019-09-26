import skype_chatbot
import os
import json
from prediction import Prediction
from train import Train
from flask import Flask, request
from upload_file import upload_file

app = Flask(__name__, static_url_path='/static')
app_id = os.environ.get('APP_ID')
app_secret = os.environ.get('APP_SECRET')
MODEL_DIR = os.environ.get('MODEL_DIR')
intents_file = "intents.json"
ml_prediction  = None

bot = skype_chatbot.SkypeBot(app_id, app_secret)

@app.route("/")
def hello():
    return app.send_static_file('train.html')

@app.route('/api/messages', methods=['POST', 'GET'])
def webhook():
    try:
        ml_prediction
    except NameError:
        ml_prediction = Prediction(MODEL_DIR)
        ml_prediction.load_model()
    answer = ''    
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            bot_id = data['recipient']['id']
            bot_name = data['recipient']['name']
            recipient = data['from']
            service = data['serviceUrl']
            sender = data['conversation']['id']
            text = data['text']

            bot.send_message(bot_id, bot_name, recipient, service, sender, 
                ml_prediction.response(text, sender))
        except Exception as e:
            print(e)
    if request.method == 'GET':
        question = request.args.get('q')
        answer = ml_prediction.response(question if question else 'Hi')
    return 'Code: 200. {}'.format(answer)

@app.route('/api/train', methods=['GET', 'POST'])
def train():
    if request.method == 'POST':
        try:
            intents_file = upload_file(request)
        except Exception as e:
            return "Error: {}".format(e)
    if request.method == 'GET':
        input_file = request.args.get('file');
        intents_file = input_file if input_file else "intents.json"

    ml = Train(intents_file, MODEL_DIR)
    try:
        ml.training()
        ml_prediction = Prediction(MODEL_DIR)
        ml_prediction.load_model()
        return "Train is completed"
    except Exception as e:
        return "Traing is failed {}".format(str(e))

@app.route('/train.html')
def train_page():
    return app.send_static_file('train.html')
