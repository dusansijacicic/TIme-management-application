from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db, csrf
from app.models import UserPreference
from . import settings

@settings.route('/preferences')
@login_required
def preferences():
    """Display user preferences page"""
    preferences = current_user.get_color_preferences()
    return render_template('settings/preferences.html', preferences=preferences)

@settings.route('/api/update-colors', methods=['POST'])
@login_required
@csrf.exempt
def update_colors():
    """Update user's color preferences"""
    try:
        data = request.get_json()
        primary_color = data.get('primary_color')
        secondary_color = data.get('secondary_color')
        text_color = data.get('text_color', 'primary')
        custom_primary_color = data.get('custom_primary_color', '#10b981')
        custom_secondary_color = data.get('custom_secondary_color', '#ffffff')
        custom_text_color = data.get('custom_text_color', '#1f2937')
        
        # Validate colors
        valid_primary_colors = ['emerald', 'purple', 'chocolate', 'blue', 'red', 'orange', 'teal', 'pink', 'custom']
        valid_secondary_colors = ['white', 'emerald', 'purple', 'chocolate', 'blue', 'red', 'orange', 'teal', 'pink', 'custom']
        valid_text_colors = ['primary', 'secondary', 'light', 'white', 'dark', 'custom']
        
        if primary_color not in valid_primary_colors:
            return jsonify({'success': False, 'message': 'Nevažeća primarna boja'})
        
        if secondary_color not in valid_secondary_colors:
            return jsonify({'success': False, 'message': 'Nevažeća sekundarna boja'})
        
        if text_color not in valid_text_colors:
            return jsonify({'success': False, 'message': 'Nevažeća boja teksta'})
        
        # Validate hex colors if custom
        import re
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        
        if primary_color == 'custom' and not hex_pattern.match(custom_primary_color):
            return jsonify({'success': False, 'message': 'Nevažeća hex boja za primarnu boju'})
        
        if secondary_color == 'custom' and not hex_pattern.match(custom_secondary_color):
            return jsonify({'success': False, 'message': 'Nevažeća hex boja za sekundarnu boju'})
        
        if text_color == 'custom' and not hex_pattern.match(custom_text_color):
            return jsonify({'success': False, 'message': 'Nevažeća hex boja za boju teksta'})
        
        # Update preferences
        preferences = current_user.get_color_preferences()
        preferences.primary_color = primary_color
        preferences.secondary_color = secondary_color
        preferences.text_color = text_color
        preferences.custom_primary_color = custom_primary_color
        preferences.custom_secondary_color = custom_secondary_color
        preferences.custom_text_color = custom_text_color
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Boje su uspešno ažurirane'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Greška pri ažuriranju: {str(e)}'})

@settings.route('/api/get-colors')
@login_required
@csrf.exempt
def get_colors():
    """Get user's current color preferences"""
    preferences = current_user.get_color_preferences()
    return jsonify({
        'primary_color': preferences.primary_color,
        'secondary_color': preferences.secondary_color,
        'text_color': preferences.text_color,
        'custom_primary_color': preferences.custom_primary_color,
        'custom_secondary_color': preferences.custom_secondary_color,
        'custom_text_color': preferences.custom_text_color
    }) 