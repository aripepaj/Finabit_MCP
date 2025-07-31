def login_form_html(auth_request_id, error_message=None):
    error_block = ""
    if error_message:
        error_block = f'<div class="error">{error_message}</div>'
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Finabit MCP Authorization</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            max-width: 500px; margin: 100px auto; padding: 20px; background: #f8fafc;
        }}
        .container {{
            background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .finabit-logo {{ margin: 0 auto 10px; width: 72px; height: 72px; }}
        h2 {{ color: #1f2937; margin: 10px 0; }}
        label {{ display: block; margin: 15px 0 5px; font-weight: 500; }}
        input {{ width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; 
                font-size: 16px; box-sizing: border-box; }}
        input:focus {{ outline: none; border-color: #2563eb; }}
        button {{ background: #2563eb; color: white; padding: 12px 24px; border: none; 
                border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 20px; }}
        button:hover {{ background: #1d4ed8; }}
        .error {{ background: #fee2e2; color: #dc2626; padding: 10px; border-radius: 6px; margin: 10px 0; }}
        .testing-hint {{ margin-top: 15px; padding: 10px; background: #f0f9ff; border-radius: 6px; font-size: 14px; color: #0369a1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="/static/icon.ico" class="finabit-logo" alt="Finabit Logo">
            <h2>Sign in to Finabit</h2>
        </div>
        <form method="post" action="/authorize">
            <input type="hidden" name="auth_request_id" value="{auth_request_id}">
            {error_block}
            <label>Username:</label>
            <input name="username" required autocomplete="username" placeholder="test">
            <label>Password:</label>
            <input type="password" name="password" required autocomplete="current-password" placeholder="test">
            <label>Key:</label>
            <input name="install_key" required maxlength="28" placeholder="Installation key">
            <button type="submit">Authorize</button>
            <div class="testing-hint">
                <strong>💡 For testing:</strong> Use username "test" and password "test".<br>
                You must also enter your Installation Key (ask your admin).
            </div>
        </form>
    </div>
</body>
</html>
"""
