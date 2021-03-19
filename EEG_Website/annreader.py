from flask import jsonify
import csv

# parse csv file into json object
def parse_annotation_file(session):
    filename = session['annotation_file']
    lst = []
    with open(filename, 'r') as csvfile:
        hdl = csv.reader(csvfile)
        for rows in hdl:
            lst.append(rows)

    ann_dict = {'Onset': [i[0] for i in lst[1:]], 'Duration': [i[1] for i in lst[1:]],
                'Annotation': [i[2] for i in lst[1:]]}
    session = session.update(ann_dict)

    return jsonify(Onset = [i[0] for i in lst[1:]],
                   Duration = [i[1] for i in lst[1:]],
                   Annotation = [i[2] for i in lst[1:]])



