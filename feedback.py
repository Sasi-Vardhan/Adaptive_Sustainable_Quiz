from flask import Flask, session, redirect, render_template, flash, Blueprint, url_for, request
from middleware.auth_middleware import login_required
from firestore_config import db
from google.cloud.firestore_v1.field_path import FieldPath

feedback = Blueprint("feedback", __name__)

@feedback.route('/feedback', methods=['GET'])
@login_required
def show_feedback():
    if 'email' not in session:
        flash("Please log in to view feedback.", "error")
        return redirect(url_for('auth.login'))

    email = session['email']
    subject = session.get('choice')
    selected_lo = request.args.get('lo')  # Optional query param: ?lo=LO2

    valid_outcomes = ['LO1', 'LO2', 'LO3', 'LO4', 'LO5']
    all_results = {}

    try:
        outcomes_to_check = [selected_lo] if selected_lo in valid_outcomes else valid_outcomes

        for lo in outcomes_to_check:
            # logger.info(f"Querying for: email={email}, subject={subject}, LO={lo}")
            # Corrected Firestore query using 'where'
            query = (
                db.collection('quiz_results')
                .where('learning_objective', '==', lo) 
                .where('email', '==', email)
                .where('subject', '==', subject)
            )


            # Execute query and process results
            for doc in query.stream():
                results = doc.to_dict()

                # Validate required fields
                required_keys = ['overall_score', 'total_correct', 'total_questions', 'easy', 'medium', 'hard']
                if all(k in results for k in required_keys):
                    overall_percentage = int(results['overall_score'] * 100)
                    average_score = round((results['total_correct'] * 6) / results['total_questions'], 1)
                    best_performance = max(
                        results['easy']['performance'],
                        results['medium']['performance'],
                        results['hard']['performance']
                    )

                    all_results[lo] = {
                        'results': results,
                        'overall_percentage': overall_percentage,
                        'average_score': average_score,
                        'best_performance': best_performance
                    }

        return render_template("Result.html", all_results=all_results, no_data=(not all_results))
    except Exception as e:
        print(f"Error: {str(e)}")
        flash("Something went wrong while fetching your feedback.", "error")
        return redirect(url_for('main'))
