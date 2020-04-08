import pg8000

user = input("Username: ")
secret = input("Password: ")
db = pg8000.connect(user=user, password = secret, host = "bartik.mines.edu", database='csci403')
print(db)

cursor = db.cursor()

cursor.execute("SELECT course_id FROM mines_cs_courses")

results = cursor.fetchall()

for row in results:
    string = row
    print(string)