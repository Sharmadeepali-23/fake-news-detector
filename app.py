import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect

from config import Config
from models import db, User, PredictionHistory
from database import init_db
from forms import LoginForm, NewsDetectionForm, SearchHistoryForm
from predict import predict_news
from utils import generate_pdf_report, generate_csv_export, analyze_text_metadata

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Extensions
csrf = CSRFProtect(app)
init_db(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the Admin Dashboard.'
login_manager.login_message_category = 'warning'

from datetime import datetime, timedelta, timezone

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Context Processor for global layout vars
@app.context_processor
def inject_global_data():
    total_predictions = PredictionHistory.query.count()
    real_count = PredictionHistory.query.filter_by(prediction='REAL NEWS').count()
    fake_count = PredictionHistory.query.filter_by(prediction='FAKE NEWS').count()
    return {
        'global_total_predictions': total_predictions,
        'global_real_count': real_count,
        'global_fake_count': fake_count,
        'current_year': datetime.now(timezone.utc).year
    }

# =========================================================================
# ROUTES
# =========================================================================

@app.route('/')
def home():
    recent_predictions = PredictionHistory.query.order_by(PredictionHistory.created_at.desc()).limit(5).all()
    total = PredictionHistory.query.count()
    real_cnt = PredictionHistory.query.filter_by(prediction='REAL NEWS').count()
    fake_cnt = PredictionHistory.query.filter_by(prediction='FAKE NEWS').count()
    
    accuracy = 96.8  # Default benchmark model accuracy
    
    return render_template(
        'index.html',
        recent_predictions=recent_predictions,
        total_predictions=total,
        real_count=real_cnt,
        fake_count=fake_cnt,
        accuracy=accuracy
    )

@app.route('/detect', methods=['GET', 'POST'])
def detector():
    form = NewsDetectionForm()
    result = None
    metadata = None

    if form.validate_on_submit():
        title = form.title.data or ''
        content = form.content.data
        
        try:
            # Execute ML prediction
            pred_data = predict_news(title, content)
            metadata = analyze_text_metadata(content)
            
            # Save record into SQLite database
            record = PredictionHistory(
                news_title=title if title else (content[:50] + '...'),
                news_content=content,
                prediction=pred_data['prediction'],
                confidence=pred_data['confidence'],
                model_used=pred_data['model_used'],
                word_count=metadata['word_count'],
                user_id=current_user.id if current_user.is_authenticated else None,
                ip_address=request.remote_addr
            )
            db.session.add(record)
            db.session.commit()
            
            result = {
                'id': record.id,
                'title': title,
                'content': content,
                'prediction': pred_data['prediction'],
                'confidence': pred_data['confidence'],
                'model_used': pred_data['model_used'],
                'is_real': pred_data['is_real'],
                'keywords': pred_data['top_keywords'],
                'metadata': metadata
            }
            
            # Handle AJAX Requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                return jsonify({'success': True, 'result': result})

        except FileNotFoundError:
            error_msg = "Model files not trained yet. Please run 'python train_model.py' first!"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(error_msg, 'danger')
        except Exception as e:
            error_msg = f"An error occurred during classification: {str(e)}"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': error_msg}), 500
            flash(error_msg, 'danger')

    return render_template('detector.html', form=form, result=result)

@app.route('/history', methods=['GET', 'POST'])
def history():
    form = SearchHistoryForm(request.args, meta={'csrf': False})
    
    query_str = request.args.get('query', '').strip()
    filter_by = request.args.get('filter_by', 'ALL')
    page = request.args.get('page', 1, type=int)
    
    query = PredictionHistory.query
    
    if query_str:
        query = query.filter(
            (PredictionHistory.news_title.ilike(f'%{query_str}%')) |
            (PredictionHistory.news_content.ilike(f'%{query_str}%'))
        )
        
    if filter_by in ['REAL NEWS', 'FAKE NEWS']:
        query = query.filter(PredictionHistory.prediction == filter_by)
        
    pagination = query.order_by(PredictionHistory.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    records = pagination.items
    
    return render_template('history.html', form=form, records=records, pagination=pagination, query_str=query_str, filter_by=filter_by)

@app.route('/history/delete/<int:id>', methods=['POST'])
def delete_history_item(id):
    record = PredictionHistory.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash('Prediction history record deleted successfully.', 'success')
    return redirect(url_for('history'))

@app.route('/history/clear', methods=['POST'])
def clear_all_history():
    PredictionHistory.query.delete()
    db.session.commit()
    flash('All prediction history cleared.', 'info')
    return redirect(url_for('history'))

@app.route('/history/export')
def export_csv():
    records = PredictionHistory.query.order_by(PredictionHistory.created_at.desc()).all()
    csv_data = generate_csv_export(records)
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=fake_news_predictions_export.csv"}
    )

@app.route('/report/<int:id>')
def download_pdf_report(id):
    record = PredictionHistory.query.get_or_404(id)
    pdf_buffer = generate_pdf_report(record)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Verification_Report_VN-{record.id:06d}.pdf",
        mimetype="application/pdf"
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin():
    total = PredictionHistory.query.count()
    real_cnt = PredictionHistory.query.filter_by(prediction='REAL NEWS').count()
    fake_cnt = PredictionHistory.query.filter_by(prediction='FAKE NEWS').count()
    
    # Calculate avg confidence
    records = PredictionHistory.query.all()
    avg_conf = (sum(r.confidence for r in records) / total) if total > 0 else 95.0
    
    recent_activities = PredictionHistory.query.order_by(PredictionHistory.created_at.desc()).limit(10).all()
    
    return render_template(
        'admin.html',
        total=total,
        real_cnt=real_cnt,
        fake_cnt=fake_cnt,
        avg_conf=round(avg_conf, 1),
        recent_activities=recent_activities
    )

@app.route('/admin/stats-json')
@login_required
def admin_stats_json():
    # Last 7 days distribution
    today = datetime.now(timezone.utc).date()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    
    labels = [d.strftime('%b %d') for d in dates]
    real_daily = []
    fake_daily = []
    
    for d in dates:
        start_dt = datetime.combine(d, datetime.min.time())
        end_dt = datetime.combine(d, datetime.max.time())
        
        r_c = PredictionHistory.query.filter(
            PredictionHistory.created_at >= start_dt,
            PredictionHistory.created_at <= end_dt,
            PredictionHistory.prediction == 'REAL NEWS'
        ).count()
        
        f_c = PredictionHistory.query.filter(
            PredictionHistory.created_at >= start_dt,
            PredictionHistory.created_at <= end_dt,
            PredictionHistory.prediction == 'FAKE NEWS'
        ).count()
        
        real_daily.append(r_c)
        fake_daily.append(f_c)

    real_total = PredictionHistory.query.filter_by(prediction='REAL NEWS').count()
    fake_total = PredictionHistory.query.filter_by(prediction='FAKE NEWS').count()
    
    return jsonify({
        'trend_labels': labels,
        'real_daily': real_daily,
        'fake_daily': fake_daily,
        'pie_data': [real_total, fake_total]
    })

@app.route('/api/sample-news')
def get_sample_news():
    sample_type = request.args.get('type', 'fake')
    
    if sample_type == 'real':
        return jsonify({
            'title': 'Global Climate Summit Reaches Binding Agreement on Renewable Targets',
            'content': 'GENEVA - Representatives from 190 nations concluded a two-week climate conference by ratifying a historic accord to reduce global carbon emissions by 45 percent over the coming decade. The treaty mandates aggressive subsidies for solar and wind grid integration while establishing a green climate fund to support developing nations.'
        })
    else:
        return jsonify({
            'title': 'SECRET DOCS: Alien Spaceship Recovered in Secret Facility, Officials Confirm',
            'content': 'Unverified reports leaking from an undisclosed desert compound claim military personnel discovered an intact extraterrestrial saucer deep underground. Anonymous whistleblowers state that reverse-engineered antigravity engines have been tested secretly for years. Share this article before the government censors it!'
        })

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
