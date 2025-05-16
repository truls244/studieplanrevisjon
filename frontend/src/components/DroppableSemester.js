import React from 'react';
import { Droppable } from '@hello-pangea/dnd';
import DraggableCourse from './DraggableCourse';
import "../styles/dragdrop.css";



const DroppableSemester = ({
  semesterNumber,
  semesterId,
  courses,
  onRemove,
  onAdministrerValgemner,
  readOnly
}) => {

  return (
    <Droppable droppableId={`semester-${semesterNumber}`} isDropDisabled={readOnly}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.droppableProps}
          className={`semester-box ${snapshot.isDraggingOver ? 'drag-over' : ''}`}
          style={{
            minHeight: snapshot.isDraggingOver ? '350px' : '200px',
            transition: 'all 0.2s ease',
            background: snapshot.isDraggingOver ? '#e6f7ff' : 'white',
            border: snapshot.isDraggingOver ? '2px dashed #1890ff' : '1px solid #eee',
            boxSizing: 'border-box',
          }}
        >


          {courses.map((course, index) => (
            <DraggableCourse
              key={course.id}
              course={course}
              index={index}
              readOnly={readOnly}
              onRemove={onRemove}
              onAdministrerValgemner={onAdministrerValgemner}
              semesterNumber={semesterNumber}
              semesterId={semesterId}
            />
          ))}
          {provided.placeholder}

          {/* drop indikator (når tom) */}
          {courses.length === 0 && !snapshot.isDraggingOver && (
            <div className="empty-semester">
              {readOnly ? 'No courses in this semester' : 'Drag courses here'}
            </div>
          )}

          {/* drop indikator */}
          {snapshot.isDraggingOver && courses.length === 0 && (
            <div className="drop-indicator">
              <p>Release to add course</p>
            </div>
          )}
        </div>
      )}
    </Droppable>
  );
};

export default DroppableSemester;