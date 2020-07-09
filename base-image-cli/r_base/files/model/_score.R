# Default R score code which helps score R model with rda file.
# You have to write own score file if your R model doesn't have Rda model file.

# If the Rda model file has not been specified in command line arguments, the script
# will look for the first Rda file in the current directory and it quits if not found.

suppressPackageStartupMessages(library("argparse"))

parser <- ArgumentParser()
parser$add_argument("-m", "--model", help="model filename")
parser$add_argument("-i", "--input", help="input filename")
parser$add_argument("-o", "--output", help="output filename")
args <- parser$parse_args()

modelfile <- args$model
inputfile <- args$input
outputfile <- args$output

inputdata <- read.csv(file=inputfile, header=TRUE, sep=",")

if (is.null(modelfile)) {
  # search for model file
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

