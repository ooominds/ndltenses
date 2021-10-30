# python implementation of the R word() function just for the purpose of this work
def word(a,b):
    word_split = a.split()
    #return(word_split[b-1])
    if b-1 < (len(word_split) - 1):      
      return(word_split[b-1])
    else:
      return("")
# python implementation of the R grepl() function just for the purpose of this work
def grepl(a,b):
  return([a in x for x in b])

# python implementation of the R paste() function just for the purpose of this work
def paste(a,b):
  a = [str(x) for x in a]
  return(b.join(a))


def get_tenses(vect_tags):    
    # Function that accepts a row vector containing verbs, tags, and positions then convert it
    # to a row vector that includes the same variables as well as verb form, main verb and tense   
  
    ############ Generating the tenses ##############

    ### Define tense of the first verb 
    vect_tenses = {"Tense":"", "VerbForm":"", "MainVerb":"", "Position":"", "infinitive":""}
    #print(vect_tags)
    c_names = list(vect_tags.columns)

    ################### Imperatives ######################

    # Examples: Writenot/ Please writenot/ Be carfulnot
    if ((vect_tags.iloc[0]['Verb1'] in ["be"]) and (vect_tags.iloc[0]["Position1"] == 1)) or ((vect_tags.iloc[0]['Tag1'] in ["VVB"]) and not(vect_tags.iloc[0][ "Verb1"] in ["thank"]) and (vect_tags.iloc[0][ "Position1"] == 1)) or ((vect_tags.iloc[0]["Position1"] == 2) and (word(vect_tags.iloc[0]['Sentence'], 1) in ["please"])):
        vect_tenses['Tense'] = "imperative"
        vect_tenses['MainVerb'] = vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm'] = vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']
      # Don't writenot Don't be a sillynot
    elif (vect_tags.iloc[0][ "Tag1"] in ["VDI"]) or ((vect_tags.iloc[0]['Tag1'] in ["VDB"]) and (vect_tags.iloc[0]["Position1"]==1) and ("Verb2" in c_names) and ((vect_tags.iloc[0][ "Position2"]) < (vect_tags.iloc[0][ "Position1"] + 3)) and (word(vect_tags.iloc[0][ "Sentence"], vect_tags.iloc[0]["Position1"] + 1) in ["not"]) and (vect_tags.iloc[0][ "Tag2"] in ["VVI", "VBI"])):
        vect_tenses['Tense'] = "imperative"
        vect_tenses['MainVerb'] = vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm'] = paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]["Verb2"]],  " ")
        vect_tenses['Position'] = vect_tags.iloc[0][ 'Position2']

  ################### Modals ###########################
  
  # Modal auxiliaries followed by "to" (e.g. "used to" and "ought not to")
  # cases of 'modal + be + V-en' or 'modal + be + V-ing' (e.g. He ought not to be sleeping)        
    elif (vect_tags.iloc[0]['Tag1'] in ["VM0"]) and (not(vect_tags.iloc[0]['Verb1'] in ["will"])) and ((word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["to"]) or (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["not"])) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+2) in ["to"]) and (vect_tags.iloc[0]['Verb2'] in ["be"]) and (vect_tags.iloc[0]['Tag3'] in ["VDG", "VHG", "VVG", "VDN", "VVN"]) and (int(vect_tags.iloc[0]['Position3']) < (int(vect_tags.iloc[0]['Position2'])+4)):
        vect_tenses['Tense'] = "modal"
        vect_tenses['MainVerb'] = vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm'] = paste([vect_tags.iloc[0]['Verb1'], "to", vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']

  # Modal auxiliaries followed by "to" (e.g. "used to" and "ought not to")
  # cases of 'modal + have + been + V-en' (e.g. They ought to have been working)
    elif (vect_tags.iloc[0]['Tag1'] in ["VM0"]) and (not(vect_tags.iloc[0]['Verb1'] in ["will"])) and ((word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["to"]) or (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["not"])) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+2) in ["to"]) and (vect_tags.iloc[0]['Verb2'] in ["have"]) and (vect_tags.iloc[0]['Verb3'] in ["been"]) and (vect_tags.iloc[0]['Tag4'] in ["VDN", "VVN"]) and (int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4) and (int(vect_tags.iloc[0]['Position4']) < (int(vect_tags.iloc[0]['Position3'])+4)):
        vect_tenses['Tense'] = "modal"
        vect_tenses['MainVerb'] = vect_tags.iloc[0]['Verb4']
        vect_tenses['VerbForm'] = paste([vect_tags.iloc[0]['Verb1'], "to", vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3'], vect_tags.iloc[0]['Verb4']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position4']

  # Modal auxiliaries followed by "to" (e.g. "used to" and "ought not to")
  # cases of 'modal + have + V-en' (e.g. They ought to have done)
    elif (vect_tags.iloc[0]['Tag1'] in ["VM0"]) and (not(vect_tags.iloc[0]['Verb1'] in ["will"])) and ((word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["to"]) or (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["not"])) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+2) in ["to"]) and (vect_tags.iloc[0]['Verb2'] in ["have"]) and (vect_tags.iloc[0]['Tag3'] in ["VBN","VDN", "VVN"]) and (int(vect_tags.iloc[0]['Position3']) < (int(vect_tags.iloc[0]['Position2'])+4)):
        vect_tenses['Tense'] = "modal"
        vect_tenses['MainVerb'] = vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm'] = paste([vect_tags.iloc[0]['Verb1'], "to", vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']]," ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']

  # Modal auxiliaries followed by "to" (e.g. "used to" and "ought not to") 
  # all other cases
    elif (vect_tags.iloc[0]['Tag1'] in ["VM0"]) and (not(vect_tags.iloc[0]['Verb1'] in ["will"])) and ('Verb2' in c_names) and ((word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["to"]) or (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["not"])) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+2) in ["to"]):
        vect_tenses['Tense'] = "modal"
        vect_tenses['MainVerb'] = vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm'] = paste([vect_tags.iloc[0]['Verb1'], "to", vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  # Other modal verbs except will (can, should, may)
  # cases of 'modal + be + V-en' or 'modal + be + V-ing' (e.g. This can be delivered; They should be working)
    elif (vect_tags.iloc[0]['Tag1'] in ["VM0"]) and (not(vect_tags.iloc[0]['Verb1'] in ["will"])) and (vect_tags.iloc[0]['Verb2'] in ["be"]) and (vect_tags.iloc[0]['Tag3'] in ["VDG", "VHG", "VVG", "VDN", "VVN"]) and (int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4):
        vect_tenses['Tense'] = "modal"
        vect_tenses['MainVerb'] = vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm'] = paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']
  # Other modal verbs except will (can, should, may)
  # cases of 'modal + have + been + V-en' (e.g. They could have been saved; They should have been saved)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VM0"]) and not(vect_tags.iloc[0]['Verb1'] in ["will"]) and (vect_tags.iloc[0]['Verb2'] in ["have"]) and (vect_tags.iloc[0]['Verb3'] in ["been"]) and (vect_tags.iloc[0]['Tag4'] in ["VDN", "VVN"]) and (int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4) and (int(vect_tags.iloc[0]['Position4']) < int(vect_tags.iloc[0]['Position3'])+4)):
        vect_tenses['Tense'] = "modal"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb4']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3'], vect_tags.iloc[0]['Verb4']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position4']
  # Other modal verbs except will (can, should, may)
  # cases of 'modal + have + V-en' (e.g. They could have saved her; They should have saved her)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VM0"]) and not(vect_tags.iloc[0]['Verb1'] in ["will"]) and (vect_tags.iloc[0]['Verb2'] in ["have"]) and (vect_tags.iloc[0]['Tag3'] in ["VBN","VDN", "VVN"]) and (int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4)):
        vect_tenses['Tense'] = "modal"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']
  # Other modal verbs except will (They can write; They should write)
  # other cases
    elif ((vect_tags.iloc[0]['Tag1'] in ["VM0"]) and not(vect_tags.iloc[0]['Verb1'] in ["will"]) and ('Verb2' in c_names)):
        vect_tenses['Tense'] = "modal"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  
  # To remove (was gonna)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBD"]) and (vect_tags.iloc[0]['Verb2'] in ["going", "gon"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position2'])+1) in ["to", "na"]) and (vect_tags.iloc[0]['Tag3'] in ["VVI", "VDI"]) and (int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4)):
        vect_tenses['Tense'] = "modal"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  ################### Present simple ###################
  
  ### Active voice
  
  # Present simple - lexical verbs  (They write)
    elif (vect_tags.iloc[0]['Tag1'] in ["VVZ", "VVB"]):
        vect_tenses['Tense'] = "present.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']
  # Present simple - modal need  (They need)
    elif ((vect_tags.iloc[0]['Verb1'] in ["need","needs"]) and not(word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["to"])):
        vect_tenses['Tense'] = "present.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']
  # Present simple - auxiliary do (They do)
  # We need to make sure it is not a negation or a question
    elif ((vect_tags.iloc[0]['Tag1'] in ["VDZ", "VDB"]) and ((not('Verb2' in c_names) or (vect_tags.iloc[0]['Verb2']=="")) or (('Verb2' in c_names) and (not(vect_tags.iloc[0]['Tag2'] in ["VVI", "VHI", "VDI"]) or not( (int(vect_tags.iloc[0]['Position2'])<int(vect_tags.iloc[0]['Position1'])+4) ))))): 
        vect_tenses['Tense'] = "present.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']
  # Present simple - auxiliary do in a negation or a question 
  #(They do not write/ Do they write)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VDZ", "VDB"]) and ('Verb2' in c_names) and (vect_tags.iloc[0]['Tag2'] in ["VVI", "VHI", "VDI"]) and (int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+4)):
        vect_tenses['Tense'] = "present.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  # Present simple - "is/are worth + V-ing"
  # (It is worth looking)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB", "VBZ"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["worth"]) and ('Verb2' in c_names) and (vect_tags.iloc[0]['Tag2'] in ["VDG", "VHG", "VVG", "VBG"]) and (int(vect_tags.iloc[0]['Position2']) == int(vect_tags.iloc[0]['Position1'])+2)):
        vect_tenses['Tense'] = "present.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']
  # Present simple - "there is + V-ing"
  # (there is no going back)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB", "VBZ"]) and (int(vect_tags.iloc[0]['Position1']) > 1) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])-1) in ["there"]) and ('Verb2' in c_names) and (vect_tags.iloc[0]['Tag2'] in ["VDG", "VHG", "VVG", "VBG"]) and (int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+3)):
        vect_tenses['Tense'] = "present.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']
  # Present simple - auxiliary be (They are)
  # We need to make sure it is NOT a present progressive or 
  #it is in passive voice
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB", "VBZ"]) and (not('Verb2' in c_names) or (('Verb2' in c_names) and (not(vect_tags.iloc[0]['Tag2'] in ["VDG", "VHG", "VBG", "VVG", "VVN", "VDN"]) or not((int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+3) ))))):
        vect_tenses['Tense'] = "present.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']
  # Present simple - auxiliary have + got (They have got a solution to the problem)
  # Very rarely such an expression will be in present perfect
    elif ((vect_tags.iloc[0]['Tag1'] in ["VHB", "VHZ"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["got"])):
        vect_tenses['Tense'] = "present.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], 'got']," ")
        vect_tenses['Position'] = int(vect_tags.iloc[0]['Position1']) + 1
  # Present simple - auxiliary have (They have)
  # We need to make sure it is not a present perfect or 
  #a present perfect progressive
    elif ((vect_tags.iloc[0]['Tag1'] in ["VHB", "VHZ"]) and (not('Verb2' in c_names) or (('Verb2' in c_names) and (not(vect_tags.iloc[0]['Tag2'] in ["VDN", "VBN","VHN", "VVN"]) or not((int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+4) ))))):
        vect_tenses['Tense'] = "present.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']
  ### Passive voice
  
  # Present simple (It is written)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB", "VBZ"]) and ('Verb2' in c_names) and (vect_tags.iloc[0]['Tag2'] in ["VVN", "VDN"]) and (int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+4)):
        vect_tenses['Tense'] = "present.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']]," ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  
  ### notnotnot
  ### notnotnot We start with dealing with tenses formed using "going to" before tackling the present progressive
  ### To avoid misdetecting as present progressive notnotnot
  ### notnotnot
  
  ################### Future simple using "going to" ###################
  
  ### Active voice
  
  # Future simple - lexical verbs (They are going to write/do)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB","VBZ"]) and (vect_tags.iloc[0]['Verb2'] in ["going", "gon"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position2'])+1) in ["to", "na"]) and (vect_tags.iloc[0]['Tag3'] in ["VVI", "VDI"]) and (int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4)):
        vect_tenses['Tense'] = "future.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], "going to", vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']  
  # Future simple - auxiliary be (They are going to be): 
  # We need to make sure it is NOT a future progressive or 
  #it is in passive voice
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB","VBZ"]) and (vect_tags.iloc[0]['Verb2'] in ["going", "gon"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position2'])+1) in ["to" ,"na"]) and (vect_tags.iloc[0]['Tag3'] in ["VBI"]) and (( not('Verb4' in c_names) or (vect_tags.iloc[0]['Verb4']=="")) or (('Verb4' in c_names) and (not(vect_tags.iloc[0]['Tag4'] in ["VDG", "VHG", "VVG", "VVN", "VDN"]) or not((int(vect_tags.iloc[0]['Position4']) < int(vect_tags.iloc[0]['Position3'])+4) ))))):
        vect_tenses['Tense'] = "future.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], "going to", vect_tags.iloc[0]['Verb3']]," ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']
  
  # Future simple - auxiliary have (They are going to have)
  # We need to make sure it is not a future perfect or 
  #a future perfect progressive
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB","VBZ"]) and (vect_tags.iloc[0]['Verb2'] in ["going", "gon"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position2'])+1) in ["to", "na"]) and (vect_tags.iloc[0]['Tag3'] in ["VHI"]) and ((not('Verb4' in c_names) or (vect_tags.iloc[0]['Verb4']=="")) or (('Verb4' in c_names) and (not(vect_tags.iloc[0]['Tag4'] in ["VDN", "VBN","VHN", "VVN"]) or not((int(vect_tags.iloc[0]['Position4']) < int(vect_tags.iloc[0]['Position3'])+4) ))))):
        vect_tenses['Tense'] = "future.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], "going to", vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']  
  ### Passive voice
  
  # Future simple (It is going to be written)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB","VBZ"]) and (vect_tags.iloc[0]['Verb2'] in ["going", "gon"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position2'])+1) in ["to", "na"]) and (vect_tags.iloc[0]['Tag3'] in ["VBI"]) and (vect_tags.iloc[0]['Tag4'] in ["VVN", "VDN"]) and (int(vect_tags.iloc[0]['Position4']) < int(vect_tags.iloc[0]['Position3'])+4)):
        vect_tenses['Tense'] = "future.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb4']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], "going to", vect_tags.iloc[0]['Verb3'], vect_tags.iloc[0]['Verb4']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position4']
  
  ################### Future progressive using "going to" ###################
  
  ### Active voice
  
  # Future progressive (They are going to be writing)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB","VBZ"]) and (vect_tags.iloc[0]['Verb2'] in ["going", "gon"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position2'])+1) in ["to", "na"]) and (vect_tags.iloc[0]['Tag3'] in ["VBI"]) and (vect_tags.iloc[0]['Tag4'] in ["VDG", "VHG", "VVG"]) and (int(vect_tags.iloc[0]['Position4']) < int(vect_tags.iloc[0]['Position3'])+4)):
        vect_tenses['Tense'] = "future.prog"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb4']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], "going to", vect_tags.iloc[0]['Verb3'], vect_tags.iloc[0]['Verb4']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position4']
  
  ### Passive voice: N/A
  
  ################### Future perfect using "going to" ###################
  
  ### Active voice
  
  # Future simple - auxiliary have (They are going to have written)
  # We need to make sure it is a future perfect progressive
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB","VBZ"]) and (vect_tags.iloc[0]['Verb2'] in ["going", "gon"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position2'])+1) in ["to", "na"]) and (vect_tags.iloc[0]['Tag3'] in ["VHI"]) and ((vect_tags.iloc[0]['Tag4'] in ["VDN","VHN", "VVN"]) or ((vect_tags.iloc[0]['Tag4'] in ["VBN"]) and ((not('Verb5' in c_names) or (vect_tags.iloc[0]['Verb5']=="")) or (('Verb5' in c_names) and not(vect_tags.iloc[0]['Tag5'] in ["VDG", "VHG", "VVG", "VVN", "VDN"] and not((int(vect_tags.iloc[0]['Position5']) < int(vect_tags.iloc[0]['Position4'])+4) ))))))):
        vect_tenses['Tense'] = "future.perf"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb4']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], "going to", vect_tags.iloc[0]['Verb3'], vect_tags.iloc[0]['Verb4']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position4']
  
  ### Passive voice
  
  # Future perfect (It is going to have been completed)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB","VBZ"]) and (vect_tags.iloc[0]['Verb2'] in ["going", "gon"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position2'])+1) in ["to", "na"]) and (vect_tags.iloc[0]['Tag3'] in ["VHI"]) and (vect_tags.iloc[0]['Tag4'] in ["VBN"]) and (vect_tags.iloc[0]['Tag5'] in ["VVN", "VDN"])):
        vect_tenses['Tense'] = "future.perf"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb5']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], "going to", vect_tags.iloc[0]['Verb3'], vect_tags.iloc[0]['Verb4'], vect_tags.iloc[0]['Verb5']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position5']
  
  ################### Future perfect progressive using "going to" ###################
  
  ### Active voice
  
  # Future perfect progressive (They are going to have been writing)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB","VBZ"]) and (vect_tags.iloc[0]['Verb2'] in ["going", "gon"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position2'])+1) in ["to", "na"]) and (vect_tags.iloc[0]['Tag3'] in ["VHI"]) and (vect_tags.iloc[0]['Tag4'] in ["VBN"]) and (vect_tags.iloc[0]['Tag5'] in ["VDG", "VHG", "VVG"])):
        vect_tenses['Tense'] = "future.perf.prog"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb5']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], "going to", vect_tags.iloc[0]['Verb3'], vect_tags.iloc[0]['Verb4'], vect_tags.iloc[0]['Verb5']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position5']
  
  ### Passive voice: N/A
  
  ################### Present progressive ###################
  
  ### Active voice
  
  # Present progressive (They are writing)
  # We need to make sure it is NOT in passive voice
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB", "VBZ"]) and ('Verb2' in c_names) and (int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+3) and ((vect_tags.iloc[0]['Tag2'] in ["VDG", "VHG", "VVG"]) or ((vect_tags.iloc[0]['Tag2'] in ["VBG"]) and (not('Verb3' in c_names) or (('Verb3' in c_names) and not(vect_tags.iloc[0]['Tag3'] in ["VVN", "VDN"])))))):
        vect_tenses['Tense'] = "present.prog"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  ### Passive voice
  
  # Present progressive (It is being written)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBB", "VBZ"])and (vect_tags.iloc[0]['Tag2'] in ["VBG"]) and (vect_tags.iloc[0]['Tag3'] in ["VVN", "VDN"])):
        vect_tenses['Tense'] = "present.prog"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']

  ################### Present perfect ###################
  
  ### Active voice
  
  # Present simple - auxiliary have (They have written)
  # We need to make sure it is a present perfect progressive or in passive mode
    elif ((vect_tags.iloc[0]['Tag1'] in ["VHB", "VHZ"]) and ('Verb2' in c_names) and ((vect_tags.iloc[0]['Tag2'] in ["VDN","VHN", "VVN"]) or ((vect_tags.iloc[0]['Tag2'] in ["VBN"]) and ((not('Verb3' in c_names) or (vect_tags.iloc[0]['Verb3']=="")) or (('Verb3' in c_names) and not(vect_tags.iloc[0]['Tag3'] in ["VDG", "VHG", "VVG", "VVN", "VDN"]) or not((int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4) )))))):
        vect_tenses['Tense'] = "present.perf"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  
  ### Passive voice
  
  # Present perfect (They have been given)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VHZ","VHB"]) and (vect_tags.iloc[0]['Tag2'] in ["VBN"]) and (vect_tags.iloc[0]['Tag3'] in ["VVN", "VDN"])):
        vect_tenses['Tense'] = "present.perf"
        vect_tenses['MainVerb'] = vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm'] = paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']

  ################### Present perfect progressive ###################
  
  ### Active voice
  
  # Present perfect progressive (They have been writing)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VHZ","VHB"]) and (vect_tags.iloc[0]['Tag2'] in ["VBN"]) and (vect_tags.iloc[0]['Tag3'] in ["VDG", "VHG", "VVG"])):
        vect_tenses['Tense'] = "present.perf.prog"
        vect_tenses['MainVerb'] = vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']
  
  ### Passive voice: N/A
  
  ################### Past simple ###################
  
  ### Active voice
  
  # Past simple - lexical verbs  (They wrote)
    elif vect_tags.iloc[0]['Tag1'] in ["VVD"]:
        vect_tenses['Tense'] = "past.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']

    elif ((vect_tags.iloc[0]['Tag1'] in ["VDD"]) and (not('Verb2' in c_names) or (('Verb2' in c_names) and (not(vect_tags.iloc[0]['Tag2'] in ["VVI", "VHI", "VDI"]) or not((int(vect_tags.iloc[0]['Position2'])<int(vect_tags.iloc[0]['Position1'])+4) ))))): 
        vect_tenses['Tense'] = "past.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']

  # Past simple - auxiliary do in a negation or a question 
  #(They did not write/ Did they write)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VDD"]) and ('Verb2' in c_names) and (vect_tags.iloc[0]['Tag2'] in ["VVI", "VHI", "VDI"]) and (int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+4)): 
        vect_tenses['Tense'] = "past.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  # Past simple - "was/were worth + V-ing"
  # (It was worth investing)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBD"]) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])+1) in ["worth"]) and ('Verb2' in c_names) and (vect_tags.iloc[0]['Tag2'] in ["VDG", "VHG", "VVG", "VBG"]) and (int(vect_tags.iloc[0]['Position2']) == int(vect_tags.iloc[0]['Position1'])+2)):
        vect_tenses['Tense'] = "past.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']
  # Past simple - "there was + V-ing"
  # (there was no going back)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBD"]) and (int(vect_tags.iloc[0]['Position1']) > 1) and (word(vect_tags.iloc[0]['Sentence'], int(vect_tags.iloc[0]['Position1'])-1) in ["there"]) and ('Verb2' in c_names) and (vect_tags.iloc[0]['Tag2'] in ["VDG", "VHG", "VVG", "VBG"]) and (int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+3)):
        vect_tenses['Tense'] = "past.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']
  # Past simple - auxiliary be (They were)
  # We need to make sure it is NOT a past progressive or 
  # it is in passive voice
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBD"]) and (not('Verb2' in c_names) or (('Verb2' in c_names) and (not(vect_tags.iloc[0]['Tag2'] in ["VDG", "VHG", "VBG", "VVG", "VVN", "VDN"]) or not((int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+4) ))))):
        vect_tenses['Tense'] = "past.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']
  # Past simple - auxiliary have (They had)
  # We need to make sure it is not a past perfect or 
  #a past perfect progressive
    elif ((vect_tags.iloc[0]['Tag1'] in ["VHD"]) and (not('Verb2' in c_names) or (('Verb2' in c_names) and (not(vect_tags.iloc[0]['Tag2'] in ["VDN", "VBN","VHN", "VVN"]) or not((int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+4) ))))):
        vect_tenses['Tense'] = "past.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb1']
        vect_tenses['VerbForm']= vect_tags.iloc[0]['Verb1']
        vect_tenses['Position'] = vect_tags.iloc[0]['Position1']

  ### Passive voice
  
  # Past simple (It was written)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBD"]) and ('Verb2' in c_names) and (vect_tags.iloc[0]['Tag2'] in ["VVN", "VDN"]) and (int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+4)):
        vect_tenses['Tense'] = "past.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  
  ################### Past progressive ###################
  
  ### Active voice
  
  # Past progressive (They were writing)
  # We need to make sure it is NOT in passive voice
    elif (vect_tags.iloc[0]['Tag1'] in ["VBD"]) and ('Verb2' in c_names) and ((vect_tags.iloc[0]['Tag2'] in ["VDG", "VHG", "VVG"]) or ((vect_tags.iloc[0]['Tag2'] in ["VBG"]) and ((not('Verb3' in c_names) or (vect_tags.iloc[0]['Verb3']=="")) or (('Verb3' in c_names) and not(vect_tags.iloc[0]['Tag3'] in ["VVN", "VDN"]) or not((int(vect_tags.iloc[0]['Position2']) < int(vect_tags.iloc[0]['Position1'])+4) ))))):
        vect_tenses['Tense'] = "past.prog"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  
  ### Passive voice
  
  # Past progressive (It was being written)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VBD"]) and(vect_tags.iloc[0]['Tag2'] in ["VBG"]) and (vect_tags.iloc[0]['Tag3'] in ["VVN", "VDN"])):
        vect_tenses['Tense'] = "past.prog"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']
  ################### Past perfect ###################
  
  ### Active voice
  
  # Past simple - auxiliary have (They had written)
  # We need to make sure it is not a past perfect progressive
    elif ((vect_tags.iloc[0]['Tag1'] in ["VHD"]) and ('Verb2' in c_names) and ((vect_tags.iloc[0]['Tag2'] in ["VDN","VHN", "VVN"]) or ((vect_tags.iloc[0]['Tag2'] in ["VBN"]) and (( not('Verb3' in c_names) or (vect_tags.iloc[0]['Verb3']=="")) or (('Verb3' in c_names) and not(vect_tags.iloc[0]['Tag3'] in ["VDG", "VHG", "VVG", "VVN", "VDN"]) or not((int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4)  )))))):
        vect_tenses['Tense'] = "past.perf"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  ### Passive voice
  
  # Past perfect (They had been given)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VHD"]) and (vect_tags.iloc[0]['Tag2'] in ["VBN"]) and (vect_tags.iloc[0]['Tag3'] in ["VVN", "VDN"])):
        vect_tenses['Tense'] = "past.perf"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']
  ################### Past perfect progressive ###################
  
  ### Active voice
  
  # Past perfect progressive (They had been writing)
    elif ((vect_tags.iloc[0]['Tag1'] in ["VHD"]) and (vect_tags.iloc[0]['Tag2'] in ["VBN"]) and (vect_tags.iloc[0]['Tag3'] in ["VDG", "VHG", "VVG"])):
        vect_tenses['Tense'] = "past.perf.prog"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']

  ### Passive voice: N/A
  
  ################### Future simple using "will" ###################
  
  ### Active voice
  
  # Future simple - lexical verbs  (They will write/do)
    elif ((vect_tags.iloc[0]['Verb1'] in ["will"]) and ('Verb2' in c_names) and (vect_tags.iloc[0]['Tag2'] in ["VVI", "VDI"])):
        vect_tenses['Tense'] = "future.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  # Future simple - auxiliary be (They will be)
  # We need to make sure it is NOT a future progressive or 
  #it is in passive voice
    elif ((vect_tags.iloc[0]['Verb1'] in ["will"]) and ('Verb2' in c_names) and (vect_tags.iloc[0]['Tag2'] in ["VBI"]) and (( not('Verb3' in c_names) or (vect_tags.iloc[0]['Verb3']=="") ) or (('Verb3' in c_names) and (not(vect_tags.iloc[0]['Tag3'] in ["VDG", "VHG", "VVG", "VVN", "VDN"]) or not((int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4) ))))):
        vect_tenses['Tense'] = "future.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  # Future simple - auxiliary have (They will have)
  # We need to make sure it is not a future perfect or 
  # a future perfect progressive
    elif ((vect_tags.iloc[0]['Verb1'] in ["will"]) and ('Verb2' in c_names) and (vect_tags.iloc[0]['Tag2'] in ["VHI"]) and ((not('Verb3' in c_names) or (vect_tags.iloc[0]['Verb3']=="")) or (('Verb3' in c_names) and (not(vect_tags.iloc[0]['Tag3'] in ["VDN", "VBN","VHN", "VVN"]) or not((int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4) ))))):
        vect_tenses['Tense'] = "future.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb2']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position2']
  ### Passive voice
  
  # Future simple (It will be written)
    elif ((vect_tags.iloc[0]['Verb1'] in ["will"]) and (vect_tags.iloc[0]['Tag2'] in ["VBI"]) and (vect_tags.iloc[0]['Tag3'] in ["VVN", "VDN"]) and (int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4)):
        vect_tenses['Tense'] = "future.simple"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']
  
  ################### Future progressive using "will" ###################
  
  ### Active voice
  
  # Future progressive (They will be writing)
    elif ((vect_tags.iloc[0]['Verb1'] in ["will"]) and (vect_tags.iloc[0]['Tag2'] in ["VBI"]) and (vect_tags.iloc[0]['Tag3'] in ["VDG", "VHG", "VVG"]) and (int(vect_tags.iloc[0]['Position3']) < int(vect_tags.iloc[0]['Position2'])+4)):
        vect_tenses['Tense'] = "future.prog"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']

  ### Passive voice: N/A
  
  ################### Future perfect using "will" ###################
  
  ### Active voice
  
  # Future perfect - auxiliary have (They will have written)
  # We need to make sure it is a future perfect progressive
    elif ((vect_tags.iloc[0]['Verb1'] in ["will"]) and (vect_tags.iloc[0]['Tag2'] in ["VHI"]) and ((vect_tags.iloc[0]['Tag3'] in ["VDN","VHN", "VVN"]) or ((vect_tags.iloc[0]['Tag3'] in ["VBN"]) and ((not('Verb4' in c_names) or (vect_tags.iloc[0]['Verb4']=="")) or (('Verb4' in c_names) and (not(vect_tags.iloc[0]['Tag4'] in ["VDG", "VHG", "VVG", "VVN", "VDN"]) or not((int(vect_tags.iloc[0]['Position4']) < int(vect_tags.iloc[0]['Position3'])+4) ))))))):
        vect_tenses['Tense'] = "future.perf"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb3']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position3']
  
  ### Passive voice
  
  # Future perfect (They will have been given)
    elif ((vect_tags.iloc[0]['Verb1'] in ["will"]) and (vect_tags.iloc[0]['Tag2'] in ["VHI"]) and  (vect_tags.iloc[0]['Tag3'] in ["VBN"]) and (vect_tags.iloc[0]['Tag4'] in ["VVN", "VDN"])):
        vect_tenses['Tense'] = "future.perf"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb4']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3'], vect_tags.iloc[0]['Verb4']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position4']
  
  ################### Future perfect progressive using "will" ###################
  
  ### Active voice
  
  # Future perfect progressive (They will have been writing)
    elif ((vect_tags.iloc[0]['Verb1'] in ["will"]) and (vect_tags.iloc[0]['Tag2'] in ["VHI"]) and (vect_tags.iloc[0]['Tag3'] in ["VBN"]) and (vect_tags.iloc[0]['Tag4'] in ["VDG", "VHG", "VVG"])):
        vect_tenses['Tense'] = "future.perf.prog"
        vect_tenses['MainVerb']= vect_tags.iloc[0]['Verb4']
        vect_tenses['VerbForm']= paste([vect_tags.iloc[0]['Verb1'], vect_tags.iloc[0]['Verb2'], vect_tags.iloc[0]['Verb3'], vect_tags.iloc[0]['Verb4']], " ")
        vect_tenses['Position'] = vect_tags.iloc[0]['Position4']  
  ### Passive voice: N/A
    return(vect_tenses)
  
 