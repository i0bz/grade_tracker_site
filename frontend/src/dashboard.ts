import { get_session_info, get_payload } from "./utils.js";

const session_info = get_session_info();
const grades_response = await fetch(`/api/v1/users/${session_info.user_id}/subjects/grades`, get_payload());

if (grades_response.status == 403)
{
    window.location.replace("/login");
}


type GradeInfo =
{
    subject_code: string,
    subject_name: string,
    units: number,
    grade: number
}

const grades_list: GradeInfo[] = await grades_response.json();
let subject_count = 0;

function set_general_overview()
{
    let highest_grade = 5;
    let total_units = 0;
    let total_grade = 0;

    grades_list.forEach(grade_info => {
        subject_count++;
        highest_grade = Math.min(highest_grade, grade_info.grade);
        if (!(grade_info.grade < 1))
        {
            total_units += grade_info.units;
            total_grade += (grade_info.grade * grade_info.units);
        }
    });

    if (total_grade === 0 && total_units === 0) total_units = 1;
    let average = total_grade / total_units;

    if (subject_count == 0)
    {
        highest_grade = 0;
        average = 0;
    }

    const subject_div = document.getElementById("subject_amount") as HTMLDivElement;
    const gwa_div = document.getElementById("gwa") as HTMLDivElement;
    const highest_grade_div = document.getElementById("highest_grade") as HTMLDivElement;

    subject_div.textContent = `${subject_count}`;
    gwa_div.textContent = `${average.toFixed(2)}`;
    highest_grade_div.textContent = `${highest_grade.toFixed(2)}`;
}



function set_subjects_overview()
{
    const container = document.getElementById("subjects_table") as HTMLDivElement;

    if (subject_count == 0)
    {
        const empty_div = document.createElement("div");
        empty_div.className = "empty-state";
        empty_div.textContent = "No subjects yet."
        container.appendChild(empty_div);
        return;
    }

    const table_wrapper = document.createElement("div");
    table_wrapper.className = "table-wrap";
    const table = document.createElement("table");
    const header = document.createElement("thead");
    header.innerHTML = `
    <tr>
        <th>Code</th>
        <th>Name</th>
        <th>Units</th>
        <th>Grade</th>
    </tr>
    `;

    const body = document.createElement("tbody");


    grades_list.forEach(grade_info => 
    {
       const row = document.createElement('tr');
       const code_col = document.createElement('td');
       const name_col = document.createElement('td');
       const units_col = document.createElement('td');
       const grade_col = document.createElement('td');
       
       code_col.textContent = grade_info.subject_code;
       name_col.textContent = grade_info.subject_name;
       units_col.textContent = `${grade_info.units}`;

       grade_col.textContent = `${Number(grade_info.grade).toFixed(2)}`;

        row.appendChild(code_col);
        row.appendChild(name_col);
        row.appendChild(units_col);
        row.appendChild(grade_col);

        body.appendChild(row);
    });

    table.appendChild(header);
    table.appendChild(body);
    table_wrapper.appendChild(table);
    container.appendChild(table_wrapper);
}




set_general_overview();
set_subjects_overview();




