import {type SessionInfo, is_logged_in} from "./login.js"

function redirect_default()
{
    let login_info: SessionInfo = is_logged_in(); 

    if (login_info.is_logged_in)
    {
        window.location.replace("/dashboard");
    }
    else window.location.replace("/login");
}



redirect_default();