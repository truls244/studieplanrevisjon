import React, { useMemo, useEffect, useState } from "react";
import { Droppable } from "@hello-pangea/dnd";
import DraggableCourse from "./DraggableCourse";
import "../styles/dragdrop.css";

const SearchBar = ({ searchTerm, setSearchTerm }) => (
  <div className="search-bar">
    <input
      id="search-input"
      type="text"
      placeholder="Search course..."
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
    />
  </div>
);



/*

Denne kan importeras når man trenger search bar med dropdown meny. (KUN DRAG AND DROP FUNKE MED DENNE IMPORTEN)

*/

const SearchCourses = ({
  searchTerm,
  setSearchTerm,
  maxResults = 10,
  allCourses,
  semesters,
  onResultsChange = () => { },
}) => {
  const [isDragging] = useState(false);

  const filteredCourses = useMemo(() => {
    if (searchTerm.length < 2) return [];

    const isInSemester = (courseId) =>
      Object.values(semesters).some((semester) =>
        (semester.semester_courses || []).some((c) => c.id === courseId)
      );

    const results = allCourses.filter((course) =>
      course.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !isInSemester(course.id) || course.courseCode.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !isInSemester(course.id)
    );

    return results.slice(0, maxResults);
  }, [searchTerm, allCourses, semesters, maxResults]);

  useEffect(() => {
    onResultsChange(filteredCourses);
  }, [filteredCourses, onResultsChange]);


  return (
    <div className="search-courses-container">
      <h3>Search for courses</h3>
      <SearchBar
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
      />

      <div className={`search-results-container ${isDragging ? 'dragging' : ''}`}>
        <h3>Search Results ({filteredCourses.length})</h3>
        <Droppable
          droppableId="search-results" //mode="virtual"
          isDropDisabled={true}
          direction="vertical"
        >
          {(provided) => (
            <div
              className="search-results-list"
              ref={provided.innerRef}
              {...provided.droppableProps}


            > {/*max10 søk*/}
              {filteredCourses.map((course, index) => (
                <DraggableCourse
                  key={course.id}
                  course={course}
                  index={index}
                  readOnly={false}
                />
              ))}

              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </div>

      {filteredCourses.length === 0 && (
        <div className="no-results">No Courses found</div>
      )}
    </div>
  );
};

export default SearchCourses;