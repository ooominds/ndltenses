####################
# Preliminary steps
####################

### Loading libraries
#library(data.table) # For fast large data manipulation
import pandas as pd

### File paths
TENSE_DATA_FOLDER = file.path(TOP, "Data_shared/")
SENT_LENGTHS = file.path(WD, "Results/freq_table_sent_length.csv")


###################
# Data exploration
###################

# Load the training dataset
#files = paste0(DATA_FOLDER, 
#               list.files(path = DATA_FOLDER, 
#                          pattern = "^sentences_BNC_[0-9]+.csv"))
#tic()
#tenses_dt = as.data.table(rbindlist(lapply(files, function(x) fread(x, select = c('sentence', 'sentence_length', 'num_verb_tags')))))
#toc() 

#summary(tenses_dt)
#    sentence         sentence_length  num_verb_tags    
#  Length:4267590     Min.   :  2.00   Min.   :  1.000  
#  Class :character   1st Qu.: 10.00   1st Qu.:  2.000  
#  Mode  :character   Median : 16.00   Median :  3.000  
#                     Mean   : 18.64   Mean   :  3.412  
#                     3rd Qu.: 24.00   3rd Qu.:  4.000  
#                     Max.   :603.00   Max.   :150.000 

#head(tenses_dt, 5)
                                                                                                                            # sentence sentence_length
# 1:                                                                                                            factsheet what is aids               4
# 2:                              immune deficiency syndrome is a condition caused by a virus called hiv human immuno deficiency virus              16
# 3:                                                     this virus affects the body defence system so that it can not fight infection              14
# 4: it is not transmitted from giving blood mosquito bites toilet seats kissing from normal day to day contact how does it affect you              23
# 5:            the medical aspects can be cancer pneumonia sudden blindness dementia dramatic weight loss or any combination of these              18
#    num_verb_tags
# 1:             1
# 2:             3
# 3:             3
# 4:             5
# 5:             2

# Histograms
#hist(tenses_dt$sentence_length)

# extreme quantiles
#quantile(tenses_dt$sentence_length, probs = c(0.01, 0.99))
#  1% 99% 
#  3  60 

# Number of sentences with length < 3
#length(which(tenses_dt$sentence_length<3))
# 9 OUT OF 4,267,590 sentences. 

# Number of sentences with length > 60
#length(which(tenses_dt$sentence_length>60))
# 40235 OUT OF 4,267,590 sentences. 
#sum(freq_sent_length$freq[freq_sent_length$sent_length>60])

# After removing long sentences
#tenses_dt_60 = tenses_dt[which(tenses_dt$sentence_length<=60 & tenses_dt$sentence_length>=3), ]

# Max number of verb tags
#max(tenses_dt_60$num_verb_tags) # 26

#tenses_dt_60$sentence[which(tenses_dt_60$num_verb_tags == 26)]

# Histograms
#png('./Results/hist_sent_lengths.png', he=6, wi=9, units='in', res=300)
#hist(tenses_dt_60$sentence_length, xlab = 'Sentence length', main = "")
#dev.off()
#hist(tenses_dt_60$num_verb_tags, xlab = 'Number of verb tags')
