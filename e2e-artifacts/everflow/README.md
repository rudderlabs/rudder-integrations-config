# Everflow destination E2E report

Run date: 2026-09-21

Tested revision: `ac1dff096f85bdd1d78fd3d3fa611cf58cbea350`

## Environment

The current `rudder-integrations-config` branch was seeded into a local RudderStack control-plane stack with the real config-backend, accounts, secrets, billing, permissions, and webapp services. The backend beta flag was enabled. Because the local webapp has no Flagsmith environment, the browser response was adjusted only to expose the beta-gated Everflow catalog card; account, destination, connection, and readback requests all went to the real local services.

## Journey and results

1. Created a JavaScript event-stream source.
2. Opened **Add destination → Create new destination** and selected the beta-labeled Everflow card.
3. Opened the Everflow Postback account form. A URL containing `?nid=123` was rejected with HTTP 400 and the configured guidance: `Paste only the base Global Postback URL and remove everything from ? onward`.
4. Replaced it with `https://www.example.com/postback`, supplied a non-numeric network ID and optional sample verification token, and created the account successfully (HTTP 200).
5. Created the Everflow destination and connected it to the source successfully (destination and connection HTTP 200).
6. Reloaded the source Overview. It showed **Connected destinations (1)** with the persisted Everflow destination and the expected initial Disabled status.
7. Read back the saved records. The account uses `DESTINATION_EVERFLOW_POSTBACK`; `postbackUrl` and `networkId` are in account options, while `verificationToken` is in the secret object. The destination uses `EVERFLOW`, references the account through `rudderAccountId`, and stores `connectionMode.web = cloud`.

## Finding

The create flow succeeds, but the newly-created destination's Configuration page crashes to the global error screen with `Cannot read properties of undefined (reading 'length')`. The Everflow `uiConfig` omits `sdkTemplate`; the webapp's V2 configuration builder treats `sdkTemplate` as required and destructures the result of `getConfigTemplateFields(sdkTemplate, ...)`, which returns no fields tuple when the template is absent. The source Overview still confirms that the destination and connection were persisted.

This run validates the dashboard/control-plane path. It does not send a postback to Everflow because transformer delivery is outside this repository and ticket.

## Evidence

- [Full browser recording](everflow-destination-e2e.webm)
- [Everflow catalog card](01-everflow-catalog.png)
- [Query-bearing URL validation attempt](02-query-url-validation.png)
- [Saved Everflow account selected in the wizard](03-configured-account.png)
- [Post-create Configuration page error](04-post-create-configuration-error.png)
- [Persisted destination connected to the source](05-connected-source.png)
