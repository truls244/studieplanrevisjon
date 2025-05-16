import React, { useState, useEffect, useMemo } from "react";
import { SearchBar, filterCourses } from "../utils/helpers.js";
import { getElectiveGroups } from "../utils/categoryHelpers.js";
import "../styles/valgemne.css";

const ValgemneOverlay = ({
  isOpen,
  closeOverlay,
  semesterId,
  semesterNumber,
  valgemne,
  setValgemne,
  setFormattedValgemner,
  allCourses,
  readOnly = false,
}) => {
  const [categories, setCategories] = useState([]);
  const [currentValgemne, setCurrentValgemne] = useState({});
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [selectedGroup, setSelectedGroup] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    if (isOpen && !readOnly && categories.length === 0) {
      fetchCategories();
    }
  }, [isOpen, readOnly, categories]);


  useEffect(() => {
    if (isOpen && valgemne && valgemne[semesterNumber]) {
      setCurrentValgemne(valgemne[semesterNumber]);
      console.log("Current Valgemne:", valgemne[semesterNumber]);
      console.log("Valgemne for Semester in Overlay:", semesterNumber, valgemne[semesterNumber]);
    }
  }, [valgemne, semesterNumber, isOpen]);

  useEffect(() => {
    console.log("Overlay opened for semester:", semesterId);
  }, [semesterId, semesterNumber]);

  const fetchCategories = async () => {
    try {
      const categories = await getElectiveGroups();
      console.log("Fetched Categories:", categories);
      setCategories(categories || []);
    } catch (error) {
      console.error("Failed to fetch categories:", error);
      setCategories([]);
    }
  };

  const filteredCourses = useMemo(
    () => filterCourses(allCourses, searchTerm),
    [searchTerm, allCourses]
  );



  // Legg te emne i kategori
  const addCourseToGroup = () => {
    if (!selectedCourse || !selectedGroup) {
      alert("Please select a course and a category.");
      return;
    }

    const courseToAdd = { ...selectedCourse, is_elective: true, category_id: selectedGroup };

    setCurrentValgemne((prev) => ({
      ...prev,
      [selectedGroup]: [
        ...(prev[selectedGroup] || []),
        courseToAdd,
      ],
    }));

    setSelectedCourse(null);
    //setSelectedGroup("");
    setSearchTerm("");
  };

  const resolveCategoryName = (categoryId, courses) => {
    const courseCategoryName = courses[0]?.category?.name;

    if (courseCategoryName) {
      return courseCategoryName;
    }

    const category = categories.find((cat) => cat.id === parseInt(categoryId, 10));
    return category?.name || `Unknown Category (${categoryId})`;
  };


  const removeCourseFromGroup = (categoryId, courseId) => {
    setCurrentValgemne((prev) => {
      const updatedCategory = prev[categoryId]?.filter(
        (course) => course.id !== courseId
      );

      // Hvis kategori ble tomt itte fjerning, fjern kategorien.
      if (!updatedCategory || updatedCategory.length === 0) {
        const { [categoryId]: _, ...rest } = prev;
        return rest;
      }

      return {
        ...prev,
        [categoryId]: updatedCategory,
      };
    });
  };

  const formatValgemne = (valgemne) => {
    const formatted = {};
    Object.entries(valgemne).forEach(([categoryId, courses]) => {
      formatted[categoryId] = courses.map((course) => ({
        course_id: course.id,
        is_elective: true,
        category_id: parseInt(categoryId),
      }));
    });
    console.log("Formatted valgemne:", formatted);
    return formatted;
  };

  const handleConfirmValgemner = () => {
    try {
      const formattedValgemner = formatValgemne(currentValgemne);

      setValgemne((prev) => ({
        ...prev,
        [semesterNumber]: currentValgemne,
      }));
      setFormattedValgemner((prev) => ({
        ...prev,
        [semesterNumber]: formattedValgemner,
      }));

      closeOverlay();
    } catch (error) {
      console.error("Error saving electives:", error);
      alert("Failed to save electives. Please try again.");
    }
  };


  if (!isOpen) return null;
  return (
    <div className="overlay">
      <div className="overlay-content">
        <h2>
          {readOnly ? "View Electives" : "Manage Electives"} (Semester{" "}
          {semesterNumber})
        </h2>

        {!readOnly && (
          <>
            <h3>Select Category</h3>
            {categories.length > 0 ? (
              <select
                value={selectedGroup}
                onChange={(e) => setSelectedGroup(e.target.value)}
                className="category-dropdown"
              >
                <option value="" disabled>
                  -- Select a Category --
                </option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            ) : (
              <p>No categories available.</p>
            )}
            {selectedGroup && (
              <>
                <SearchBar
                  searchTerm={searchTerm}
                  setSearchTerm={(term) => {
                    setSearchTerm(term);
                    setSelectedCourse(null);
                  }}
                  filteredCourses={filteredCourses}
                  onCourseSelect={(course) => {
                    setSelectedCourse(course);
                    setSearchTerm(`${course.name} (${course.courseCode})`);
                  }}
                />
                <button onClick={addCourseToGroup} disabled={!selectedCourse}>
                  Add to Category
                </button>
              </>
            )}
          </>
        )}



        {Object.keys(currentValgemne).length > 0 ? (
          Object.entries(currentValgemne).map(([categoryId, courses]) => {
            const categoryName = resolveCategoryName(categoryId, courses);
            const totalCredits = courses.reduce((sum, course) => sum + course.credits, 0);
            return (
              <div key={categoryId} className="category-section">
                <h4>{categoryName}</h4>
                {courses.length > 0 ? (
                  <>
                    <ul>
                      {courses.map((course) => (
                        <li key={course.id} className="valgemne">
                          {course.name} ({course.courseCode}) - {course.credits} credits
                          {!readOnly && (
                            <button
                              onClick={() =>
                                removeCourseFromGroup(categoryId, course.id)
                              }
                            >
                              Remove
                            </button>
                          )}
                        </li>
                      ))}
                    </ul>
                    <p className="total-credits">Total Credits: {totalCredits}</p>
                  </>
                ) : (
                  <p>No courses in this category.</p>
                )}
              </div>
            );
          })
        ) : (
          <p>No electives added for this semester.</p>
        )}

        {!readOnly && (
          <button onClick={handleConfirmValgemner}>Confirm Changes</button>
        )}
        <button onClick={closeOverlay}>Close</button>
      </div>
    </div>
  );
};

export default ValgemneOverlay;