import { get_session_info, get_payload, delete_payload, post_payload } from "./utils.js";

const session_info = get_session_info();

type SubjectInfo = {
    subject_code: string,
    subject_name: string
};

async function render_user_subject_selection()
{
    const user_subjects_response = await fetch(`/api/v1/users/${session_info.user_id}/subjects`, get_payload());
    const user_subjects: SubjectInfo[] = await user_subjects_response.json();

    if (user_subjects_response.status == 401)
    {
        window.location.replace("/login");
    }

    const selection = document.getElementById("subject_code") as HTMLSelectElement;

    user_subjects.forEach((subject: SubjectInfo) => {
        const option = document.createElement("option");
        option.textContent = subject.subject_code;
        option.value = subject.subject_code;

        selection.appendChild(option);
    });
}


type ActivityInfo = {
    id: number,
    subject_code: string,
    activity_name: string,
    activity_type: string,
    points: number,
    max_points: number
};


async function render_activities()
{
        const activities_response = await fetch(`/api/v1/users/${session_info.user_id}/activities`, get_payload());
    
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
            <th>Subject Code</th>
            <th>Name</th>
            <th>Points</th>
            <th>Max Points</th>
        </tr>
        `;
    
        const body = document.createElement("tbody");
        activities.forEach((activity: ActivityInfo) => 
        {
           const row = document.createElement('tr');
           const subject_col = document.createElement('td');
           const name_col = document.createElement('td');
           const points_col = document.createElement('td');
           const max_points_col = document.createElement('td');
           const delete_col = document.createElement('td');
           
           subject_col.textContent = activity.subject_code;
           name_col.textContent = activity.activity_name;
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
                const delete_response = await fetch(`/api/v1/users/${session_info.user_id}/subjects/${activity.subject_code}/activities/${activity.id}`, delete_payload());
                render_activities();
            });
    
            delete_col.appendChild(delete_btn);
    
            row.appendChild(subject_col);
            row.appendChild(name_col);
            row.appendChild(points_col);
            row.appendChild(max_points_col);
            row.appendChild(delete_col);
    
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
    const subject_code = form_data.get("subject_code");
    console.log(form_data.get("activity_type"));
    const response = await fetch(`/api/v1/users/${session_info.user_id}/subjects/${subject_code}/activities`, post_payload(activity_payload));
    const result_div = document.getElementById("result_div") as HTMLDivElement;
    
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





render_activities();
render_user_subject_selection();