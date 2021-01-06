remove_specials=function(x){
  x=x%>%
    gsub(pattern = "Ä",replacement = "a")%>%
    gsub(pattern = "Ä",replacement = "c")%>%
    gsub(pattern = "Ä",replacement = "e")%>%
    gsub(pattern = "Å",replacement = "l")%>%
    gsub(pattern = "Å",replacement = "n")%>%
    gsub(pattern = "Ã³",replacement = "o")%>%
    gsub(pattern = "Å",replacement = "s")%>%
    gsub(pattern = "Åº",replacement = "z")%>%
    gsub(pattern = "Å¼",replacement = "z")%>%
    gsub(pattern = "Ä",replacement = "A")%>%
    gsub(pattern = "Ä",replacement = "C")%>%
    gsub(pattern = "Ä",replacement = "E")%>%
    gsub(pattern = "Å",replacement = "L")%>%
    gsub(pattern = "Å",replacement = "N")%>%
    gsub(pattern = "Ã",replacement = "O")%>%
    gsub(pattern = "Å",replacement = "S")%>%
    gsub(pattern = "Å¹",replacement = "Z")%>%
    gsub(pattern = "Å»",replacement = "Z")
  return(x)
}

set_utf8 <- function(x) {
  # Declare UTF-8 encoding on all character columns:
  chr <- sapply(x, is.character)
  x[, chr] <- lapply(x[, chr, drop = FALSE], `Encoding<-`, "UTF-8")
  # Same on column names:
  Encoding(names(x)) <- "UTF-8"
  x
}

encoding_map = set_utf8(as.data.frame(read_excel("C:/Users/kzielinski003/Desktop/predictive_qc_lion_king/monitoring/encoding.xlsx")))

mgsub(wf$AnalystAssignedName[6],pattern = encoding_map$pattern,replacement = encoding_map$replacement)
