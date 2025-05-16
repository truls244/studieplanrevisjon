
function FilterCourse( {sendToParent} ) {


    const updateFilters = (e) => {
        sendToParent(e)
    }

    return (
        <div>
            <h4>Filtrer Emner</h4>
            <div>
                <h4>Semester</h4>
                <input type="checkbox" name="autumn" value="H" onChange={(e) => updateFilters(e)} ></input>
                <label for="autumn" >Høst</label>
                <input type="checkbox" name="spring" value="V" onChange={(e) => updateFilters(e)} ></input>
                <label for="spring" >Vår</label>
                
            </div>
            <div>
                <h4>Fagområde</h4>
                <input type="checkbox" name="data" value="datascience" ></input>
                <label for="data" >Data</label>
                <input type="checkbox" name="autumn" value="electrical" ></input>
                <label for="electrical" >Elektro</label>
            </div>
            <div>
                <h4>Nivå</h4>
                <input type="checkbox" name="bachelor" value="Bachelor" onChange={(e) => updateFilters(e)} ></input>
                <label for="bachelor" >Bachelor</label>
                <input type="checkbox" name="master" value="Master" onChange={(e) => updateFilters(e)} ></input>
                <label for="master" >Master</label>
            </div>
        </div>
    );
}
export default FilterCourse;