# Submission checklist

## Local repo state
The project is a working Git repo on branch `main` with a tagged submission commit. The
report is in `report/main.tex` (compiles on Overleaf) and the live app under `src/`.

```bash
git log --oneline       # see the commit history
git tag                 # see the submission tag
```

## 1. Push to GitHub

The instructor expects a Git repository (and the slides mention single classroom repo with
per-student forks). On <https://github.com> create a new public repo named
`oceanus-folk-explorer` (or your preferred name), then from this folder:

```bash
git remote add origin https://github.com/<your-github-username>/oceanus-folk-explorer.git
git push -u origin main
git push origin --tags
```

If the course has a classroom org (e.g. `va602aa-master`) the instructor wants you to fork
into, fork it on GitHub, then change the URL above to your fork and push the same way.

## 2. Compile the report on Overleaf

1. New Project → Upload Project → upload `report/` (the whole folder).
2. Recompile. The output PDF embeds the three view screenshots from `report/figures/`.
3. Download the PDF as `oceanus_folk_explorer.pdf` (or any name with `[VA]` in the
   filename for clarity).

## 3. Send the report email

Email the PDF to Salvatore Rinzivillo **at least four days before the discussion date**.
The subject line **must** start with `[VA]`.

Template:

> **To:** rinzivillo@isti.cnr.it
> **Subject:** `[VA] Final project report — Iskandar Huseynzade (618017)`
>
> Dear Professor Rinzivillo,
>
> Attached is the report for my final project, Oceanus Folk Explorer, based on VAST 2025
> Mini-Challenge 1. The source repository is at
> <https://github.com/your-username/oceanus-folk-explorer>.
>
> Thank you,
> Iskandar Huseynzade
> Matricola 618017

## 4. Register for the discussion

Register on <https://esami.unipi.it> for the chosen discussion date (admission requires
registration).

## 5. On the discussion day

Be ready to:
- Run `npm install && npm run dev` and walk through the three tabs live.
- Show one analytical task per tab and explain the design (this is what the report
  describes).
- Open `data/README.md` to discuss the schema and edge-direction rule.
- Open `report/main.tex` if asked about a specific choice.
