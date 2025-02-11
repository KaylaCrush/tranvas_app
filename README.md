# Tranvas: a Canvas integration for Trello

This application syncs assignments from Canvas to a Trello board, keeping track of due dates and submission statuses. It helps you stay organized by automatically updating your Trello cards based on Canvas assignments.

To use this app, you need API tokens for both **Canvas** and **Trello**. Follow the instructions below to generate them.

---
#### Generating a Trello API Key and Token

Get a Trello Key and Token as [described here](https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/).

You'll need both the **API Key** and **Token** when setting up this app. Make sure you record them!


#### Generating a Canvas API Token

1. Log into your Canvas account.
2. Click on your profile icon in the top-left corner.
3. Select **"Settings"**.
4. Scroll down to the **Approved Integrations** section.
5. Click **"+ New Access Token"**.
6. Give the token a meaningful name (e.g., "Trello Integration").
7. Set an expiration date if needed, or 0 for no expiration.
8. Click **"Generate Token"** and copy it immediately.
   **Note:** You won’t be able to see this token again after leaving the page.

---
#### Remote Configuration
To run the project remotely via github actions, you will need to set your keys as github secrets:
1. Go to your GitHub repository.
2. Click on **Settings**.
3. In the left sidebar, click **Secrets and variables** → **Actions**.
4. Click the **New repository secret** button.
5. Add the following secrets:
   - **`TRELLO_KEY`** → Your Trello API Key
   - **`TRELLO_TOKEN`** → Your Trello API Token
   - **`CANVAS_TOKEN`** → Your Canvas API Token



#### Local Configuration

To run the program on your local machine, store the keys in a `.env` file or pass them as environment variables:

```env
TRELLO_API_KEY=your_trello_api_key
TRELLO_TOKEN=your_trello_api_token
CANVAS_API_TOKEN=your_canvas_api_token
```
