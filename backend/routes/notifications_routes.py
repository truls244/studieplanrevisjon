from flask import Flask, jsonify, request, Blueprint
from app.models import Course, Studyprogram, Institute, Studyplan, Notifications, User, Semester, SemesterCourses
from app import db
from services import ServiceFactory
from flask_jwt_extended import  jwt_required


# http://localhost:5000/backend/notifications/
# LA LINJÅ OPPFOR STÅ - brukan te å lett henta URLen te POSTMAN.

# Create a Blueprint
notification_bp = Blueprint('notifications', __name__)

# Notification
# get notifications
@notification_bp.route("/", methods=["GET"])
@jwt_required()
def get_notifications():
    try:
        program_id = request.args.get("program_id")
        if not program_id:
            return jsonify({"error": "Program ID is required"}), 400

        notifications = Notifications.query.filter_by(program_id=program_id).order_by(Notifications.created_at.desc()).all()

        # Add term details if applicable
        for notification in notifications:
            if notification.noti_type == "course":
                course = Course.query.get(notification.noti_id)
                if course:
                    semester_course = SemesterCourses.query.filter_by(course_id=course.id).first()
                    if semester_course:
                        notification.course_code = course.courseCode

        return jsonify([notification.serialize() for notification in notifications]), 200
    except Exception as e:
        print(f"Error fetching notifications: {str(e)}")
        return jsonify({"error": str(e)}), 500



@notification_bp.route('/create-noti/prog', methods=['POST'])
@jwt_required()
def create_prog_notification():
    try:
        data = request.json
        print(f"Received data: {data}")

        source_program_id = data.get('source_program_id')
        term_conflicts = data.get('term_conflicts', [])
        # fetched_notifications = data.get('fetched_notifications', [])

        if not source_program_id or not term_conflicts:
            print("Missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        notification_service = ServiceFactory.get_notification_service()
        notifications = notification_service.create_prog_notifications(
            source_program_id=source_program_id,
            term_conflicts=term_conflicts,
            # fetched_notifications=fetched_notifications,
        )

        # Return the created notifications
        print(f"Notifications created: {notifications}")
        return jsonify({"notifications": notifications}), 201

    except Exception as e:
        print(f"Error creating notification: {str(e)}")
        return jsonify({"error": str(e)}), 500


@notification_bp.route('/get-group/<string:group_id>', methods=['GET'])
@jwt_required()
def get_notification_group(group_id):
    try:
        notifications = Notifications.query.filter_by(notification_group_id=group_id).all()

        courses = []
        for notification in notifications:
            if notification.noti_type == "course":
                course = Course.query.get(notification.noti_id)
                if course:
                    courses.append({
                        "course_id": course.id,
                        "course_code": course.courseCode,
                        "course_name": course.name,
                        "notification_message": notification.message,
                        "program_id": notification.program_id
                    })

        return jsonify(courses), 200
    except Exception as e:
        print(f"Error fetching courses by group ID: {str(e)}")
        return jsonify({"error": str(e)}), 500


@notification_bp.route('/find-notification-group', methods=['POST'])
@jwt_required()
def find_notification_group():
    try:
        data = request.get_json()
        affected_programs = data.get('affected_programs', [])
        noti_id = data.get('noti_id')
        target_term = data.get('target_term')

        if not affected_programs or not noti_id or not target_term:
            return jsonify({"error": "Missing required fields"}), 400

        notification_service = ServiceFactory.get_notification_service()

        group_id = notification_service.find_notification_group_id(affected_programs, noti_id, target_term)

        if group_id:
            return jsonify({"notification_group_id": group_id}), 200
        else:
            return jsonify({"message": "No notification group found"}), 404
    except Exception as e:
        print(f"Error in /find-notification-group route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@notification_bp.route('/<int:notification_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_program_notification(notification_id):
    try:
        notification_service = ServiceFactory.get_notification_service()
        notification = notification_service.delete_notification(notification_id)

        if not notification:
            return jsonify({"success": False, "message": "Notification not found"}), 404

        return jsonify({"success": True, "message": "Notification deleted"}), 200
    except Exception as e:
        print(f"Error deleting notification: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


# @notification_bp.route("/<int:program_id>/notifications", methods=["GET"])
# def get_program_notifications(program_id):
#     try:
#         notification_service = ServiceFactory.get_notification_service()
#         notifications = notification_service.get_notifications_by_program(program_id)
#         unread_count = sum(1 for n in notifications if not n.get('is_acknowledged', False))
        
#         return jsonify({
#             'notifications': notifications,
#             'unread_count': unread_count
#         }), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


@notification_bp.route("/notifications", methods=["DELETE"])
@jwt_required()
def delete_all_notifications():
    try:
        notification_service = ServiceFactory.get_notification_service()
        notification_service.delete_all_notifications()
        return jsonify({"success": True, "message": "All notifications deleted"}), 200
    except Exception as e:
        print(f"Error deleting all notifications: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
