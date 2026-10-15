if (!requireNamespace("rmarkdown", quietly=TRUE))
  install.packages("rmarkdown", repos="https://cloud.r-project.org")
if (!requireNamespace("knitr", quietly=TRUE))
  install.packages("knitr", repos="https://cloud.r-project.org")

if (!file.exists("manuscript.Rmd"))
  stop("manuscript.Rmd not found. Set wd to project root.")

cat("Working directory:", getwd(), "\n")
cat("Rendering manuscript.Rmd -> manuscript.docx\n\n")

rmarkdown::render("manuscript.Rmd", output_file="manuscript.docx", quiet=FALSE)

if (file.exists("manuscript.docx")) {
  cat("\nSUCCESS\n")
  cat("Output: manuscript.docx\n")
  cat("Size:", round(file.info("manuscript.docx")$size/1024, 1), "KB\n")
} else {
  cat("\nFAILED\n")
}
