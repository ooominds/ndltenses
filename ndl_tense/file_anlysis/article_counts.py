from numpy import mean
import logging
logging.basicConfig(level=logging.DEBUG)

def distances(x):
    avg_dis = mean([x[n]-x[n-1] for n in range(1,len(x))])
    return(avg_dis)

def counts(data_read, def_info, indef_info, null_info, null_token):
    """
        produce a count of each article type from a file
    ----
    PARAMETERS
    ----
    data_read: generator of lines from a file
        processed by identifying and counting articles in each line
    def_info: double (list, int)
        a list of the positions of definite articles and a running count of articles so far as an int
    indef_info: double (list, int)
        a list of the positions of indefinite articles and a running count of articles so far as an int
    null_info: double (list, int)
        a list of the positions of null articles and a running count of articles so far as an int
    ----
    RETURN
    ----
        4 doubles like (list, int), one for each article and one for all articles.
        the list is of the positions in which each article type was found and the count is the
        total number of article tokens
    """
    position_count = 0
    article_pos = []
    article_no_null = []
    def_pos, indef_pos, null_pos = def_info[1], indef_info[1], null_info[1]
    def_count, indef_count, null_count = def_info[0], indef_info[0], null_info[0]
    for line in data_read:
        strip_line = line.strip('\n').split('\t')
        word = strip_line[0].strip()
        tag = strip_line[1].strip()
        if word in ['The', 'the']:
            def_count += 1
            def_pos.append(position_count)
            article_pos.append(position_count)
            article_no_null.append(position_count)
        elif word in ['a', 'an', 'An', 'A']:
            indef_count += 1
            indef_pos.append(position_count)
            article_pos.append(position_count)
            article_no_null.append(position_count)
        elif word in [null_token]:
            null_count += 1
            null_pos.append(position_count)
            article_pos.append(position_count)
        position_count += 1
    return((def_count, def_pos),
           (indef_count, indef_pos),
           (null_count, null_pos), article_pos, article_no_null)

# Get total counts of articles and the mean distances between article tokens in a text
def article_counts(infile, VERBOSE, null_token='ø'):
    """
        gives the total count and average distance between articles in a file
    ----
    PARAMTERS
    ----
    infile: path/str
        path to the file with articles
    VERBOSE:
        Whether to log the end result of the process into the terminal
    null_token: str
        the str used to represent the null_token
    ----
    RETURN
    ----
    avg_pos: (double, double, double, float, float)
        returns the following
        (count of definite articles, average distance between definite articles)
        (count of indefinite articles, average distance between indefinite articles)
        (count of null articles, average distance between null articles)
        (average distance to an article in general)
        (average distance to an article but ignoring the null article)

    """
    data_read = (line for line in open(infile, 'r', encoding="utf-8"))

    def_count, indef_count, null_count = 0,0,0
    def_pos, indef_pos, null_pos = [], [], []
    def_info, indef_info, null_info = (def_count, def_pos), (indef_count, indef_pos), (null_count, null_pos)
    def_info, indef_info, null_info, article_pos, article_no_null = counts(data_read, def_info, indef_info, null_info, null_token)
    avg_pos = (distances(def_info[1]), distances(indef_info[1]), distances(null_info[1]), distances(article_pos), distances(article_no_null))
    if VERBOSE:
        logging.info("DEF INFO - \ncount: %s \nmean distances %s"%(def_info[0], avg_pos[0]))
        logging.info("INDEF INFO - \ncount: %s \nmean distances %s"%(indef_info[0], avg_pos[1]))
        logging.info("NULL INFO - \ncount: %s \nmean distances %s\n"%(null_info[0], avg_pos[2]))
        logging.info("mean distance to article: %s"%(avg_pos[3]))
        logging.info("mean distance to article (whithout null article): %s"%(avg_pos[4]))

    # count of definite articles, average distance between definite articles
    # count of indefinite articles, average distance between indefinite articles
    # count of null articles, average distance between null articles
    # average distance to an article in general
    # average distance to an article but ignoring the null article
    return((def_info[0], avg_pos[0]), (indef_info[0], avg_pos[1]), (null_info[0], avg_pos[2]), avg_pos[3], avg_pos[4])
