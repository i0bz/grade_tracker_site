import { get_session_info, get_payload, delete_payload, post_payload } from "./utils.js";

const session_info = get_session_info();
const subject_code = sessionStorage.getItem("subject_to_edit");

if (!subject_code)
{
    window.location.replace("/dashboard");
}



type SubjectInfo = {
    subject_code: string,
    subject_name: string
};

type ActivityInfo = {
    id: number,
    subject_code: string,
    activity_name: string,
    activity_type: string,
    points: number,
    max_points: number
};

type SubjectSchema  = SubjectInfo & {
    activity_split: number,
    major_exam_split: number,
    final_output_split: number
};

async function render_default_values()
{
    const response = await fetch(`/api/v1/users/${session_info.user_id}/subjects/${subject_code}`, get_payload());
    const full_subj_info: SubjectSchema = await response.json();

    if (!response.ok)
    {
        window.location.replace("/");
    }

    const act_split_input = document.getElementById("activity_split") as HTMLInputElement;
    const maj_exam_split_input = document.getElementById("major_exam_split") as HTMLInputElement;
    const final_out_split = document.getElementById("final_output_split") as HTMLInputElement;


    act_split_input.value = `${Number(full_subj_info.activity_split)}`;
    maj_exam_split_input.value = `${Number(full_subj_info.major_exam_split)}`;
    final_out_split.value = `${Number(full_subj_info.final_output_split)}`;
}




async function render_activities()
{
        const activities_response = await fetch(`/api/v1/users/${session_info.user_id}/subjects/${subject_code}/activities`, get_payload());
    
        if (activities_response.status == 401)
        {
            window.location.replace("/login");
        }
        const activities: ActivityInfo[] = await activities_response.json();
    
        const container = document.getElementById("activities_table") as HTMLDivElement;
        container.replaceChildren();
        if (activities.length === 0)
        {
            const empty_div = document.createElement("div");
            empty_div.className = "empty-state";
            empty_div.textContent = "No activities yet."
            container.appendChild(empty_div);
            return;
        }
    
        const table_wrapper = document.createElement("div");
        table_wrapper.className = "table-wrap";
        const table = document.createElement("table");
        const header = document.createElement("thead");
        header.innerHTML = `
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Points</th>
            <th>Max Points</th>
            <th>Action</th>
        </tr>
        `;
    
        const body = document.createElement("tbody");
        activities.forEach((activity: ActivityInfo) => 
        {
            const row = document.createElement('tr');
            const name_col = document.createElement('td');
            const type_col = document.createElement('td');
            const points_col = document.createElement('td');
            const max_points_col = document.createElement('td');
            const action_col = document.createElement('td');
           
            name_col.textContent = activity.activity_name;
            type_col.textContent = activity.activity_type;
            points_col.textContent = `${activity.points}`;
            max_points_col.textContent = `${activity.max_points}`;
            
            const delete_btn = document.createElement("button");
            delete_btn.className = "btn btn-danger";
            delete_btn.textContent = "Delete"
            delete_btn.addEventListener("click", async (event) =>
            {
                const confirmation = window.confirm("Delete this activity?");
                if (!confirmation)
                {
                    return;
                }
                const delete_response = await fetch(`/api/v1/users/${session_info.user_id}/subjects/${subject_code}/activities/${activity.id}`, delete_payload());
                render_activities();
            });
    
            action_col.appendChild(delete_btn);
    
            row.appendChild(name_col);
            row.appendChild(type_col);
            row.appendChild(points_col);
            row.appendChild(max_points_col);
            row.appendChild(action_col);
    
            body.appendChild(row);
        });
    
        table.appendChild(header);
        table.appendChild(body);
        table_wrapper.appendChild(table);
        container.appendChild(table_wrapper);
}

const activity_form = document.getElementById("add_activity") as HTMLFormElement;
activity_form.addEventListener('submit', async (event) =>
{
    event.preventDefault();
    const form_data = new FormData(activity_form);

    const activity_payload = {
        activity_name: form_data.get("activity_name"),
        activity_type: form_data.get("activity_type"),
        points: form_data.get("points"),
        max_points: form_data.get("max_points")
    };

    console.log(form_data.get("activity_type"));
    const response = await fetch(`/api/v1/users/${session_info.user_id}/subjects/${subject_code}/activities`, post_payload(activity_payload));
    const result_div = document.getElementById("activity_result_div") as HTMLDivElement;
    
    if (response.ok)
    {
        result_div.className = "message success"
        result_div.textContent = "Saved Successfully"
        render_activities();
        return
    }

    const error = await response.json();

    switch (response.status)
    {
        case 500:
            result_div.className = "message error";
            result_div.textContent = "Server Shat Itself";
            break;   
        
        case 422:
            result_div.className = "message error";
            result_div.textContent = error.detail[0].msg;
            break;
        case 401:
            window.location.replace("/login");
            break;
    }

});



const save_schema_form = document.getElementById("edit_subject") as HTMLFormElement;
save_schema_form.addEventListener('submit', async (event) =>
{
    event.preventDefault();
    const add_form_data = new FormData(save_schema_form);
    const add_schema_payload = 
    {
        activity_split: add_form_data.get('activity_split'),
        major_exam_split: add_form_data.get('major_exam_split'),
        final_output_split: add_form_data.get('final_output_split')
    };

    const response = await fetch(`/api/v1/users/${session_info.user_id}/subjects/${subject_code}`, post_payload(add_schema_payload));

    const result_div = document.getElementById("subject_result_div") as HTMLDivElement;
    
    if (response.ok)
    {
        result_div.className = "message success";
        result_div.textContent = "Saved Successfully";
        render_default_values();
        return
    }
    
    const error = await response.json();
    
    switch (response.status)
    {
        case 409:
            result_div.className = "message error";
            result_div.textContent = "Schema Already exists";
            break;
        case 500:
            result_div.className = "message error";
            result_div.textContent = "Server Shat Itself";
            break;   
        
        case 422:
            result_div.className = "message error";
            result_div.textContent = error.detail[0].msg;
            break;
        case 401:
            window.location.replace("/login");
            break;
    }
});





render_activities();
render_default_values();