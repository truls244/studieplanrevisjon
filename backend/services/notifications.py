from app import db, mail
from app.models import User, Studyprogram, Studyplan, Institute, Course, Notifications
import threading
from datetime import datetime
from flask import request, jsonify
from flask_mail import Message
import uuid

class NotificationService:
    def __init__(self, db_session=None, user_service=None, studyprogram_service=None):
        self.db = db_session or db.session
        self.user_service = user_service
        self.studyprogram_service = studyprogram_service

    def generate_notification_group_id(self):
        return str(uuid.uuid4())

    def find_notification_group_id(self, affected_programs, noti_id, target_term):
        try:
            for program_id in affected_programs:
                existing_notification = self.db.query(Notifications).filter(
                    Notifications.program_id == program_id,
                    Notifications.noti_id == noti_id,
                    Notifications.target_term == target_term
                ).first()

                if existing_notification:
                    print(f"Found notification group in database for program_id={program_id}: group_id={existing_notification.notification_group_id}")
                    return existing_notification.notification_group_id

            print(f"No notification group found for noti_id={noti_id}, target_term={target_term}")
            return None
        except Exception as e:
            print(f"Error finding notification group ID: {str(e)}")
            return None

    def create_prog_notification(self, program_id, source_program_id, message, noti_type, noti_id, notification_group_id, target_term):
        try:
            notification = Notifications(
                program_id=program_id,
                source_program_id=source_program_id,
                message=message,
                noti_type=noti_type,
                noti_id=noti_id,
                notification_group_id=notification_group_id,
                target_term=target_term,
                # created_at=datetime.now(),
            )
            print(f"Creating notification for program_id={program_id}, noti_id={noti_id}, group_id={notification_group_id}")
            self.db.add(notification)
            self.send_send_email(program_id,source_program_id,message)
            self.db.commit()
            return notification.serialize()
        except Exception as e:
            self.db.rollback()
            print(f"Error creating program notification: {str(e)}")
            return None

    def create_prog_notifications(self, source_program_id, term_conflicts):
        try:
            notifications = []

            grouped_conflicts = {}
            for conflict in term_conflicts:
                noti_id = conflict['noti_id']
                target_term = conflict['target_term']
                if noti_id not in grouped_conflicts:
                    grouped_conflicts[noti_id] = {
                        "message": conflict['message'],
                        "target_term": target_term,
                        "affected_programs": []
                    }
                grouped_conflicts[noti_id]["affected_programs"].append(conflict['affected_program_id'])


            for noti_id, group_data in grouped_conflicts.items():
                message = group_data["message"]
                target_term = group_data["target_term"]
                affected_programs = group_data["affected_programs"]

                notification_group_id = self.find_notification_group_id(affected_programs, noti_id, target_term)
                if notification_group_id:
                    print(f"Notification group already exists for noti_id={noti_id}, target_term={target_term}.")

                    source_notification = self.db.query(Notifications).filter(
                        Notifications.program_id == source_program_id,
                        Notifications.noti_id == noti_id,
                        Notifications.target_term == target_term,
                        Notifications.notification_group_id == notification_group_id
                    ).first()

                    if source_notification:
                        source_notification.is_solved = True
                        self.db.commit()
                        print(f"Notification for source_program_id={source_program_id}, noti_id={noti_id} marked as solved.")
                    else:
                        print(f"No notification for source_program_id={source_program_id}, noti_id={noti_id}. Nothing to solve.")
                    continue

                notification_group_id = self.generate_notification_group_id()
                print(f"Created new notification group: group_id={notification_group_id}")

                for program_id in affected_programs:
                    if program_id == source_program_id:
                        continue

                    existing_notification = self.db.query(Notifications).filter(
                        Notifications.program_id == program_id,
                        Notifications.noti_id == noti_id,
                        Notifications.target_term == target_term,
                        Notifications.notification_group_id == notification_group_id
                    ).first()

                    if existing_notification:
                        print(f"Notification already exists for program_id={program_id}, noti_id={noti_id}, target_term={target_term}")
                        continue

                    notification = self.create_prog_notification(
                        program_id=program_id,
                        source_program_id=source_program_id,
                        message=message,
                        noti_type="course",
                        noti_id=noti_id,
                        notification_group_id=notification_group_id,
                        target_term=target_term
                    )
                    if notification:
                        notifications.append(notification)

            return notifications
        except Exception as e:
            print(f"Error creating program notifications: {str(e)}")
            return None



    def get_prog_notifications(self, program_id):
        try:
            notifications = self.db.query(Notifications).filter_by(program_id=program_id).order_by(Notifications.created_at.desc()).all()
            return [notification.serialize() for notification in notifications]
        except Exception as e:
            print(f"Error fetching program notifications: {str(e)}")
            return []


    def delete_notification(self, notification_id):
        try:
            notification = self.db.query(Notifications).get(notification_id)
            if not notification:
                return False
            
            self.db.delete(notification)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error deleting notification: {str(e)}")
            return False

        
    # get all notifications for a studyprogram
    def get_notifications_by_program(self, program_id):
        
        query = self.db.query(Notifications).filter(Notifications.program_id == program_id)

        notifications = query.order_by(Notifications.created_at.desc()).all()
        return [notification.serialize() for notification in notifications]


    def get_notification_by_id(self, notification_id):
        try:
            notification = self.db.query(Notifications).get(notification_id)
            if not notification:
                return None
            
            return notification.serialize()
        except Exception as e:
            print(f"Error fetching notification by ID: {str(e)}")
            return None

    def get_notifications_by_user(self, user_id):
        try:
            notifications = self.db.query(Notifications).filter_by(recipient_id=user_id).order_by(Notifications.created_at.desc()).all()
            return [notification.serialize() for notification in notifications]
        except Exception as e:
            print(f"Error fetching user notifications: {str(e)}")
            return []

    def get_notifications_by_sender(self, sender_id):
        try:
            notifications = self.db.query(Notifications).filter_by(sender_id=sender_id).order_by(Notifications.created_at.desc()).all()
            return [notification.serialize() for notification in notifications]
        except Exception as e:
            print(f"Error fetching sender notifications: {str(e)}")
            return []

    def get_notifications_by_group(self, notification_group_id):
        try:
            notifications = Notifications.query.filter_by(notification_group_id=notification_group_id).all()
            return [notification.serialize() for notification in notifications]
        except Exception as e:
            print(f"Error fetching group notifications: {str(e)}")
            return []

    def delete_all_notifications(self):
        try:
            self.db.query(Notifications).delete()
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error deleting all notifications: {str(e)}")
            return False
    

    def send_send_email(self, recipient_program_id, sender_program_id, message):
        try:
            program_service = self.studyprogram_service
            recipient_program = program_service.get_studyprogram_by_id(recipient_program_id)
            sender_program = program_service.get_studyprogram_by_id(sender_program_id)
            if not recipient_program.program_ansvarlig:
                return("No one in charge of this program")
            msg = Message(
                subject="Notifikasjon fra studieplanrevisjon",
                recipients=["truls244@gmail.com"],
                body=f"{sender_program.name} gjøre denne endringen: {message} Mottaker er: {recipient_program.program_ansvarlig.email}"
                )
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return []