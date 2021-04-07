from flask import jsonify
import csv
from edf_manager import get_file_start
from datetime import datetime, timedelta


def get_annotations(session):
    start_time = get_file_start(session)
    parsed = parse_annotation_file(session)
    chart_max = int(session['data_offset']) * int(session['selected_count'])
    chart_min = int(session['data_offset']) * -1
    return map_annotations_to_time(parsed, start_time, chart_max, chart_min)


# parse csv file into list of annoations
def parse_annotation_file(session):
    filename = session['annotation_file']
    with open(filename, 'r') as csvfile:
        hdl = csv.reader(csvfile)
        next(csvfile)
        lst = [{'Onset': rows[0], 'Duration': rows[1], 'Annotation': rows[2]} for rows in hdl]

    session['annotations'] = lst
    return lst


def map_annotations_to_time(annotations, start_time, chart_max, chart_min):
    mapping = []
    for annotation in annotations:
        info = {}
        start = start_time + timedelta(milliseconds=int(annotation['Onset']))
        end = start + timedelta(milliseconds=int(annotation['Duration']))

        info['start'] = str(start.time())
        info['end'] = str(end.time())
        info['label'] = annotation['Annotation']
        mapping.append(info)

    return jsonify(annotations=mapping,
                   chart_max=chart_max,
                   chart_min=chart_min)


def get_annotation_by_offset(session):
    parsed = parse_annotation_file(session)
    return jsonify(annotations=parsed)

