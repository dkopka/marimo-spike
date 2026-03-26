# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "requests",
# ]
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    css_file="/usr/local/_marimo/custom.css",
    auto_download=["html"],
)


# ── Imports ────────────────────────────────────────────────────────────────────

@app.cell(hide_code=True)
def _():
    import marimo as mo
    import requests
    import json
    import os
    return json, mo, os, requests


# ── Title ──────────────────────────────────────────────────────────────────────

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Plume API Quick Start

    A step-by-step walkthrough of the minimum requirements to get your first Plume API request up and running.

    | Step | Action | Endpoint |
    |------|--------|----------|
    | 1 | Generate an Access Token | OAuth 2.0 Token URL |
    | 2 | Configure connection details | — |
    | 3 | Create a User | `POST /v1/users` |
    | 4 | Get the User's Location | `GET /v1/locations/{id}` |
    | 5 | Assign internal identifiers | `PATCH /v1/users/{id}` · `PATCH /v1/locations/{id}` |

    Run each section top to bottom. API responses feed automatically into the next step.
    """)
    return


# ── Step 1 — Generate an Access Token ─────────────────────────────────────────

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 1 — Generate an Access Token

    Plume APIs use **OAuth 2.0 Client Credentials** (machine-to-machine). After creating an API Token
    in the Plume Portal you receive three values needed to mint a short-lived JWT bearer token:

    - **Authorization Token URL** — the OAuth token endpoint for your deployment
    - **Authorization Header** — `Basic <base64(clientId:clientSecret)>` (shown **once** in the Portal — store it safely)
    - **Scope** — controls which APIs the token can access

    > 💡 Load secrets from environment variables rather than pasting them here:
    > `AUTH_TOKEN_URL`, `AUTH_HEADER`, `AUTH_SCOPE`.

    > ⚠️ Reuse access tokens until they expire — do **not** mint a new token per API call.
    """)
    return


@app.cell
def _(mo, os):
    auth_token_url = mo.ui.text(
        value=os.environ.get("AUTH_TOKEN_URL", ""),
        placeholder="https://yourco.okta.com/oauth2/default/v1/token",
        label="Authorization Token URL",
        full_width=True,
    )
    auth_header_input = mo.ui.text(
        value=os.environ.get("AUTH_HEADER", ""),
        placeholder="Basic dXNlcjpwYXNzd29yZA==",
        label="Authorization Header",
        full_width=True,
    )
    scope_input = mo.ui.text(
        value=os.environ.get("AUTH_SCOPE", ""),
        placeholder="partnerId:6971f4934016be004a041191 role:partnerIdAdmin",
        label="Scope",
        full_width=True,
    )
    mint_button = mo.ui.run_button(label="🔑 Mint Access Token")
    mo.vstack([auth_token_url, auth_header_input, scope_input, mint_button])
    return auth_header_input, auth_token_url, mint_button, scope_input


@app.cell
def _(auth_header_input, auth_token_url, mint_button, mo, requests, scope_input):
    access_token = None
    if mint_button.value:
        try:
            _resp = requests.post(
                auth_token_url.value,
                headers={
                    "Authorization": auth_header_input.value,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": scope_input.value,
                },
                timeout=10,
            )
            _resp.raise_for_status()
            access_token = _resp.json().get("access_token")
        except Exception as _e:
            access_token = None

    (
        mo.callout(
            mo.md(
                f"✅ **Access token minted successfully.**\n\n"
                f"```\n{access_token[:80]}…\n```"
            ),
            kind="success",
        )
        if access_token
        else mo.callout(
            mo.md("Fill in your credentials above and click **🔑 Mint Access Token** to continue."),
            kind="info",
        )
    )
    return (access_token,)


# ── Step 2 — Connection Details ────────────────────────────────────────────────

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 2 — Set Connection Details

    Set your API base URL and Partner ID. These are used in every subsequent request.

    You can also set them from the environment: `API_URL`, `PARTNER_ID`.
    """)
    return


@app.cell
def _(mo, os):
    api_url_input = mo.ui.text(
        value=os.environ.get("API_URL", ""),
        placeholder="https://api.usw2.prod.plume.tech",
        label="API Base URL",
        full_width=True,
    )
    partner_id_input = mo.ui.text(
        value=os.environ.get("PARTNER_ID", ""),
        placeholder="6971f4934016be004a041191",
        label="Partner ID",
        full_width=True,
    )
    mo.vstack([api_url_input, partner_id_input])
    return api_url_input, partner_id_input


# ── Step 3 — Create a User ─────────────────────────────────────────────────────

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 3 — Create a User

    `POST /v1/users` creates a new customer. The request body requires **name**, **email**,
    and **partnerId**.

    > **Note:** Creating a User also automatically creates a default Location (`"Home"`, type `RESIDENTIAL`).
    > A User cannot exist without at least one Location. The `locationId` is returned in the response
    > and used in Steps 4 and 5.
    """)
    return


