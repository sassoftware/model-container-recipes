# Default R score code which helps score R model with rda file.
# You have to write own score file if your R model doesn't have Rda model file.

# If the Rda model file has not been specified in command line arguments, the script
# will look for the first Rda file in the current directory and it quits if not found.

args = commandArgs(trailingOnly=TRUE)

if (length(args)<2) {
  stop("Rscript _score.R [model file] <inputfile> <outputfile>.n", call.=FALSE)
} else if (length(args)<3) {
  modelfile = ''
  inputfile = args[1]
  outputfile = args[2]
} else {
  modelfile = args[1]
  inputfile = args[2]
  outputfile = args[3]
}

inputdata <- read.csv(file=inputfile, header=TRUE, sep=",")

if (modelfile == '') {
  files <- list.files(pattern = "\\.rda$")

  if(length(files) == 0) {
     print("not found rda file in the directory!")
     stop()
  }
 
  modelfile<-files[[1]]
}

model<-load(modelfile)
# -----------------------------------------------
# SCORE THE MODEL
# -----------------------------------------------
score<- predict(get(model), type="vector", newdata=inputdata)

# -----------------------------------------------
# MERGING PREDICTED VALUE WITH MODEL INPUT VARIABLES
# -----------------------------------------------
mm_outds <- cbind(inputdata, score)

write.csv(mm_outds, file = outputfile, row.names=F)

