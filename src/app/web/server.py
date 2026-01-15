"""
Web server module for FIB Manager.
Provides a minimal web interface for schedule management.
"""

import os
import webbrowser
import threading
from typing import Dict, List, Any, Optional

from flask import Flask, render_template, request, jsonify, redirect, url_for

from app.core.utils import get_default_quadrimester, normalize_languages, parse_blacklist
from app.core.parser import parse_classes_data, split_schedule_by_group_type
from app.core.schedule_generator import get_schedule_combinations
from app.api import fetch_classes_data, fetch_subject_names, generate_schedule_url


# Initialize Flask app with correct template and static folders
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = 'fib-manager-secret-key'


@app.route('/')
def index():
    """Home page with navigation to main features."""
    default_quad = get_default_quadrimester()
    return render_template('index.html', default_quad=default_quad)


@app.route('/subjects')
def subjects():
    """Display subjects for a quadrimester."""
    quad = request.args.get('quad', get_default_quadrimester())
    lang = request.args.get('lang', 'en')
    
    try:
        raw_data = fetch_classes_data(quad, lang)
        parsed_data = parse_classes_data(raw_data)
        names = fetch_subject_names(lang)
        
        subjects_list = [
            {'code': code, 'name': names.get(code, code)}
            for code in sorted(parsed_data.keys())
        ]
        
        return render_template('subjects.html', 
                             subjects=subjects_list,
                             quad=quad,
                             lang=lang,
                             default_quad=get_default_quadrimester())
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/subjects/api')
def subjects_api():
    """API endpoint for subjects data."""
    quad = request.args.get('quad', get_default_quadrimester())
    lang = request.args.get('lang', 'en')
    
    try:
        raw_data = fetch_classes_data(quad, lang)
        parsed_data = parse_classes_data(raw_data)
        names = fetch_subject_names(lang)
        
        subjects_list = [
            {'code': code, 'name': names.get(code, code)}
            for code in sorted(parsed_data.keys())
        ]
        
        return jsonify({
            'success': True,
            'quad': quad,
            'lang': lang,
            'subjects': subjects_list
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/search')
def search():
    """Schedule search form."""
    default_quad = get_default_quadrimester()
    return render_template('search.html', default_quad=default_quad)


@app.route('/search/results', methods=['GET', 'POST'])
def search_results():
    """Display schedule search results."""
    if request.method == 'POST':
        quad = request.form.get('quad', get_default_quadrimester())
        subjects_input = request.form.get('subjects', '')
        start_hour = int(request.form.get('start_hour', 8))
        end_hour = int(request.form.get('end_hour', 20))
        languages_input = request.form.get('languages', '')
        max_days = int(request.form.get('max_days', 5))
        freedom = request.form.get('freedom') == 'on'
        max_dead_hours = int(request.form.get('max_dead_hours', -1))
        blacklist_input = request.form.get('blacklist', '')
    else:
        quad = request.args.get('quad', get_default_quadrimester())
        subjects_input = request.args.get('subjects', '')
        start_hour = int(request.args.get('start_hour', 8))
        end_hour = int(request.args.get('end_hour', 20))
        languages_input = request.args.get('languages', '')
        max_days = int(request.args.get('max_days', 5))
        freedom = request.args.get('freedom', 'false').lower() == 'true'
        max_dead_hours = int(request.args.get('max_dead_hours', -1))
        blacklist_input = request.args.get('blacklist', '')
    
    # Parse inputs
    subjects = [s.strip().upper() for s in subjects_input.split(',') if s.strip()]
    languages = normalize_languages([l.strip() for l in languages_input.split(',') if l.strip()])
    blacklist = parse_blacklist([b.strip() for b in blacklist_input.split(',') if b.strip()])
    
    if not subjects:
        return render_template('error.html', error='No subjects specified')
    
    try:
        relax_days = 5 - max_days
        same_subgroup = not freedom
        
        result = get_schedule_combinations(
            quad, subjects, start_hour, end_hour,
            languages, same_subgroup, relax_days,
            blacklist, max_dead_hours
        )
        
        # Process schedules for display
        schedules = result.get('schedules', [])
        
        return render_template('results.html',
                             schedules=schedules,
                             total=result.get('total', 0),
                             quad=quad,
                             subjects=subjects,
                             start_hour=start_hour,
                             end_hour=end_hour,
                             default_quad=get_default_quadrimester())
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template('error.html', error=str(e))


@app.route('/search/api', methods=['POST'])
def search_api():
    """API endpoint for schedule search."""
    data = request.get_json() or {}
    
    quad = data.get('quad', get_default_quadrimester())
    subjects = [s.upper() for s in data.get('subjects', [])]
    start_hour = data.get('start_hour', 8)
    end_hour = data.get('end_hour', 20)
    languages = normalize_languages(data.get('languages', []))
    max_days = data.get('max_days', 5)
    freedom = data.get('freedom', False)
    max_dead_hours = data.get('max_dead_hours', -1)
    blacklist = parse_blacklist(data.get('blacklist', []))
    
    if not subjects:
        return jsonify({'success': False, 'error': 'No subjects specified'})
    
    try:
        relax_days = 5 - max_days
        same_subgroup = not freedom
        
        result = get_schedule_combinations(
            quad, subjects, start_hour, end_hour,
            languages, same_subgroup, relax_days,
            blacklist, max_dead_hours
        )
        
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html', default_quad=get_default_quadrimester())


def open_browser(port: int):
    """Open the web browser after a short delay."""
    import time
    time.sleep(1.5)
    webbrowser.open(f'http://127.0.0.1:{port}')


def run_server(host: str = '127.0.0.1', port: int = 5000, debug: bool = False, open_browser_flag: bool = True):
    """
    Run the Flask web server.
    
    Args:
        host: Host address to bind to
        port: Port number to listen on
        debug: Enable debug mode
        open_browser_flag: Open browser automatically
    """
    if open_browser_flag:
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    print(f"\n  ╭─────────────────────────────────────────╮")
    print(f"  │  FIB Manager Web Interface              │")
    print(f"  │  Running at: http://{host}:{port}       │")
    print(f"  │  Press Ctrl+C to stop                   │")
    print(f"  ╰─────────────────────────────────────────╯\n")
    
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == '__main__':
    run_server(debug=True)
