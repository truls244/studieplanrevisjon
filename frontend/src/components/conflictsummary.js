import React, { useState } from 'react';
import axios from 'axios';
import '../styles/notifications.css';
const ConflictSummary = ({
    termConflicts,
    affectedPrograms,
    fetchedNotifications,
    isOpen,
    onClose,
    onConfirm,
    onCancel,
    sourceProgram,

}) => {

    const [notificationGroupId, setNotificationGroupId] = useState(null);
    if (!isOpen) return null;

    const programConflicts = {};
    termConflicts.forEach(termConflict => {
        const programId = termConflict.affectedProgram.id;
        if (!programConflicts[programId]) {
            programConflicts[programId] = {
                program: termConflict.affectedProgram,
                courses: []
            };
        }

        programConflicts[programId].courses.push({
            code: termConflict.course.courseCode,
            name: termConflict.course.name,
            current_term: termConflict.current_term,
            new_term: termConflict.new_term,
            semester_number: termConflict.semester_number,
        });
    });


    const handleConfirmConflicts = async () => {
        try {
            if (notificationGroupId) {
                console.log('Notifications for this group have already been sent.');
                return;
            }

            const payload = {
                source_program_id: sourceProgram.id,
                term_conflicts: termConflicts.map(tc => ({
                    noti_id: tc.course.id,
                    message: tc.message,
                    affected_program_id: tc.affectedProgram.id,
                    target_term: tc.new_term,
                })),
                fetched_notifications: fetchedNotifications,
            };

            console.log('Payload for notification:', payload);
            const response = await axios.post('/backend/notifications/create-noti/prog', payload);
            console.log('Notification sent successfully:', response.data);
            setNotificationGroupId(response.data.notification_group_id);


            onConfirm();

        } catch (error) {
            console.error('Error sending notification:', error);
        }
    };

    return (
        <div className="notification-overlay" style={{ zIndex: 1000 }}>
            <div className="notification-content">
                <div className="notification-header">
                    <h3>Conflict Summary</h3>
                    <button className="close-button" onClick={onClose}>×</button>
                </div>

                <div className="notification-body">
                    <p>The following study programs will be affected by term conflicts:</p>

                    {Object.values(programConflicts).map((item, idx) => (
                        <div key={idx} className="conflict-program">
                            <h4>{item.program.name}</h4>
                            <ul>
                                {item.courses.map((course, courseIdx) => (
                                    <li key={courseIdx}>
                                        <strong>{course.code}</strong> - {course.name}
                                        <div className="conflict-detail">
                                            Currently in <strong>{course.current_term}</strong> term,
                                            moved to <strong>{course.new_term}</strong> term.
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}

                    <p className="warning-text">
                        Notifications will be sent to all affected programs.
                        Do you want to continue?
                    </p>
                </div>

                <div className="notification-actions">
                    <button
                        className="cancel-button"
                        onClick={onCancel}
                    >
                        Cancel and Review
                    </button>
                    <button
                        className="confirm-button"
                        onClick={handleConfirmConflicts}
                    >
                        Confirm and Save
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConflictSummary;