# open csv list with withdrawn participation IDs
with open("csvfilename.csv") as f:
    list2 = [row.split(',')[0] for row in f]

#select = 'SELECT * FROM SESSION_INFO WHERE participation_id = (%s)'
update = "UPDATE SESSION_INFO SET consent = 0 WHERE participation_id = (%s)"
list2 = list2[1::]
for i in range(len(list2)):
    participation_id = list2[i]
    db.execute(update,(participation_id,),0)