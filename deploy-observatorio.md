# Deploy Observatório Rural do RN

## Goal
Ingest pending documentation, fix file structure for Vercel, and deploy the application to production.

## Tasks
- [ ] **Task 1: Git Ingestion** → Add untracked files in `docs/` and `pnad_sol/docs_pnad/`.
- [ ] **Task 2: Commit Changes** → Commit with message "docs: include territorial reports and pnad documentation".
- [ ] **Task 3: Pre-flight Fix** → Run `python vercel_architecture_fix.py` to ensure index.html/dashboard.html paths are correct.
- [ ] **Task 4: Production Deploy** → Run `vercel --prod` to deploy to Vercel.
- [ ] **Task 5: Health Check** → Open the production URL and verify the main dashboard and dimensions.

## Done When
- [ ] Repository is clean and pushed to main.
- [ ] Vercel deployment is live.
- [ ] Dashboards are loading dynamic data correctly in production.

## Notes
- The project uses a mix of Static HTML and Python Serverless Functions (`api/index.py`).
- No `package.json` present, Vercel will auto-detect the configuration.
