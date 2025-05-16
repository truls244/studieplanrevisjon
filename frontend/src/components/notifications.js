import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import '../styles/notifications.css';

const Notifications = ({ programId, setNotificationsRef }) => {
    const [notifications, setNotifications] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [unreadCount] = useState(0);
    const overlayRef = useRef(null);

    useEffect(() => {
        const fetchNotifications = async () => {
            if (!programId) return;
            try {
                const response = await axios.get(`/backend/notifications/?program_id=${programId}`);
                console.log('Fetched notifications:', response.data);
                setNotifications(response.data);
                if (setNotificationsRef) {
                    setNotificationsRef(response.data);
                }
            } catch (error) {
                console.error('Failed to fetch notifications:', error);
            }
        };

        fetchNotifications();
    }, [programId, setNotificationsRef]);

    const toggleNotifications = () => {
        setIsOpen(!isOpen);
    };

    const handleDeleteNotification = async (notificationId) => {
        try {
            const response = await axios.delete(`/backend/notifications/${notificationId}/delete`);
            console.log('Notification deleted:', response.data);

            setNotifications((prevNotifications) =>
                prevNotifications.filter((notification) => notification.id !== notificationId)
            );
        } catch (error) {
            console.error('Failed to delete notification:', error);
        }
    };


    return (
        <div className="notification-container">
            {/* Notification Badge/Button */}
            <button
                className="notification-badge"
                onClick={toggleNotifications}
                aria-label="Notifications"
            >
                <span className="badge-icon">🔔</span>
                {unreadCount > 0 && (
                    <span className="badge-count">{unreadCount}</span>
                )}
            </button>

            {/* Notification Overlay */}
            {isOpen && (
                <div className="notification-overlay" ref={overlayRef}>
                    <div className="notification-header">
                        <h3>Notifications</h3>
                        <button
                            className="close-button"
                            onClick={() => setIsOpen(false)}
                        >
                            ✕
                        </button>
                    </div>

                    <div className="notification-list">
                        {notifications.length === 0 ? (
                            <div className="no-notifications">
                                <p>No notifications</p>
                            </div>
                        ) : (
                            notifications.map((notification, index) => (
                                <div
                                    key={notification.id || index}
                                    className="notification-item"
                                >
                                    <div className="notification-content">
                                        <p>
                                            <strong>Message:</strong> {notification.message}
                                        </p>
                                        <div className="notification-meta">
                                            {new Date(notification.created_at).toLocaleString()}
                                        </div>
                                    </div>
                                    {notification.is_solved && (
                                        <button
                                            className="solved-button"
                                            onClick={() => handleDeleteNotification(notification.id)}
                                        >
                                            Delete
                                        </button>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Notifications;