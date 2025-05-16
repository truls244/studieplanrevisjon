import React from 'react';
import { Draggable } from '@hello-pangea/dnd';
import "../styles/dragdrop.css";

const DraggableCourse = ({
  course,
  index,
  onRemove,
  isDragDisabled = false,
  readOnly,
  onAdministrerValgemner,
  semesterNumber = null,
  semesterId = null,
}) => {

  // valgemne er ikke draggable
  const isValgemne = course.courseCode === "VALGEMNE";
  const courseDragDisabled = readOnly || isValgemne || isDragDisabled;

  return (
    <Draggable draggableId={`course-${course.id}`} index={index} isDragDisabled={courseDragDisabled}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={`course-item ${snapshot.isDragging ? 'dragging' : ''} ${isValgemne ? 'valgemne-item' : ''} ${courseDragDisabled ? "disabled" : ""}`}
          style={{
            ...provided.draggableProps.style,
            background: snapshot.isDragging ? '#e6f7ff' : 'white',
            border: snapshot.isDragging ? '2px dashed #1890ff' : '1px solid #eee',
            boxSizing: 'border-box',
            outline: snapshot.isDragging ? '2px solid purple' : 'none',
          }}
        >
          <div className="course-details">
            <div className="course-name">{course.name}</div>
            <div className="course-info">
              <span className="course-code">{course.courseCode}</span>
              {course.credits && <span className="course-credits">{course.credits} sp</span>}
              {course.semester && <span className="course-semester">{course.semester}</span>}
            </div>
          </div>

          {!readOnly && semesterNumber && !isValgemne && (

            <button
              onClick={() => onRemove(course.id)}

              className="remove-button"
            >
              Remove
            </button>
          )}

          {isValgemne && semesterNumber && (
            <button
              onClick={() => onAdministrerValgemner()}
              className="manage-valgemner-button"
            >
              {readOnly ? "Vis valgemner" : "Administrer valgemner"}
            </button>
          )}
        </div>
      )}
    </Draggable>
  );
};

export default DraggableCourse;