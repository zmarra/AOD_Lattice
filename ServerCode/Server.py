#!/usr/bin/env python
from flask import Flask
from flask import render_template
from flask import request
import json
import sys
sys.path.insert(0, 'Tools/')
import WaveformManager


class SDRServer():

    waveMan = WaveformManager.WaveformManager("Resources/waveformArguments.json")

    def runServer(self, sub, stream, conMan):

        app = Flask(__name__)

        @app.route('/monitor', methods=['GET', 'PUT'])
        def monitor():


            # sub_list = {1:{'kwargs':{kwargs}, 'control':{control}}
            return render_template('index.html', id_list=(waveMan.getJsonData()).keys(), sub_list=waveMan.getJsonData(), **waveMan.getJsonData())
            # except Exception:
            #     return 'Unable to load page'

                # subscribe

        @app.route('/update/<id>/config', methods=['POST'])
        def updateConfig(id):
            with open(sub_file, 'r') as f:
                sub_list = json.load(f)
            id_dict = sub_list[id]
            print id_dict
            kwargs = id_dict['kwargs']
            configDict = request.form.to_dict()
            for key in configDict.keys():
                conMan.config.set('CHANNEL'+str(kwargs['channel']), key, configDict[key])
            conMan.updateConfig()
            return ''

        @app.route('/update/<id>', methods=['GET', 'POST'])
        def update(id):
            id = id.encode('ascii', 'ignore')
            with open(sub_file, 'r') as f:
                sub_list = json.load(f)
                # sub_list = {1:{'kwargs':{kwargs}, 'control':{control}}

            if request.method == 'POST':
                sub_list[id]['kwargs'] = request.form.to_dict()
                sub.update(stream, int(id), **sub_list[id]['kwargs'])

            id_dict = sub_list[id]
            control = id_dict['control']
            kwargs = id_dict['kwargs']

            if control['alert']:
                alert = 'On'
            else:
                alert = 'Off'
            if control['pause']:
                pause = 'Paused'
            else:
                pause = 'Started'

            configStuff = conMan.config.items('CHANNEL'+str(kwargs['channel']))

            return render_template('keywords.html', id=id, kw_dict=kwargs, alert=alert, pause=pause, config_dict=configStuff)

        super(PIDServer, self).runServer(sub, stream)
        app.run(host='0.0.0.0', debug=True, use_reloader=False)
