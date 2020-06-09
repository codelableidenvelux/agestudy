# Task switching
Monsell, S. (2003). Task switching. Trends in Cognitive Sciences, 7, 134-140.
Wasylyshyn et al (2011) Aging and task switching: A meta analysis, Psychology and aging 26(1) 15-20 

# Settings
- Do not to show a welcome screen at all
- Do not to show an end screen at all
- Survey name in header: Wisseltaak or Task Switching
- Do not show a progress report
- Exclude mobile phone and tablet users
- Input = user_id

All other settings are default.

# Data
Space seperated
- (1). BLOCKNUMBER (as in 1 2 3 etc)
- (2). BLOCKNAME (as in training, realColor, realshape, realmixed)
- (3). Image shown according to the Table below, occupyin till col. (6)
- (7). RT in ms
- (8). Key status (1== correct, 2 == incorrect, 3 == too slow)
- (9). Start of exp marker 


Table 
table colortasktable
 > "color congruent   1 left " colorcue circle_yellow     1
 > "color incongruent 2 left " colorcue rectangle_yellow  1
 > "color incongruent 2 right" colorcue circle_blue       2
 > "color congruent   1 right" colorcue rectangle_blue    2

table shapetasktable
  > "shape congruent   1 left " shapecue circle_yellow     1
  > "shape incongruent 2 right" shapecue rectangle_yellow  2
  > "shape incongruent 2 left " shapecue circle_blue       1
  > "shape congruent   1 right" shapecue rectangle_blue    2
