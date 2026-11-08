import {type SessionInfo, get_session_info} from "./utils.js"

function redirect_default()
{
    let login_info: SessionInfo = get_session_info(); 

    if (login_info.is_logged_in)
    {
        window.location.replace("/dashboard");
    }
    else window.location.replace("/login");
}



redirect_default();