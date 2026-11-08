import { post_payload } from "./utils.js";

const register_form = document.getElementById("register_form") as HTMLFormElement;
const error_div = document.getElementById("error_div") as HTMLDivElement;

register_form?.addEventListener('submit', async (event: SubmitEvent) => 
{
    event.preventDefault();

    const register_data = new FormData(register_form);
    const register_payload = {
        username: register_data.get("username"),
        password: register_data.get("password")
    };

    try
    {
        const response = await fetch('/api/v1/auth/register', post_payload(register_payload));

        if (response.ok)
        {
            window.location.replace("/login");
            return;
        }

        const error_data = await response.json();

        switch(response.status)
        {
            case 401:
                error_div.textContent = error_data.detail;
            case 500:
                error_div.textContent = "Server shat itself";
        }
    }
    catch (e: unknown)
    {
        error_div.textContent = "Something shat itself";
    }
});