@app.cell
def _(mo):
    user_name_input = mo.ui.text(
        value="Jane Doe",
        placeholder="Jane Doe",
        label="Name",
        full_width=True,
    )
    user_email_input = mo.ui.text(
        value="jdoe369@example.com",
        placeholder="jdoe369@example.com",
        label="Email",
        full_width=True,
    )
    create_user_button = mo.ui.run_button(label="👤 Create User")
    mo.vstack([user_name_input, user_email_input, create_user_button])
    return create_user_button, user_email_input, user_name_input


@app.cell
def _(
    access_token,
    api_url_input,
    create_user_button,
    json,
    mo,
    partner_id_input,
    requests,
    user_email_input,
    user_name_input,
):
    user_id = None
    location_id = None
    create_user_response = None

    if create_user_button.value:
        try:
            _resp = requests.post(
                f"{api_url_input.value}/v1/users",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
                json={
                    "name": user_name_input.value,
                    "email": user_email_input.value,
                    "partnerId": partner_id_input.value,
                },
                timeout=10,
            )
            _resp.raise_for_status()
            create_user_response = _resp.json()
            user_id = create_user_response.get("id")
            location_id = create_user_response.get("location", {}).get("id")
        except Exception as _e:
            create_user_response = {"error": str(_e)}

    (
        mo.vstack([
            mo.callout(
                mo.md(
                    f"✅ **User created.**\n\n"
                    f"- `userId`: `{user_id}`\n"
                    f"- `locationId`: `{location_id}`\n\n"
                    f"These IDs are automatically used in Steps 4 and 5."
                ),
                kind="success",
            ),
            mo.md(f"```json\n{json.dumps(create_user_response, indent=2)}\n```"),
        ])
        if user_id
        else (
            mo.callout(
                mo.md(f"❌ **Error:** `{create_user_response.get('error')}`"),
                kind="danger",
            )
            if create_user_response and "error" in create_user_response
            else mo.callout(
                mo.md("Complete Steps 1 & 2, then click **👤 Create User**."),
                kind="info",
            )
        )
    )
    return create_user_response, location_id, user_id


