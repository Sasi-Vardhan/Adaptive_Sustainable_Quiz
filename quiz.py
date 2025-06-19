from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
import random
import csv
import os
import math
from fuzzy_rules import setup_fuzzy_system
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from fuzzy_rules import setup_fuzzy_system
import json
from firestore_config import db
from middleware.auth_middleware import login_required
import uuid
quiz_bp = Blueprint('quiz', __name__)

# Initialize fuzzy system
fuzzy_difficulty = setup_fuzzy_system()

# Initialize fuzzy system
fuzzy_difficulty = setup_fuzzy_system()

# Load questions from CSV
def load_questions(lesson):
    paths=["Questions/Sustainability_Questions.csv","Questions/generative_ai_questions.csv"]
    questions = []
    try:
        if not lesson:
            print("Error: No lesson provided")
            return []
        session["LO"]=lesson
        if(session["choice"] == 'sustainability'):
            path=paths[0]
        else:
            path=paths[1]
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            required_fields = ['question', 'option1', 'option2', 'option3', 'option4', 'correctAnswer', 'level', 'bloomsLevel', 'learningOutcome']
            
            if not all(field in reader.fieldnames for field in required_fields):
                print(f"Error: CSV missing required fields. Found: {reader.fieldnames}")
                return []
            
            count = 0
            for row in reader:
                if row.get('learningOutcome') == lesson and all(field in row for field in required_fields):
                    if row['level'] in ['Easy', 'Medium', 'Hard']:
                        row['level'] = row['level'].capitalize()
                        questions.append(row)
                        count += 1
            print(f"Loaded {count} questions for lesson: {lesson}")
    except FileNotFoundError:
        print("Error: Sustainability_Questions.csv not found")
        return []
    except Exception as e:
        print(f"Error loading questions: {str(e)}")
        return []
    return questions

def select_difficulty(pe, pm, ph, easy_correct_streak, medium_correct_streak, total_correct, success_rate):
    print(f"select_difficulty inputs: pe={pe}, pm={pm}, ph={ph}, "
          f"easy_streak={easy_correct_streak}, medium_streak={medium_correct_streak}, "
          f"total_correct={total_correct}, success_rate={success_rate}")
    
    fuzzy_difficulty.input['total_correct'] = total_correct
    fuzzy_difficulty.input['success_rate'] = success_rate
    fuzzy_difficulty.input['p_e'] = pe
    fuzzy_difficulty.input['p_m'] = pm
    fuzzy_difficulty.input['p_h'] = ph
    fuzzy_difficulty.input['easy_streak'] = easy_correct_streak
    fuzzy_difficulty.input['medium_streak'] = medium_correct_streak

    try:
        fuzzy_difficulty.compute()
        diff_value = fuzzy_difficulty.output['difficulty']
        print(f"Fuzzy system output: diff_value={diff_value}")
    except Exception as e:
        print(f"Error in fuzzy system computation: {str(e)}")
        diff_value = 1.0

    if diff_value < 0.7:
        return "Easy", easy_correct_streak, medium_correct_streak
    elif diff_value < 1.7:
        return "Medium", easy_correct_streak, medium_correct_streak
    else:
        return "Hard", easy_correct_streak, medium_correct_streak

def updateProbabilities(pe, pm, ph, label, isCorrect, easy_correct_streak=0, medium_correct_streak=0):
    alpha_h = 0.15
    alpha_e = alpha_h / 2
    alpha_m = alpha_h / 2.6
    beta = 0.05
    
    label = label.capitalize()
    if not (0 <= pe <= 1 and 0 <= pm <= 1 and 0 <= ph <= 1) or label not in ["Easy", "Medium", "Hard"]:
        return pe, pm, ph, easy_correct_streak, medium_correct_streak
    
    isCorrect = 1 if isCorrect else 0
    pe_new, pm_new, ph_new = pe, pm, ph
    
    if isCorrect:
        if label == "Easy":
            easy_correct_streak += 1
            medium_correct_streak = 0
        elif label == "Medium":
            medium_correct_streak += 1
            easy_correct_streak = 0
        else:
            easy_correct_streak = 0
            medium_correct_streak = 0
    else:
        if label == "Easy":
            easy_correct_streak = 0
        elif label == "Medium":
            medium_correct_streak = 0
    
    if label == "Easy":
        pe_new = (1 - alpha_e) * pe + alpha_e * isCorrect
    elif label == "Medium":
        pm_new = (1 - alpha_m) * pm + alpha_m * isCorrect
    else:
        ph_new = (1 - alpha_h) * ph + alpha_h * isCorrect
    
    if isCorrect:
        if label == "Medium":
            pe_new = pe + beta * (1 - pe)
        elif label == "Hard":
            pe_new = pe + beta * (1 - pe)
            pm_new = pm + beta * (1 - pm)
    
    pe_new = max(0, min(1, pe_new))
    pm_new = max(0, min(1, pm_new))
    ph_new = max(0, min(1, ph_new))
    
    if pe_new < pm_new:
        pe_new = pm_new
    if pm_new < ph_new:
        pm_new = ph_new
    if pm_new > pe_new:
        pm_new = pe_new
    if ph_new > pm_new:
        ph_new = pm_new
    
    return pe_new, pm_new, ph_new, easy_correct_streak, medium_correct_streak

