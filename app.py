from flask import Flask, session, render_template, request, redirect, url_for, jsonify, abort
from datetime import datetime
from waitress import serve
import configparser
import os
import sys
import argparse
import requests 

app = Flask(__name__)
config_file = 'system.cfg'
default_page_table = [
    "system_error.html"
]

SECRET_KEY_FILE = 'secret_key.txt'

def generate_secret_key():
    return os.urandom(24)

def load_secret_key():
    if os.path.exists(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, 'rb') as f:
            return f.read()
    else:
        secret_key = generate_secret_key()
        with open(SECRET_KEY_FILE, 'wb') as f:
            f.write(secret_key)
        return secret_key

def load_config(file):
    config_data = {
        'page_table': default_page_table,
        'app_script_url': 'https://script.google.com/a/macros/volocitee.com/s/AKfycbxF7S-m59UCCcPKGknU1sKUCouBdC5VfDtJARhKkRhEMfPDExBVtMjVpfpsUjwtR1w2/exec',
        'projects': {},
        'verbose_debug_info': 1,
        'display_skip_button': 0
    }

    if os.path.exists(file):
        try:
            config = configparser.ConfigParser()
            config.read(file)
            print(f"Loading {file} ...")

            if 'debug' in config:
                if 'verbose_debug_info' in config['debug']:
                    config_data['verbose_debug_info'] = 1 if config.get('debug', 'verbose_debug_info').strip().lower() == 'on' else 0
                if 'display_skip_button' in config['debug']:
                    config_data['display_skip_button'] = 1 if config.get('debug', 'display_skip_button').strip().lower() == 'on' else 0

            if 'google' in config and 'app_script_url' in config['google']:
                config_data['app_script_url'] = config.get('google', 'app_script_url')

            for section_name in config.sections():
                if section_name.startswith('project.'):
                    section = config[section_name]
                    pid = section.get('project_id', '').strip()
                    if not pid:
                        continue
                    proj = {
                        'name': section.get('project_name', '').strip(),
                        'url': section.get('app_script_url', '').strip(),
                    }
                    # Optional per-project debug overrides; absence inherits [debug] global.
                    if 'verbose_debug_info' in section:
                        proj['verbose_debug_info'] = 1 if section.get('verbose_debug_info', '').strip().lower() == 'on' else 0
                    if 'display_skip_button' in section:
                        proj['display_skip_button'] = 1 if section.get('display_skip_button', '').strip().lower() == 'on' else 0
                    config_data['projects'][pid] = proj

            if 'pages' in config and 'page_table' in config['pages']:
                page_list = config.get('pages', 'page_table').split(',')
                config_data['page_table'] = [page.strip() for page in page_list]

        except (configparser.NoSectionError, configparser.NoOptionError, configparser.ParsingError) as e:
            raise RuntimeError(f"Error reading config file: {e}")
    else:
        raise RuntimeError(f"Config file {file} not found.")

    return config_data


def get_app_script_url(project_id):
    if project_id and project_id in projects:
        return projects[project_id]['url']
    return app_script_url


def get_project_name(project_id):
    if project_id and project_id in projects:
        return projects[project_id]['name']
    return ''


def get_verbose_debug_info(project_id):
    if project_id and project_id in projects and 'verbose_debug_info' in projects[project_id]:
        return projects[project_id]['verbose_debug_info']
    return verbose_debug_info


def get_display_skip_button(project_id):
    if project_id and project_id in projects and 'display_skip_button' in projects[project_id]:
        return projects[project_id]['display_skip_button']
    return display_skip_button


def render_next_page(page_name, html_content):
    project_id = session.get('project_id', '')
    return render_template(
        page_name,
        page_name=page_name,
        display_skip_button=get_display_skip_button(project_id),
        session_id=session['session_id'],
        project_id=project_id,
        html_content=html_content,
    )


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
    try:
        pid = session.get('project_id', '')
    except RuntimeError:
        pid = ''
    if get_verbose_debug_info(pid):
        print(message)


def is_pc(user_agent):
    if not user_agent:          # catches None and empty string
        return False

    pc_agents = ['Windows NT', 'Macintosh', 'X11']
    for agent in pc_agents:
        if agent in user_agent:
            return True
    return False


@app.before_request
def block_non_pc():
    user_agent = request.headers.get('User-Agent')
    if not is_pc(user_agent):
        return render_template('system_error.html', error_message='PCからアクセスしてください'), 500


try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True) 
    config_data = load_config(config_file)
    app.secret_key = load_secret_key()
    verbose_debug_info = config_data['verbose_debug_info']
    display_skip_button = config_data['display_skip_button']
    app_script_url = config_data['app_script_url']
    projects = config_data['projects']
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

        session_id = request.args.get('session_id')
        if not session_id:
            session_id = str(000000)
        session['session_id'] = session_id

        project_id = request.args.get('project_id')
        if not project_id:
            project_id = ''
        session['project_id'] = project_id
        session['project_name'] = get_project_name(project_id)

        if 'order' not in session:
            session['order'] = []
        session['order'].append('project_id')
        session['order'].append('project_name')
        session['order'].append('session_id')

        page = get_page_name(get_current_page_index())
        return render_next_page(page, "")
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
        html_content = ""

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
            return render_next_page(current_page_name, html_content)

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
                # Keep project_id, project_name, session_id at the front of the
                # order list so they always land in columns A, B, C of the data sheet.
                if key not in ('session_id', 'project_id', 'project_name'):
                    session['order'].remove(key)
                    session['order'].append(key)

        session_id = session.get('session_id', str(000000))
        project_id = session.get('project_id', '')
        debug_print(f'project_id: {project_id}')
        debug_print(f'session_id: {session_id}')

        # If the user returns to the initial page by pressing the back button and then clicks the start button from there,
        # an initialization process will be necessary.
        if current_page_index == 0:
            initialize_system()
            session['session_id'] = session_id
            session['project_id'] = project_id
            session['project_name'] = get_project_name(project_id)
            session['start_time'] = datetime.now().isoformat()
            session['order'] = []
            session['order'].append('project_id')
            session['order'].append('project_name')
            session['order'].append('session_id')
            session['order'].append('start_time')

            response = requests.get(get_app_script_url(project_id), params={'session_id': session_id})
            data = response.json()
            # debug_print(data)
            if data['status'] == 'error':
                raise Exception(data['message'])

            html_content = data['message']

            debug_print(f'doGet {session_id} >>>>>>>>> {data}')
        # debug_print('------------')
        # debug_print(data['message'])
        # debug_print('------------')



        debug_print("----------------------------")
        for key in session['order']:
            debug_print(f"{key}: {session[key]}")
        debug_print("----------------------------")

        debug_print(f'Going to {dst_page_name} ...')
        set_page_index(dst_page_index)
        return render_next_page(dst_page_name, html_content)
    except Exception as e:
        abort(500, description=str(e))


@app.route('/completed')
def completed():
    return render_template('4_completion.html')


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
            project_id = session.get('project_id', '')
            response = requests.post(get_app_script_url(project_id), json={"data": data})

            if response.status_code == 200:
                debug_print('Redirecting to the completion page...')
                return redirect(url_for('completed'))
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
    env = os.getenv("FLASK_ENV", "production")
    
    if env == "development":
        print("Using Flask development server")
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        print("Using Waitress server")
        serve(app, host="0.0.0.0", port=port, threads=16, connection_limit=1000, channel_timeout=5)
        # serve(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    main()
