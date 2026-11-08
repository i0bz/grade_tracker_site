import { get_session_info, post_payload } from "./utils.js";

const session = get_session_info()
await fetch(`/api/v1/users/${session.user_id}/logout`,post_payload({}));
localStorage.removeItem("session_info");

window.location.replace("/");