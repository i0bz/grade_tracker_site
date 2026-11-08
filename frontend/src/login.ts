import { type SessionInfo, post_payload} from "./utils.js";


const login_form = document.getElementById("login_form") as HTMLFormElement;
const error_div = document.getElementById("error-div") as HTMLDivElement;

login_form.addEventListener('submit', async (event: SubmitEvent) => 
{
    event.preventDefault();

    const login_data = new FormData(login_form);
    const login_payload = {
        username: String(login_data.get("username")),
        password: String(login_data.get("password"))
    };
    
    try 
    {
        const response = await fetch('/api/v1/auth/login', post_payload(login_payload));

        if (response.ok)
        {
            const response_data = await response.json();
            const session_info: SessionInfo = {
                is_logged_in: true,
                user_id: response_data.user_id,
                session_token: response_data.session_token,
                token_type: response_data.token_type,
                username: login_payload.username
            };

            localStorage.setItem("session_info", JSON.stringify(session_info));
            window.location.replace("/dashboard");
            return;
        }

        const error_data = await response.json();
        switch(response.status)
        {
            case 401:
                error_div.textContent = error_data.detail;
                break;
            case 500:
                error_div.textContent = "Server shat itself.";
                break;
        }


    }
    catch (error: unknown)
    {
        error_div.textContent = "Something shat itself.";        
    }
});