@quiz_bp.route('/set_lesson', methods=['POST'])
@login_required
def set_lesson():
    lesson = request.form.get('lesson')
    if lesson:
        session['lesson'] = lesson
        session['user_id'] = 'test_user'
        print(f"Lesson set to: {lesson}")
        session.pop('questions', None)
        return redirect(url_for('quiz.quiz'))
    return "No lesson selected", 400

@quiz_bp.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if 'lesson' not in session:
        return "No lesson selected. Please select a lesson first.", 400
    
    if 'questions' not in session:
        session['questions'] = load_questions(session['lesson'])
        session.modified = True
    
    QUESTIONS = session['questions']
    if not QUESTIONS:
        return "No questions available for this lesson.", 500

    if 'question_count' not in session:
        print("Initializing session variables")
        session['question_count'] = 0
        session['score'] = 0
        session['easy'] = 0
        session['medium'] = 0
        session['hard'] = 0
        session['easy_incorrect'] = 0
        session['medium_incorrect'] = 0
        session['hard_incorrect'] = 0
        session['total_correct'] = 0
        session['easy_total'] = 0
        session['medium_total'] = 0
        session['hard_total'] = 0
        session['pe'] = 1/3
        session['pm'] = 1/3
        session['ph'] = 1/3
        session['easy_streak'] = 0
        session['medium_streak'] = 0
        session['hard_to_give'] = 0
        session['medium_to_give'] = 0
        session['asked'] = []
        session['total_questions'] = 15
        session['current_question'] = None
        session['processed_questions'] = []
        session['current_difficulty'] = None
        session.modified = True

    print(f"Before request: question_count={session['question_count']}, asked={session['asked']}, total_correct={session['total_correct']}, "
          f"easy_streak={session['easy_streak']}, medium_streak={session['medium_streak']}, "
          f"hard_to_give={session['hard_to_give']}, medium_to_give={session['medium_to_give']}, "
          f"Easy: {session['easy']}/{session['easy_total']}, Medium: {session['medium']}/{session['medium_total']}, Hard: {session['hard']}/{session['hard_total']}")
