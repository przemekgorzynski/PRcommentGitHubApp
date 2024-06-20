# GitHub App
GitHub app written in Python to put comments inside PR. 

Currently it just put example MD text, but action could be alligned inside code.

```md
## Pull Request Review
### Comment written by GitHub App

### Checklist:
- [ ] Fix bugs
- [ ] Tests have been added/updated
- [ ] Documentation has been updated

Happy Coding! :smile:
```
## Table of content
- [GitHub App](#GitHub-App)
  - [Table of Content](#table-of-content)
  - [Registering GitHub App](#registering-github-app)
  - [Building Docker Image](#building-docker-image)
  - [Running App Locally](#running-app-locally)

### Registering GitHub App

1. Click on your account -> Settings -> Developer Settings
2. Click New GitHub App
3.  Fill following fields: 
    * GitHub App name
    * Homepage URL - Link to repository where App code is stored
    * Webhook URL - URL where app will be listening (/webhook path)
      * eg. https://prcomment.example.com/webhook
    * Webhook secret - set random secret to protect your webhooks
    * Permissions 
      * Repository permissions -> Pull requests -> Read and Write
    * Subscribe to events -> Pull request
    * Where can this GitHub App be installed?
      * Any account
4. After creating WebApp collect following data
    * App_ID
    * Generate and store provate key

### Building docker image

1. Store you secrets in repo files. Will be copied to docker image and used by python app.
    * secrets/app_id
    * secrets/webhook_secret
    * secrets/github.pem

### Running APP locally
1. Install smee package and redirect traffic to your local instance

    `smee -u https://smee.io/tX7AEoeQo5sUKNji --path /webhook --port 8000`

2. Update GitHub App `Webhook URL` to smee generated link
3. Run python script

    `uvicorn app:app --reload`