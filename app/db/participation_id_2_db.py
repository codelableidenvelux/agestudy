# Insert new IDs
with open('static/csv/p_ids_first.csv') as f:
    read_data = f.readlines()

for i in read_data:
    insert = "INSERT INTO participation_id (p_id) VALUES (%s)"
    p_id = i.strip()
    db.execute(insert, (p_id, ), 0)
# select an ID and remove it
select = "SELECT * FROM participation_id order by p_id desc limit 1"
delete = """DELETE FROM participation_id WHERE p_id = ANY(SELECT * FROM participation_id order by p_id desc limit 1) RETURNING *"""
db.execute(delete, ("",), 2)
# check results
select = "SELECT * FROM participation_id"
db.execute(select, ("",), 1)
