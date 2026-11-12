import { get_session_info, get_payload, delete_payload, post_payload } from "./utils.js";

const session_info = get_session_info();

type SubjectInfo = 
{
    subject_code: string,
    subject_name: string,
    units: number,
};

type SubjectSchema  = SubjectInfo & {
    activity_split: number,
    major_exam_split: number,
    final_output_split: number
};


async function render_subject_schemas()
{
    const user_subjects_response = await fetch(`/api/v1/users/${session_info.user_id}/subjects`, get_payload());

    if (user_subjects_response.status == 401)
    {
        window.location.replace("/login");
    }
    const user_subjects: SubjectSchema[] = await user_subjects_response.json();

    const container = document.getElementById("schema_table") as HTMLDivElement;
    container.replaceChildren();
    if (user_subjects.length === 0)
    {
        const empty_div = document.createElement("div");
        empty_div.className = "empty-state";
        empty_div.textContent = "No schema saved yet."
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
        <th>Subject</th>
        <th>Act</th>
        <th>Major</th>
        <th>Final</th>
        <th>Action</th>
    </tr>
    `;

    const body = document.createElement("tbody");
    user_subjects.forEach((schema: SubjectSchema) => 
    {
       const row = document.createElement('tr');
       const code_col = document.createElement('td');
       const name_col = document.createElement('td');
       const act_col = document.createElement('td');
       const major_col = document.createElement('td');
       const final_col = document.createElement('td');
       const action_col = document.createElement('td');
       
       code_col.textContent = schema.subject_code;
       name_col.textContent = schema.subject_name;
       act_col.textContent = `${Number(schema.activity_split).toFixed(2)}%`;
       major_col.textContent = `${Number(schema.major_exam_split).toFixed(2)}%`;
       final_col.textContent = `${Number(schema.final_output_split).toFixed(2)}%`;

       const delete_btn = document.createElement("button");
       delete_btn.className = "btn btn-danger";
       delete_btn.textContent = "Delete";
       delete_btn.addEventListener("click", async (event) =>
        {
            const confirmation = window.confirm("Delete this subject schema?");
            if (!confirmation)
            {
                return;
            }
            const delete_response = await fetch(`/api/v1/users/${session_info.user_id}/subjects/${schema.subject_code}`, delete_payload());
            render_subject_schemas();
        });

       const edit_btn = document.createElement("button");
       edit_btn.className = "btn";
       edit_btn.textContent = "Edit";
       edit_btn.addEventListener("click", async (event) =>
        {
            sessionStorage.setItem("subject_to_edit", schema.subject_code); 
            window.location.replace("/edit");
        });
        
        
        const button_container = document.createElement("div");
        button_container.style.gap = "4px";
        button_container.style.display = "flex";

        button_container.appendChild(edit_btn);
        button_container.appendChild(delete_btn);
        action_col.appendChild(button_container);

        row.appendChild(code_col);
        row.appendChild(name_col);
        row.appendChild(act_col);
        row.appendChild(major_col);
        row.appendChild(final_col);
        row.appendChild(action_col);

        body.appendChild(row);
    });

    table.appendChild(header);
    table.appendChild(body);
    table_wrapper.appendChild(table);
    container.appendChild(table_wrapper);
}

async function render_global_subjects_list()
{
    const global_subjects_responese = await fetch(`/api/v1/subjects`, get_payload());

    if (global_subjects_responese.status == 401)
    {
        window.location.replace("/login");
    }
    const global_subjects: SubjectInfo[] = await global_subjects_responese.json();

    const selection = document.getElementById("subject_code") as HTMLSelectElement;

    global_subjects.forEach((subject: SubjectInfo) => 
    {
        const subject_option = document.createElement("option");
        subject_option.value = subject.subject_code;
        subject_option.textContent = subject.subject_code;
        selection.appendChild(subject_option);
    });
}

const add_schema_form = document.getElementById("add_subject") as HTMLFormElement;
add_schema_form.addEventListener('submit', async (event) =>
{
    event.preventDefault();
    const add_form_data = new FormData(add_schema_form);
    const add_schema_payload = 
    {
        subject_code: add_form_data.get('subject_code'),
        activity_split: add_form_data.get('activity_split'),
        major_exam_split: add_form_data.get('major_exam_split'),
        final_output_split: add_form_data.get('final_output_split')
    };

    const response = await fetch(`/api/v1/users/${session_info.user_id}/subjects`, post_payload(add_schema_payload));

    const result_div = document.getElementById("result_div") as HTMLDivElement;
    
    if (response.ok)
    {
        result_div.className = "message success"
        result_div.textContent = "Saved Successfully"
        render_subject_schemas();
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



render_global_subjects_list();
render_subject_schemas();