# ── Step 4 — Get the User's Location ──────────────────────────────────────────

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 4 — Get the User's Location

    `GET /v1/locations/{locationId}` returns the full Location record.

    The `locationId` from Step 3 is used automatically — this cell reruns as soon as a User is created.
    """)
    return


@app.cell
def _(access_token, api_url_input, json, location_id, mo, requests):
    location_data = None
    if location_id:
        try:
            _resp = requests.get(
                f"{api_url_input.value}/v1/locations/{location_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            _resp.raise_for_status()
            location_data = _resp.json()
        except Exception as _e:
            location_data = {"error": str(_e)}

    (
        mo.vstack([
            mo.callout(
                mo.md(f"✅ **Location retrieved.** `locationId`: `{location_id}`"),
                kind="success",
            ),
            mo.md(f"```json\n{json.dumps(location_data, indent=2)}\n```"),
        ])
        if location_data and "error" not in location_data
        else (
            mo.callout(
                mo.md(f"❌ **Error:** `{location_data.get('error') if location_data else ''}`"),
                kind="danger",
            )
            if location_data and "error" in location_data
            else mo.callout(
                mo.md("Waiting for a `locationId` from Step 3…"),
                kind="info",
            )
        )
    )
    return (location_data,)


# ── Step 5 — Assign Internal Identifiers ──────────────────────────────────────

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 5 — Assign Internal Identifiers *(optional)*

    Link Plume records to your own CRM or billing system using two identifiers:

    - **`accountId`** on the **User** — your customer's account reference (e.g., a UUID from your CRM)
    - **`serviceId`** on the **Location** — the service contract reference (e.g., a subscription ID)

    These make it easy to look up Plume data using your own IDs, and vice versa.
    See [accountId vs serviceId](../core-concepts/entity-hierarchy.md#accountid-vs-serviceid) for details.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("### 5a — Update `accountId` on User")
    return


@app.cell
def _(mo):
    account_id_input = mo.ui.text(
        value="9eec69a9-5e27-4110-bdf3-146ed14e1632",
        placeholder="your-crm-account-uuid",
        label="accountId (your CRM reference for this customer)",
        full_width=True,
    )
    update_account_button = mo.ui.run_button(label="✏️ Update accountId")
    mo.vstack([account_id_input, update_account_button])
    return account_id_input, update_account_button


@app.cell
def _(
    access_token,
    account_id_input,
    api_url_input,
    json,
    mo,
    requests,
    update_account_button,
    user_id,
):
    updated_user = None
    if update_account_button.value and user_id:
        try:
            _resp = requests.patch(
                f"{api_url_input.value}/v1/users/{user_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
                json={"accountId": account_id_input.value},
                timeout=10,
            )
            _resp.raise_for_status()
            updated_user = _resp.json()
        except Exception as _e:
            updated_user = {"error": str(_e)}

    (
        mo.vstack([
            mo.callout(mo.md("✅ **`accountId` updated on User.**"), kind="success"),
            mo.md(f"```json\n{json.dumps(updated_user, indent=2)}\n```"),
        ])
        if updated_user and "error" not in updated_user
        else (
            mo.callout(
                mo.md(f"❌ **Error:** `{updated_user.get('error') if updated_user else ''}`"),
                kind="danger",
            )
            if updated_user and "error" in updated_user
            else mo.callout(
                mo.md("Complete Step 3 first, then click **✏️ Update accountId**."),
                kind="info",
            )
        )
    )
    return (updated_user,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("### 5b — Update `serviceId` on Location")
    return


@app.cell
def _(mo):
    service_id_input = mo.ui.text(
        value="92283fcf-abbe-4580-ab0f-82a99ebda411",
        placeholder="your-crm-service-contract-uuid",
        label="serviceId (contract/subscription reference)",
        full_width=True,
    )
    location_name_input = mo.ui.text(
        value="CentralParkApartment",
        placeholder="CentralParkApartment",
        label="Location name",
        full_width=True,
    )
    location_type_input = mo.ui.dropdown(
        options=["RESIDENTIAL", "SMALL_BUSINESS"],
        value="RESIDENTIAL",
        label="Location type",
    )
    update_location_button = mo.ui.run_button(label="✏️ Update serviceId")
    mo.vstack([service_id_input, location_name_input, location_type_input, update_location_button])
    return location_name_input, location_type_input, service_id_input, update_location_button


@app.cell
def _(
    access_token,
    api_url_input,
    json,
    location_id,
    location_name_input,
    location_type_input,
    mo,
    requests,
    service_id_input,
    update_location_button,
):
    updated_location = None
    if update_location_button.value and location_id:
        try:
            _resp = requests.patch(
                f"{api_url_input.value}/v1/locations/{location_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
                json={
                    "name": location_name_input.value,
                    "type": location_type_input.value,
                    "serviceId": service_id_input.value,
                },
                timeout=10,
            )
            _resp.raise_for_status()
            updated_location = _resp.json()
        except Exception as _e:
            updated_location = {"error": str(_e)}

    (
        mo.vstack([
            mo.callout(mo.md("✅ **`serviceId` updated on Location.**"), kind="success"),
            mo.md(f"```json\n{json.dumps(updated_location, indent=2)}\n```"),
        ])
        if updated_location and "error" not in updated_location
        else (
            mo.callout(
                mo.md(f"❌ **Error:** `{updated_location.get('error') if updated_location else ''}`"),
                kind="danger",
            )
            if updated_location and "error" in updated_location
            else mo.callout(
                mo.md("Complete Step 3 first, then click **✏️ Update serviceId**."),
                kind="info",
            )
        )
    )
    return (updated_location,)


# ── Summary ────────────────────────────────────────────────────────────────────

@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md(r"""
        **🎉 You're all set!**

        With these steps complete you have:

        - Authenticated via OAuth 2.0 Client Credentials and minted a JWT bearer token
        - Created a User with an auto-provisioned Location
        - Retrieved the Location record using the `locationId`
        - Linked your CRM identifiers (`accountId`, `serviceId`) to Plume records

        **Next steps:** explore the full API reference or read the
        [entity hierarchy guide](../core-concepts/entity-hierarchy.md) to understand how
        Users, Locations, and Nodes relate to each other.
        """),
        kind="success",
    )
    return


if __name__ == "__main__":
    app.run()
