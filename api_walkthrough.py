import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Plume API — Interactive Walkthrough

    A standalone notebook demonstrating the core API operations against the Plume cloud.
    Uses **only `httpx`** — no auto-generated clients required.

    ## What's covered

    1. **Full CRUD lifecycle** — create → read → update → verify → delete → confirm deletion
    2. **Known API issues** — server returning wrong status codes / null bodies

    ## Prerequisites

    You need a `Basic` auth header value (base64-encoded `client_id:client_secret`) and a valid `partner_id`.
    The notebook exchanges these for a Bearer JWT via the OAuth2 `client_credentials` grant —
    same flow as `conftest.py`'s `api_token` fixture.
    """)
    return


@app.cell
def _():
    import httpx
    import json
    import uuid

    return httpx, json, uuid


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Configuration

    Enter your Basic auth header when prompted. Credentials are **never stored in the notebook**.
    """)
    return


@app.cell
def _(httpx):
    BASE_URL = 'https://virtserver.swaggerhub.com/plumedesigninc-c7a/plume/next'
    PARTNER_ID = '6971f4934016be004a041191'
    auth_header = 'Basic mock'
    with httpx.Client(base_url=BASE_URL) as _c:
        _resp = _c.post('/v1/auth/token', headers={'Authorization': auth_header}, data={'grant_type': 'client_credentials', 'scope': f'partnerId:{PARTNER_ID} role:partnerIdAdmin'})
    assert _resp.status_code == 200, f'Token acquisition failed: {_resp.status_code} — {_resp.text}'
    token_data = _resp.json()
    TOKEN = token_data['access_token']
    print(f'Using base URL: {BASE_URL}')
    print(f'Partner ID:     {PARTNER_ID}')
    print(f"Token type:     {token_data.get('token_type', '?')}")
    print(f"Expires in:     {token_data.get('expires_in', '?')}s")
    print(f'JWT (first 20): {TOKEN[:20]}...')
    return BASE_URL, PARTNER_ID, TOKEN


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Helper: authenticated client factory

    All subsequent cells use this. Keeps the token and common headers in one place.
    """)
    return


@app.cell
def _(BASE_URL, TOKEN, httpx, json):
    def api_client() -> httpx.Client:
        """Create a pre-configured httpx client with Bearer auth."""
        return httpx.Client(base_url=BASE_URL, headers={'Authorization': f'Bearer {TOKEN}', 'User-Agent': 'plume-api-notebook/0.1'}, timeout=60.0)

    def pp(resp: httpx.Response) -> None:
        """Pretty-print a response for notebook output."""
        print(f'{resp.request.method} {resp.request.url}')
        print(f'Status: {resp.status_code}')
        try:
            body = resp.json()
        except json.JSONDecodeError:
            print(repr(resp.text[:500]) if resp.text else '(empty body)')
        else:
            print(json.dumps(body, indent=2))

    return api_client, pp


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 1. User CRUD Lifecycle

    **Create → Read → Update → Read (verify) → Delete → Read (expect 404)**

    This is the equivalent of `test_user_lifecycle` from `tests/test_users.py`,
    written as plain `httpx` calls so you can step through each operation.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1a. Create user
    """)
    return


@app.cell
def _(PARTNER_ID, api_client, pp, uuid):
    tag = uuid.uuid4().hex[:8]
    new_user = {'name': f'notebook-test-{tag}', 'email': f'notebook-{tag}@test.plume.com', 'partnerId': PARTNER_ID}
    with api_client() as _c:
        _resp = _c.post('/v1/users', json=new_user)
    pp(_resp)
    assert _resp.status_code == 200, f'Create failed: {_resp.text}'
    created = _resp.json()
    USER_ID = created['id']
    print(f'\n>>> Created user {USER_ID}')
    return USER_ID, new_user, tag


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1b. Read back
    """)
    return


@app.cell
def _(USER_ID, api_client, new_user, pp):
    with api_client() as _c:
        _resp = _c.get(f'/v1/users/{USER_ID}')
    pp(_resp)
    assert _resp.status_code == 200
    assert _resp.json()['name'] == new_user['name'], 'Name mismatch!'
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1c. Update user
    """)
    return


