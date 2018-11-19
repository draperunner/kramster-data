# coding=utf-8
import re
from pymongo import MongoClient
from pymongo import ReturnDocument

def get_answers(line):
    ans = line.strip()
    match = re.search("Riktig svar:\s(.)", ans)
    answer = match.group(1)
    return [ord(answer.strip().lower()) - 97]


def insert(exam_file):
    with open(exam_file, encoding="utf-8") as file:
        lines = file.readlines()

    exam = {"school": lines[0].strip(), "course": lines[1].strip(), "name": lines[2].strip(), "questions": []}
    if lines[3].strip() == "MC" or lines[3].strip() == "TF":
        exam["mode"] = lines[3].strip()

    i = 4
    while i < len(lines) - 1:  # lines[i] should be "Q" or empty lines
        if lines[i].strip() == "":
            i += 1
            continue

        q_object = {}

        # Question
        question = re.sub('^[\d]{1,2}\)\s*', '', lines[i].strip())
        q_object["question"] = question

        i += 1

        # Options
        options = []
        for j in range(4):
            option = re.sub("^[A-D]\.\s+", '', lines[i].strip())
            options.append(option)
            i += 1
        q_object["options"] = options

        q_object["answers"] = get_answers(lines[i].strip())

        question_insert_result = db.questions.insert_one(q_object)
        exam["questions"].append(question_insert_result.inserted_id)

        i += 1

    exam_insert_result = db.exams.insert_one(exam)
    print("exam inserted.")
    print("db.exams.findOne({_id: ObjectId(\"" + str(exam_insert_result.inserted_id) + "\")})")


def delete(exam_file):
    with open(exam_file, encoding="utf-8") as file:
        school = file.readline().strip()
        course = file.readline().strip()
        exam = file.readline().strip()

    mongo_exam = db.exams.find_one({'school': school, 'course': course, 'name': exam})

    if mongo_exam is None:
        print("No exam found")
        return

    mongo_questions = mongo_exam["questions"]

    for qid in mongo_questions:
        db.questions.delete_one({'_id': qid})

    db.exams.delete_one(mongo_exam)
    print("exam removed.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Kramster inserter')

    parser.add_argument('file', nargs='+', help='files to insert or remove')
    parser.add_argument('-d', '--delete', action='store_true', help='delete exam')
    parser.add_argument('-r', '--reinsert', action='store_true', help='delete and insert exam')
    parser.add_argument('-e', '--explanation', action='store_true', help='add explanation to existing questions')

    parser.add_argument('--db', default='kramster', help='database to use (default: kramster)')

    # Logger verbosity parameters
    # parser.add_argument('-v', '--verbose', action='count', default=0, help='verbosity level, repeat to increase')
    # parser.add_argument('-q', '--quiet', action='store_true', help='no print to console')

    args = parser.parse_args()

    client = MongoClient()
    db = client[args.db]

    for f in args.file:
        if args.explanation:
            add_explanation(f)
            continue
        if args.delete or args.reinsert:
            delete(f)
        if not args.delete:
            insert(f)
