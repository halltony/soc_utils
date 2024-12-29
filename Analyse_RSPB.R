library(tidyverse)
library(readxl)
rspb <- read_excel('/Users/Tony/soc_utils/RSPB-2023 Incidental and ARM Records Clyde Reserves.xlsx', guess_max=Inf)
unique(rspb$Comments)
