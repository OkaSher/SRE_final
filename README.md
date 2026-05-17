# SRE_final
CI/CD and Deployment
=====================

Required GitHub Secrets
- `DOCKERHUB_USERNAME` — your Docker Hub username
- `DOCKERHUB_REPOSITORY` — repository name (image name) in Docker Hub, e.g. `sre_app`
- `DOCKERHUB_TOKEN` — Docker Hub access token or password
- `SSH_HOST` — target server IP or hostname (e.g. 35.202.129.148)
- `SSH_USER` — SSH user on the server (e.g. `ubuntu`)
- `SSH_PRIVATE_KEY` — private SSH key (PEM) for `SSH_USER`

How it works
- On push to `main` (or when started manually via "Run workflow"), GitHub Actions will:
  1. Checkout the repository
  2. Compute the image name as `${{ secrets.DOCKERHUB_USERNAME }}/${{ secrets.DOCKERHUB_REPOSITORY }}`
  3. Log in to Docker Hub and build+push the image from `./app` with tags `:latest` and `:${{ github.sha }}`
  4. SSH to `SSH_HOST` as `SSH_USER` and run a small script that pulls `:latest`, stops and removes the old container, and runs the new one on port 8080

Triggering
- Push to `main`:

```bash
git checkout main
git add .
git commit -m "Trigger CI/CD"
git push origin main
```

- Or run the workflow manually in the Actions tab (because `workflow_dispatch` is enabled).

Setting secrets via GitHub CLI (example):

```bash
gh secret set DOCKERHUB_USERNAME --body "myuser"
gh secret set DOCKERHUB_REPOSITORY --body "sre_app"
gh secret set DOCKERHUB_TOKEN --body "<docker-token>"
gh secret set SSH_HOST --body "35.202.129.148"
gh secret set SSH_USER --body "ubuntu"
gh secret set SSH_PRIVATE_KEY --body "$(cat ~/.ssh/id_rsa)"
```

Notes and checks performed
- Workflow file: [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml) — it builds from `./app`, pushes to Docker Hub, and uses SSH action to update the container on the remote host.
- Ensure the `SSH_PRIVATE_KEY` has access to the `SSH_USER` on `SSH_HOST` and that Docker is installed on the VM.
- The production host provided: `35.202.129.148` (set as `SSH_HOST` secret or use the UI to input it).

If anything fails when the workflow runs, check the Actions log for the failing step (Build/Push or SSH deploy) and paste the error here — I will help fix it.
