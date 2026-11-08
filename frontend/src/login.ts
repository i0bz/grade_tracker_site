
export type SessionInfo = 
{
    "is_logged_in": Boolean,
    "user_id": Number | null,
    "session_token": string | null    
};

export function is_logged_in(): SessionInfo
{
    let raw_login = localStorage.getItem("session_info");
    let login_info: SessionInfo = raw_login ? JSON.parse(raw_login) : {"is_logged_in" : false, "session_token": null, "user_id": null};

    return login_info;
}

