from pymongo import MongoClient
import io, sys

client = MongoClient('mongodb://localhost/kramster')
db = client.kramster
docs = db.exams

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
lines = []
for line in input_stream:
    lines.append(line.strip())

doc = {}
doc["school"] = lines[0]
doc["course"] = lines[1]
doc["name"] = lines[2]
doc["questions"] = []

for line in lines[3:]:
    q_array = line.split("§§")
    q_object = {}

    q_object["question"] = q_array[0].strip()
    q_object["answers"] = list(map(lambda x: int(x.strip()), q_array[1].strip().split(" ")))
    q_object["options"] = []

    for i in range(2, len(q_array)):
        q_object["options"].append(q_array[i].strip())

    doc["questions"].append(q_object)

id = docs.insert_one(doc)
print("Document inserted.")