#This block is made to tell the user that Quiz is completed and storing results
    if session['question_count'] >= session['total_questions']:
        e, m, h = session.get('easy', 0), session.get('medium', 0), session.get('hard', 0)
        ei, mi, hi = session.get('easy_incorrect', 0), session.get('medium_incorrect', 0), session.get('hard_incorrect', 0)
        et, mt, ht = session.get('easy_total', 0), session.get('medium_total', 0), session.get('hard_total', 0)
        total = session['total_questions']
        score = (e * 1 + m * 3.5 + h * 5.5) / (total * (1 + 3.5 + 5.5) / 3) if total > 0 else 0
        print(f"Quiz Complete: Easy: {e}/{et}, Medium: {m}/{mt}, Hard: {h}/{ht}, Score={score:.2f}")
        # Calculate accuracy for each difficulty
        easy_accuracy = e / et if et > 0 else 0
        medium_accuracy = m / mt if mt > 0 else 0
        hard_accuracy = h / ht if ht > 0 else 0

        # Convert probabilities to performance (scale 0-100)
        easy_performance = round(session['pe'] * 100)
        medium_performance = round(session['pm'] * 100)
        hard_performance = round(session['ph'] * 100)

        # Prepare the results in JSON format
        quiz_results = {
            "email": session['email'],
            'subject':session['choice'],
            "total_correct": session['total_correct'],
            "total_questions": total,
            "overall_score": round(score, 2),
            "learning_objective":session["LO"],
            "easy": {
                "correct": e,
                "total_shown": et,
                "accuracy": round(easy_accuracy, 2),
                "performance": easy_performance
            },
            "medium": {
                "correct": m,
                "total_shown": mt,
                "accuracy": round(medium_accuracy, 2),
                "performance": medium_performance
            },
            "hard": {
                "correct": h,
                "total_shown": ht,
                "accuracy": round(hard_accuracy, 2),
                "performance": hard_performance
            }
        }

        # Store results in Firestore with email as the document ID
        try:
            doc_id = f"{session['email']}_{session['LO']}_{uuid.uuid4().hex}"
            db.collection('quiz_results').document(doc_id).set(quiz_results)
        except Exception as e:
            print(f"Error storing quiz results in Firestore: {str(e)}")
        template_data = {
            'score': score,
            'easy': e,
            'medium': m,
            'hard': h,
            'easy_incorrect': ei,
            'medium_incorrect': mi,
            'hard_incorrect': hi,
            'total': total,
            'pe': session['pe'],
            'pm': session['pm'],
            'ph': session['ph']
        }
        
        keys_to_remove = [key for key in session.keys() if key != 'email']
        NC = ['email', 'choice', 'user_id', 'key']
        for key in keys_to_remove:
            if key not in NC:
                session.pop(key, None)
        # return render_template('feedback.html', **template_data)
        return redirect(url_for("LO.Learning"))

    if request.method == 'POST':
        selected = request.form.get('answer')
        question_data = session.get('current_question')
        
        if question_data:
            current_index = session.get('current_index')
            if current_index in session.get('processed_questions', []):
                print(f"Question {current_index} already processed, skipping")
                return redirect(url_for('quiz.quiz'))

            is_correct = selected == question_data['correctAnswer']
            if is_correct:
                session['score'] = session.get('score', 0) + 1
                session['total_correct'] = session.get('total_correct', 0) + 1
                if question_data['level'] == "Easy":
                    session['easy'] = session.get('easy', 0) + 1
                elif question_data['level'] == "Medium":
                    session['medium'] = session.get('medium', 0) + 1
                else:
                    session['hard'] = session.get('hard', 0) + 1
            else:
                if question_data['level'] == "Easy":
                    session['easy_incorrect'] = session.get('easy_incorrect', 0) + 1
                elif question_data['level'] == "Medium":
                    session['medium_incorrect'] = session.get('medium_incorrect', 0) + 1
                else:
                    session['hard_incorrect'] = session.get('hard_incorrect', 0) + 1

            if question_data['level'] == "Easy":
                session['easy_total'] = session.get('easy_total', 0) + 1
            elif question_data['level'] == "Medium":
                session['medium_total'] = session.get('medium_total', 0) + 1
            else:
                session['hard_total'] = session.get('hard_total', 0) + 1
            
            pe, pm, ph, easy_streak, medium_streak = updateProbabilities(
                session['pe'], session['pm'], session['ph'], question_data['level'], 
                is_correct, session['easy_streak'], session['medium_streak']
            )
            session['pe'], session['pm'], session['ph'] = pe, pm, ph
            session['easy_streak'], session['medium_streak'] = easy_streak, medium_streak

            if easy_streak >= 2 and session['medium_to_give'] == 0 and session['hard_to_give'] == 0:
                session['medium_to_give'] = 4
                print(f"Triggered 4 Medium questions due to easy_streak={easy_streak}")
            if medium_streak >= 2 and session['hard_to_give'] == 0:
                session['hard_to_give'] = 3
                session['medium_to_give'] = 0
                print(f"Triggered 3 Hard questions due to medium_streak={medium_streak}")
            
            print(f"Question {session['question_count'] + 1} ({question_data['level']}): "
                  f"pe={pe:.4f}, pm={pm:.4f}, ph={ph:.4f}, Correct={is_correct}")
            
            session['question_count'] = session.get('question_count', 0) + 1
            session['processed_questions'] = session.get('processed_questions', []) + [current_index]
            session['current_question'] = None
            session['current_index'] = None
            session['current_difficulty'] = None
            session.modified = True
            
        print(f"After POST: question_count={session['question_count']}, asked={session['asked']}, total_correct={session['total_correct']}, "
              f"easy_streak={session['easy_streak']}, medium_streak={session['medium_streak']}, "
              f"hard_to_give={session['hard_to_give']}, medium_to_give={session['medium_to_give']}, "
              f"Easy: {session['easy']}/{session['easy_total']}, Medium: {session['medium']}/{session['medium_total']}, Hard: {session['hard']}/{session['hard_total']}")
        return redirect(url_for('quiz.quiz'))

    current_difficulty = session.get('current_difficulty', 'Easy')
    if current_difficulty == "Easy":
        total = session.get('easy_total', 0)
        correct = session.get('easy', 0)
    elif current_difficulty == "Medium":
        total = session.get('medium_total', 0)
        correct = session.get('medium', 0)
    else:
        total = session.get('hard_total', 0)
        correct = session.get('hard', 0)
    success_rate = correct / total if total > 0 else 0.5

    if session['question_count'] == 0:
        difficulty = "Easy"
    elif session['question_count'] == 1:
        difficulty = "Medium"
    elif session['question_count'] == 2:
        difficulty = "Hard"
    else:
        if session['hard_to_give'] > 0:
            difficulty = "Hard"
            session['hard_to_give'] -= 1
            print(f"Enforcing Hard question, hard_to_give remaining: {session['hard_to_give']}")
        elif session['medium_to_give'] > 0:
            difficulty = "Medium"
            session['medium_to_give'] -= 1
            print(f"Enforcing Medium question, medium_to_give remaining: {session['medium_to_give']}")
        else:
            difficulty, session['easy_streak'], session['medium_streak'] = select_difficulty(
                session['pe'], session['pm'], session['ph'], 
                session['easy_streak'], session['medium_streak'],
                session['total_correct'], success_rate
            )
        session.modified = True
    
    available_questions = [
        (i, q) for i, q in enumerate(QUESTIONS) 
        if q['level'] == difficulty and i not in session.get('asked', [])
    ]
    
    if not available_questions:
        available_questions = [
            (i, q) for i, q in enumerate(QUESTIONS) if i not in session.get('asked', [])
        ]
        if not available_questions:
            session.clear()
            return "✅ Quiz Complete! No more questions available."

    index, question_data = random.choice(available_questions)
    session['asked'] = session.get('asked', []) + [index]
    session['current_question'] = question_data
    session['current_index'] = index
    session['current_difficulty'] = difficulty
    session.modified = True

    if len(session['asked']) != session['question_count'] + 1:
        print(f"Warning: Mismatch detected! question_count={session['question_count']}, asked={len(session['asked'])}")

    question_text = question_data['question']
    options = [
        question_data['option1'],
        question_data['option2'],
        question_data['option3'],
        question_data['option4']
    ]
    question_diff = question_data.get('level', 'Unknown').lower()

    print(f"After GET: question_count={session['question_count']}, asked={session['asked']}, total_correct={session['total_correct']}, "
          f"selected_difficulty={difficulty}, "
          f"Easy: {session['easy']}/{session['easy_total']}, Medium: {session['medium']}/{session['medium_total']}, Hard: {session['hard']}/{session['hard_total']}")
    
    return render_template(
        "quiz.html",
        question_text=question_text,
        options=options,
        index=session['question_count'] + 1,
        total=session['total_questions'],
        question_level=question_data["bloomsLevel"],
        question_diff=question_diff
    )


# @quiz_bp.route('/Learning')
# def Learning():
#     # Clear quiz-related session variables
#     keys_to_clear = [
#         'question_count',
#         'score',
#         'easy',
#         'medium',
#         'hard',
#         'easy_incorrect',
#         'medium_incorrect',
#         'hard_incorrect',
#         'total_correct',
#         'easy_total',
#         'medium_total',
#         'hard_total',
#         'pe',
#         'pm',
#         'ph',
#         'easy_streak',
#         'medium_streak',
#         'hard_to_give',
#         'medium_to_give',
#         'asked',
#         'total_questions',
#         'current_question',
#         'processed_questions',
#         'current_difficulty'
#     ]

#     for key in keys_to_clear:
#         session.pop(key, None)

#     session.modified = True
#     return render_template('LB.html')
