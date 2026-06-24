# Report

`main.tex` is the project report. It compiles with any LaTeX setup.

## Compile

- **Overleaf:** upload `main.tex` (and the `figures/` folder), then Recompile.
- **Local:** `pdflatex main.tex` twice (the second pass fixes references), or `latexmk -pdf main.tex`.

## Screenshots

Each view has a figure slot that compiles as a gray placeholder until you add an image.
To insert a real screenshot:

1. Save the image in `figures/`, e.g. `figures/artist.png`, `figures/genre.png`, `figures/stars.png`.
2. In `main.tex`, find the matching `\viewfig{...}` line and replace the `\fbox{...}` line inside
   the `\viewfig` macro definition with `\includegraphics`, or simply swap each `\viewfig` call for a
   normal figure that uses `\includegraphics[width=0.9\linewidth]{artist.png}`.
