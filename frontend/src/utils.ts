export type SessionInfo = 
{
    is_logged_in: Boolean,
    user_id: Number | null,
    username: string | null,
    session_token: string | null,
    token_type: string| null,  
};

export function get_session_info(): SessionInfo
{
    const raw_login = localStorage.getItem("session_info");
    const login_info: SessionInfo = raw_login ? JSON.parse(raw_login) : {is_logged_in : false, session_token: null, user_id: null, username: null, token_type: null};

    return login_info;
}


export function get_payload()
{
    const session = get_session_info();
    return {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${session.session_token}`,
            "Content-Type": "application/json"
        }
    };
}


export function post_payload(object: any)
{
    const session = get_session_info();
    if (!session.is_logged_in)
    {
        return {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(object)
        };
    }

    return {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${session.session_token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(object)
    };
}