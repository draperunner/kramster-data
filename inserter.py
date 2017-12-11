from pymongo import MongoClient
from pymongo import ReturnDocument


def get_answers(line):
    ans = line.strip().split()

    if len(ans) < 1:
        print("No answers given!")
        return ans

    if ans[0].isdigit():
        return list(map(lambda x: int(x.strip()), ans))
    else:
        return list(map(lambda x: ord(x.strip().lower()) - 97, ans))


def insert(exam_file):
    with open(exam_file, encoding="utf-8") as file:
        lines = file.readlines()

    exam = {"school": lines[0].strip(), "course": lines[1].strip(), "name": lines[2].strip(), "questions": []}
    if lines[3].strip() == "MC" or lines[3].strip() == "TF":
        exam["mode"] = lines[3].strip()

    i = 4
    while i < len(lines):  # lines[i] should be "Q" or empty lines

        if lines[i].strip() == "":
            i += 1
            continue

        q_object = {}

        i += 1

        # Correct answer(s)
        q_object["answers"] = get_answers(lines[i])

        i += 1

        # Question
        question = ""
        while i < len(lines) and lines[i].strip() != "O":
            question += lines[i]
            i += 1
        q_object["question"] = question.strip()

        # Options
        options = []
        while i < len(lines) and lines[i].strip() != "Q" and lines[i].strip() != "EXPLANATION":
            i += 1
            option = ""
            while i < len(lines) and lines[i].strip() != "O" and lines[i].strip() != "Q" and lines[
                i].strip() != "EXPLANATION":
                option += lines[i]
                i += 1
            options.append(option.strip())
        q_object["options"] = options

        if i < len(lines) and lines[i].strip() == "EXPLANATION":
            i += 1
            explanation = ""
            while i < len(lines) and lines[i].strip() != "Q":
                explanation += lines[i]
                i += 1
            q_object["explanation"] = explanation.strip()

        question_insert_result = db.questions.insert_one(q_object)
        exam["questions"].append(question_insert_result.inserted_id)

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


def add_explanation(exam_file):
    with open(exam_file, encoding="utf-8") as file:
        lines = file.readlines()

    exam = {"school": lines[0].strip(), "course": lines[1].strip(), "name": lines[2].strip(), "questions": []}
    if lines[3].strip() == "MC" or lines[3].strip() == "TF":
        exam["mode"] = lines[3].strip()

    i = 4
    while i < len(lines):  # lines[i] should be "Q" or empty lines

        if lines[i].strip() == "":
            i += 1
            continue

        q_object = {}

        i += 1

        # Correct answer(s)
        q_object["answers"] = get_answers(lines[i])

        i += 1

        # Question
        question = ""
        while i < len(lines) and lines[i].strip() != "O":
            question += lines[i]
            i += 1
        q_object["question"] = question.strip()

        # Options
        options = []
        while i < len(lines) and lines[i].strip() != "Q" and lines[i].strip() != "EXPLANATION":
            i += 1
            option = ""
            while i < len(lines) and lines[i].strip() != "O" and lines[i].strip() != "Q" and lines[
                i].strip() != "EXPLANATION":
                option += lines[i]
                i += 1
            options.append(option.strip().replace("\n", " "))
        q_object["options"] = options

        explanation = ""
        if i < len(lines) and lines[i].strip() == "EXPLANATION":
            i += 1
            while i < len(lines) and lines[i].strip() != "Q":
                explanation += lines[i]
                i += 1
            q_object["explanation"] = explanation.strip().replace("\n", " ")

        if explanation != "":
            doc = db.questions.find_one_and_update({"question": q_object["question"]}, {'$set': {'explanation': explanation}},
                                             return_document=ReturnDocument.AFTER)
            print(doc["_id"])
        else:
            print("No explanation")

    print("exam updated.")


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