@app.cell
def _(USER_ID, api_client, pp, tag):
    updated_name = f'notebook-updated-{tag}'
    with api_client() as _c:
        _resp = _c.patch(f'/v1/users/{USER_ID}', json={'name': updated_name})
    pp(_resp)
    assert _resp.status_code == 200
    assert _resp.json()['name'] == updated_name
    print(f'\n>>> Renamed to: {updated_name}')
    return (updated_name,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1d. Read back (verify update stuck)
    """)
    return


@app.cell
def _(USER_ID, api_client, pp, updated_name):
    with api_client() as _c:
        _resp = _c.get(f'/v1/users/{USER_ID}')
    pp(_resp)
    assert _resp.json()['name'] == updated_name, 'Update did not persist!'
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1e. Delete user
    """)
    return


@app.cell
def _(USER_ID, api_client):
    with api_client() as _c:
        _resp = _c.delete(f'/v1/users/{USER_ID}')
    print(f'DELETE /v1/users/{USER_ID}')
    print(f'Status: {_resp.status_code}')
    assert _resp.status_code == 204, f'Expected 204 No Content, got {_resp.status_code}'
    print('>>> User deleted successfully')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1f. Confirm deletion (expect 404)
    """)
    return


@app.cell
def _(USER_ID, api_client, pp):
    with api_client() as _c:
        _resp = _c.get(f'/v1/users/{USER_ID}')
    pp(_resp)
    assert _resp.status_code == 404, f'Expected 404 after deletion, got {_resp.status_code}'
    print('\n>>> Confirmed: user no longer exists')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 2. Known API Issues

    The following cells demonstrate real bugs we've filed against the backend.
    They serve as examples of how testing exposes specification violations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2a. Empty name → wrong status code (PODE-3000)

    The spec says `name` has `minLength: 1` and validation errors return `422`.

    **Actual behaviour:** server returns **400** with `"Either firstName or name must be included."`
    The field `firstName` is not even in the OpenAPI spec.
    """)
    return


@app.cell
def _(PARTNER_ID, api_client, pp):
    with api_client() as _c:
        _resp = _c.post('/v1/users', json={'name': '', 'email': 'validation-test@test.plume.com', 'partnerId': PARTNER_ID})
    pp(_resp)
    print(f'\n--- Analysis ---')
    print(f'Expected status: 422 (per OpenAPI spec)')
    print(f'Actual status:   {_resp.status_code}')
    if _resp.status_code == 400:
        print('BUG CONFIRMED: server returns 400 instead of 422.')
        print("The error message references 'firstName' which is not in the spec.")
        print('Tracked: https://plumedesign.atlassian.net/browse/PODE-3000')
    elif _resp.status_code == 422:
        print('Bug appears to be FIXED. Update the xfail marker in test_users.py!')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2b. Forbidden characters in accountId → null response body (PODE-3001)

    The spec says `accountId` cannot contain `<` or `>` and violations return `422` with an `Error` object.

    **Actual behaviour:** server returns `422` but with a **`null` body** instead of a JSON error.
    This breaks the generated client (`Error.from_dict(None)` → `TypeError`).
    """)
    return


@app.cell
def _(PARTNER_ID, api_client, pp):
    with api_client() as _c:
        _resp = _c.post('/v1/users', json={'name': 'validation-test', 'email': 'validation-test@test.plume.com', 'partnerId': PARTNER_ID, 'accountId': 'acct<id'})
    pp(_resp)
    print(f'\n--- Analysis ---')
    print(f'Status: {_resp.status_code} (422 is expected — correct)')
    print(f'Body:   {_resp.text!r}')
    if _resp.text.strip() in ('', 'null'):
        print('BUG CONFIRMED: response body is null/empty.')
        print('The spec promises an Error object with details. The generated client')
        print('crashes with TypeError because Error.from_dict(None) is not handled.')
        print('Tracked: https://plumedesign.atlassian.net/browse/PODE-3001')
    else:
        print('Bug appears to be FIXED — server now returns a proper error body.')
        print('Update the xfail marker in test_users.py!')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Cleanup

    If any cell above failed before deletion, run this to clean up the user.
    Safe to run even if the user was already deleted (just gets a 404).
    """)
    return


@app.cell
def _(USER_ID, api_client):
    try:
        with api_client() as _c:
            _resp = _c.delete(f'/v1/users/{USER_ID}')
        print(f'Cleanup: DELETE {USER_ID} -> {_resp.status_code}')
    except NameError:
        print('Nothing to clean up (USER_ID not set — create probably never succeeded)')
    return


if __name__ == "__main__":
    app.run()
