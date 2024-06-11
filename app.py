import configparser
import os
from flask import Flask, session, render_template, request, redirect, url_for, jsonify, abort
import requests
from datetime import datetime
from waitress import serve
import argparse

app = Flask(__name__)
config_file = 'system.cfg'
default_page_table = [
    "system_error.html"
]

def load_config(file):
    config_data = {
        'page_table': default_page_table,
        'secret_key': 'default_secret_key',
        'app_script_url': 'https://script.google.com/a/macros/volocitee.com/s/AKfycbxF7S-m59UCCcPKGknU1sKUCouBdC5VfDtJARhKkRhEMfPDExBVtMjVpfpsUjwtR1w2/exec',
        'verbose_debug_info': 1,
        'display_skip_button': 0
    }

    if os.path.exists(file):
        try:
            config = configparser.ConfigParser()
            config.read(file)
            print(f"Loading {file} ...")

            if 'flask' in config and 'secret_key' in config['flask']:
                config_data['secret_key'] = config.get('flask', 'secret_key')

            if 'debug' in config and 'verbose_debug_info' in config['debug']:
                if config.get('debug', 'verbose_debug_info').lower() == 'on':
                    config_data['verbose_debug_info'] = 1

            if 'debug' in config and 'display_skip_button' in config['debug']:
                if config.get('debug', 'display_skip_button').lower() == 'on':
                    config_data['display_skip_button'] = 1

            if 'google' in config and 'app_script_url' in config['google']:
                config_data['app_script_url'] = config.get('google', 'app_script_url')

            if 'pages' in config and 'page_table' in config['pages']:
                page_list = config.get('pages', 'page_table').split(',')
                config_data['page_table'] = [page.strip() for page in page_list]
            
        except (configparser.NoSectionError, configparser.NoOptionError, configparser.ParsingError) as e:
            raise RuntimeError(f"Error reading config file: {e}")
    else:
        raise RuntimeError(f"Config file {file} not found.")

    return config_data


def render_next_page(page_name):
    return render_template(page_name, page_name=page_name, display_skip_button=display_skip_button)


def get_page_name(index):
    last_index = len(page_table) - 1
    if index >= last_index:
        page_name = page_table[last_index]
    else:
        page_name = page_table[index]
    return page_name


def get_last_page_name():
    page_index = len(page_table) - 1
    return page_table[page_index]


def set_page_index(index):
    if 'page_index' not in session:
        session['page_index'] = 0
    else:
        session['page_index'] = index


def get_current_page_index():
    if 'page_index' not in session:
        session['page_index'] = 0
    return session['page_index']


def initialize_system():
    session.clear()
    session['page_index'] = 0


def debug_print(message):
    if verbose_debug_info:
        print(message)




try:
    config_data = load_config(config_file)
    app.secret_key = config_data['secret_key']
    verbose_debug_info = config_data['verbose_debug_info']
    display_skip_button = config_data['display_skip_button']
    app_script_url = config_data['app_script_url']
    page_table = config_data['page_table']
except RuntimeError as e:
    print(f"{e}")
    exit();


# Error handler -------------------------------
@app.errorhandler(500)
def internal_error(error):
    return render_template('system_error.html', error_message=str(error)), 500


# Routing process -------------------------------
@app.route('/')
def index():
    try:
        debug_print("\n\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        debug_print('Initializing the system ...')
        initialize_system()

        id = request.args.get('id')
        if not id:
            id = str(000000)
        session['id'] = id
        if 'order' not in session:
            session['order'] = []
        session['order'].append('id')

        page = get_page_name(get_current_page_index())
        return render_next_page(page)
    except Exception as e:
        abort(500, description=str(e))


@app.route('/process', methods=['GET', 'POST'])
def process():
    try:
        src_page_name = request.form.get('source')
        current_page_index = get_current_page_index()
        current_page_name = get_page_name(current_page_index)
        dst_page_index = current_page_index + 1
        dst_page_name = get_page_name(dst_page_index)

        debug_print("\n\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        debug_print(f'method: {request.method}')
        debug_print(f'src_page_name: {src_page_name}')
        debug_print(f'current_page_index: {current_page_index}')
        debug_print(f'current_page_name: {current_page_name}')
        debug_print(f'dst_page_index: {dst_page_index}')
        debug_print(f'dst_page_name: {dst_page_name}')

        # Since screen transitions are only performed using the POST method, 
        # any requests that come via the GET method will be redirected to the original page. 
        # This is mainly to handle accesses that occur when the browser's back button is pressed.
        if request.method == 'GET':
            return render_next_page(current_page_name)

        # If the user returns to the initial page by pressing the back button and then clicks the start button from there, 
        # an initialization process will be necessary.
        if current_page_index == 0:
            if 'id' in session:
                id = session['id']
            else:
                id = str(000000)
            
            initialize_system()
            session['id'] = id
            session['start_time'] = datetime.now().isoformat()
            session['order'] = []
            session['order'].append('id')
            session['order'].append('start_time')

        form_data = request.form.to_dict(flat=False)
        debug_print("Form Data Received ---------")
        for key, values in form_data.items():
            if isinstance(values, list):
                session[key] = ', '.join(values)
            else:
                session[key] = values
            debug_print(f"{key}: {session[key]}")

            if 'order' not in session:
                session['order'] = []
            if key not in session['order']:
                session['order'].append(key)
            else:
                session['order'].remove(key)
                session['order'].append(key)

        debug_print("----------------------------")
        for key in session['order']:
            debug_print(f"{key}: {session[key]}")
        debug_print("----------------------------")

        debug_print(f'Going to {dst_page_name} ...')
        set_page_index(dst_page_index)
        return render_next_page(dst_page_name)
    except Exception as e:
        abort(500, description=str(e))


@app.route('/write_to_gsheet', methods=['POST'])
def write_to_gsheet():
    try:
        if 'order' in session:
            session['end_time'] = datetime.now().isoformat()

            session['order'].remove('source')

            start_time = datetime.fromisoformat(session['start_time'])
            end_time = datetime.fromisoformat(session['end_time'])
            duration = end_time - start_time
            duration_str = str(duration)
            session['duration'] = duration_str

            ordered_keys = session['order']
            start_index = ordered_keys.index('start_time')
            ordered_keys.insert(start_index + 1, 'end_time')
            ordered_keys.insert(start_index + 2, 'duration')

            data = [[key, session[key]] for key in ordered_keys]
            response = requests.post(app_script_url, json={"data": data})

            if response.status_code == 200:
                debug_print('Redirecting to the top page...')
                return redirect(url_for('index', id=session['id']))
            else:
                raise Exception(response.text)
        else:
            raise Exception("No data to write")
    except Exception as e:
        abort(500, description=str(e))


def main():
    parser = argparse.ArgumentParser(description="Run the Flask application.")
    parser.add_argument("--port", type=int, help="Port to run the server on.")
    args = parser.parse_args()
    
    port = args.port if args.port else 8080  # デフォルトのポートを8080に設定
    env = os.getenv("FLASK_ENV", "development")
    
    if env == "development":
        print("Using Flask");
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        print("Using Waitress server");
        serve(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    main()
