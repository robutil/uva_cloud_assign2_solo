import os
import tempfile
from functools import reduce
from typing import Union, Tuple

from tinydb import TinyDB, Query

from swagger_server.models import Student

db_dir_path = tempfile.gettempdir()
db_file_path = os.path.join(db_dir_path, "students.json")
student_db = TinyDB(db_file_path)


def add_student(student):
    if not student.last_name or not student.first_name:
        return 'Missing student (last) name', 405

    queries = []
    query = Query()
    queries.append(query.first_name == student.first_name)
    queries.append(query.last_name == student.last_name)

    query = reduce(lambda a, b: a & b, queries)
    res = student_db.search(query)
    if res:
        return 'already exists', 409

    doc_id = student_db.insert(student.to_dict())
    student.student_id = doc_id
    return student.student_id


def get_student_by_id(student_id, subject):
    student = student_db.get(doc_id=int(student_id))
    if not student:
        return None

    student = Student.from_dict(student)
    if not subject:
        return student

    elif subject not in student.grades:
        return None

    return student


def delete_student(student_id):
    student = student_db.get(doc_id=int(student_id))
    if not student:
        return student
    student_db.remove(doc_ids=[int(student_id)])
    return student_id


def get_student_by_last_name(last_name: str) -> Union[Student, Tuple[str, int]]:
    """
    Returns a single student that matches the given last name. If no student is found
    this function returns a tuple containing an error message and error code, in that
    order.

    :param last_name: Last name of student to find
    :return: Student or error description
    """
    query = Query()
    query = reduce(lambda a, b: a & b, [query.last_name == last_name])
    res = student_db.search(query)

    if not res:
        return 'doesnt exist', 404

    return res[0]
