from shapely.geometry import *
from io import StringIO
import importlib
import codecs
import os
import sys
import re
import zipfile
import json
import sys
from evaluation import geometry
sys.path.append('./')


def print_help():
    sys.stdout.write(
        'Usage: python %s.py -g=<gtFile> -s=<submFile> [-o=<outputFolder> -p=<jsonParams>]' % sys.argv[0])
    sys.exit(2)


def load_zip_file_keys(file, fileNameRegExp=''):
    """
    Returns an array with the entries of the ZIP file that match with the regular expression.
    The key's are the names or the file or the capturing group definied in the fileNameRegExp
    """
    try:
        archive = zipfile.ZipFile(file, mode='r', allowZip64=True)
    except:
        raise Exception('Error loading the ZIP archive.')

    pairs = []

    for name in archive.namelist():
        addFile = True
        keyName = name
        if fileNameRegExp != "":
            m = re.match(fileNameRegExp, name)
            if m == None:
                addFile = False
            else:
                if len(m.groups()) > 0:
                    keyName = m.group(1)

        if addFile:
            pairs.append(keyName)

    return pairs


def load_zip_file(file, fileNameRegExp='', allEntries=False):
    """
    Returns an array with the contents (filtered by fileNameRegExp) of a ZIP file.
    The key's are the names or the file or the capturing group definied in the fileNameRegExp
    allEntries validates that all entries in the ZIP file pass the fileNameRegExp
    """
    try:
        archive = zipfile.ZipFile(file, mode='r', allowZip64=True)
    except:
        raise Exception('Error loading the ZIP archive')

    pairs = []
    for name in archive.namelist():
        addFile = True
        keyName = name
        
        if fileNameRegExp != "":
            m = re.match(fileNameRegExp, name)
            if m == None:
                addFile = False
            else:
                if len(m.groups()) > 0:
                    keyName = m.group(1)

        if addFile:
            pairs.append([keyName, archive.read(name)])
        else:
            if allEntries:
                raise Exception('ZIP entry not valid: %s' % name)

    return dict(pairs)


def decode_utf8(raw):
    """
    Returns a Unicode object on success, or None on failure
    """
    try:
        raw = codecs.decode(raw, 'utf-8', 'replace')
        # extracts BOM if exists
        raw = raw.encode('utf8')
        if raw.startswith(codecs.BOM_UTF8):
            raw = raw.replace(codecs.BOM_UTF8, '', 1)
        return raw.decode('utf-8')
    except:
        return None


def validate_lines_in_file_gt(fileName, file_contents, CRLF=True, LTRB=True, with_transcription=False, with_confidence=False, imWidth=0, imHeight=0):
    """
    This function validates that all lines of the file calling the Line validation function for each line
    """
    utf8File = decode_utf8(file_contents)
    if (utf8File is None):
        raise Exception("The file %s is not UTF-8" % fileName)

    lines = utf8File.split("\r\n" if CRLF else "\n")
    for line in lines:
        line = line.replace("\r", "").replace("\n", "")
        # if(line != ""):
        #     try:
        #         validate_tl_line_gt(
        #             line, LTRB, with_transcription, with_confidence, imWidth, imHeight)
        #     except Exception as e:
        #         raise Exception(("Line in sample not valid. Sample: %s Line: %s Error: %s" % (
        #             fileName, line, str(e))).encode('utf-8', 'replace'))


def validate_lines_in_file(fileName, file_contents, CRLF=True, LTRB=True, with_transcription=False, with_confidence=False, imWidth=0, imHeight=0):
    """
    This function validates that all lines of the file calling the Line validation function for each line
    """
    utf8File = decode_utf8(file_contents)
    if (utf8File is None):
        raise Exception("The file %s is not UTF-8" % fileName)

    lines = utf8File.split("\r\n" if CRLF else "\n")
    for line in lines:
        line = line.replace("\r", "").replace("\n", "")
        # if(line != ""):
        #     try:
        #         validate_tl_line(line, LTRB, with_transcription,
        #                          with_confidence, imWidth, imHeight)
        #     except Exception as e:
        #         raise Exception(("Line in sample not valid. Sample: %s Line: %s Error: %s" % (
        #             fileName, line, str(e))).encode('utf-8', 'replace'))


def validate_tl_line_gt(line, LTRB=True, with_transcription=True, with_confidence=True, imWidth=0, imHeight=0):
    """
    Validate the format of the line. If the line is not valid an exception will be raised.
    If maxWidth and maxHeight are specified, all points must be inside the imgage bounds.
    Posible values are:
    LTRB=True: xmin,ymin,xmax,ymax[,confidence][,transcription] 
    LTRB=False: x1,y1,x2,y2,x3,y3,x4,y4[,confidence][,transcription] 
    """
    get_tl_line_values_gt(line, LTRB, with_transcription,
                          with_confidence, imWidth, imHeight)


def validate_tl_line(line, LTRB=True, with_transcription=True, with_confidence=True, imWidth=0, imHeight=0):
    """
    Validate the format of the line. If the line is not valid an exception will be raised.
    If maxWidth and maxHeight are specified, all points must be inside the imgage bounds.
    Posible values are:
    LTRB=True: xmin,ymin,xmax,ymax[,confidence][,transcription] 
    LTRB=False: x1,y1,x2,y2,x3,y3,x4,y4[,confidence][,transcription] 
    """
    get_tl_line_values(line, LTRB, with_transcription,
                       with_confidence, imWidth, imHeight)


def get_tl_line_values_gt(line, LTRB=True, with_transcription=False, with_confidence=False, imWidth=0, imHeight=0):
    """
    Validate the format of the line. If the line is not valid an exception will be raised.
    If maxWidth and maxHeight are specified, all points must be inside the imgage bounds.
    Posible values are:
    LTRB=True: xmin,ymin,xmax,ymax[,confidence][,transcription] 
    LTRB=False: x1,y1,x2,y2,x3,y3,x4,y4[,confidence][,transcription] 
    Returns values from a textline. Points , [Confidences], [Transcriptions]
    """
    confidence = 0.0
    transcription = ""
    points = []

    if LTRB:
        # do not use
        raise Exception('Not implemented.')

    else:
        # if with_transcription and with_confidence:
        #     cors = line.split(',')
        #     assert(len(cors)%2 -2 == 0), 'num cors should be even.'
        #     try:
        #         points = [ float(ic) for ic in cors[:-2]]
        #     except Exception as e:
        #         raise(e)
        # elif with_confidence:
        #     cors = line.split(',')
        #     assert(len(cors)%2 -1 == 0), 'num cors should be even.'
        #     try:
        #         points = [ float(ic) for ic in cors[:-1]]
        #     except Exception as e:
        #         raise(e)
        # elif with_transcription:
        #     cors = line.split(',')
        #     assert(len(cors)%2 -1 == 0), 'num cors should be even.'
        #     try:
        #         points = [ float(ic) for ic in cors[:-1]]
        #     except Exception as e:
        #         raise(e)
        # else:
        #     cors = line.split(',')
        #     assert(len(cors)%2 == 0), 'num cors should be even.'
        #     try:
        #         points = [ float(ic) for ic in cors[:]]
        #     except Exception as e:
        #         raise(e)

        if with_transcription and with_confidence:
            raise('not implemented')
        elif with_confidence:
            raise('not implemented')
        elif with_transcription:
            ptr = line.strip().split(',####')
            cors = ptr[0].split(',')
            recs = ptr[1].strip()
            assert(len(cors) % 2 == 0), 'num cors should be even.'
            try:
                points = [float(ic) for ic in cors[:]]
            except Exception as e:
                raise(e)
        else:
            raise('not implemented')

        #points=geometry.choose_best_begin_point(points)
        validate_clockwise_points(points)
       

        if (imWidth > 0 and imHeight > 0):
            for ip in range(0, len(points), 2):
                validate_point_inside_bounds(
                    points[ip], points[ip+1], imWidth, imHeight)

    if with_confidence:
        try:
            confidence = 1.0
        except ValueError:
            raise Exception("Confidence value must be a float")

    if with_transcription:
        # posTranscription = numPoints + (2 if with_confidence else 1)
        # transcription = cors[-1].strip()
        transcription = recs
        m2 = re.match(r'^\s*\"(.*)\"\s*$', transcription)
        if m2 != None:  # Transcription with double quotes, we extract the value and replace escaped characters
            transcription = m2.group(1).replace(
                "\\\\", "\\").replace("\\\"", "\"")

    return points, confidence, transcription


def get_tl_line_values(line, LTRB=True, with_transcription=False, with_confidence=False, imWidth=0, imHeight=0):
    """
    Validate the format of the line. If the line is not valid an exception will be raised.
    If maxWidth and maxHeight are specified, all points must be inside the imgage bounds.
    Posible values are:
    LTRB=True: xmin,ymin,xmax,ymax[,confidence][,transcription] 
    LTRB=False: x1,y1,x2,y2,x3,y3,x4,y4[,confidence][,transcription] 
    Returns values from a textline. Points , [Confidences], [Transcriptions]
    """
    confidence = 0.0
    transcription = ""
    points = []

    if LTRB:
        # do not use
        raise Exception('Not implemented.')

    else:
        if with_transcription and with_confidence:
            raise('not implemented')
        elif with_confidence:
            raise('not implemented')
        elif with_transcription:
            ptr = line.strip().split(',####')
            cors = ptr[0].split(',')
            recs = ptr[1].strip()
            assert(len(cors) % 2 == 0), 'num cors should be even.'
            try:
                points = [float(ic) for ic in cors[:]]
            except Exception as e:
                raise(e)
        else:
            raise('not implemented')

        # print('det clock wise')
        #points=geometry.choose_best_begin_point(points)
        validate_clockwise_points(points)
        

        if (imWidth > 0 and imHeight > 0):
            for ip in range(0, len(points), 2):
                validate_point_inside_bounds(
                    points[ip], points[ip+1], imWidth, imHeight)

    if with_confidence:
        try:
            confidence = 1.0
        except ValueError:
            raise Exception("Confidence value must be a float")

    if with_transcription:
        # posTranscription = numPoints + (2 if with_confidence else 1)
        transcription = recs
        m2 = re.match(r'^\s*\"(.*)\"\s*$', transcription)
        if m2 != None:  # Transcription with double quotes, we extract the value and replace escaped characters
            transcription = m2.group(1).replace(
                "\\\\", "\\").replace("\\\"", "\"")

    return points, confidence, transcription


def validate_point_inside_bounds(x, y, imWidth, imHeight):
    if(x < 0 or x > imWidth):
        raise Exception("X value (%s) not valid. Image dimensions: (%s,%s)" % (
            xmin, imWidth, imHeight))
    if(y < 0 or y > imHeight):
        raise Exception("Y value (%s)  not valid. Image dimensions: (%s,%s) Sample: %s Line:%s" % (
            ymin, imWidth, imHeight))


def validate_clockwise_points(points):
    """
    Validates that the points that the 4 points that dlimite a polygon are in clockwise order.
    """

    # if len(points) != 8:
    #     raise Exception("Points list not valid." + str(len(points)))

    # point = [
    #             [int(points[0]) , int(points[1])],
    #             [int(points[2]) , int(points[3])],
    #             [int(points[4]) , int(points[5])],
    #             [int(points[6]) , int(points[7])]
    #         ]
    # edge = [
    #             ( point[1][0] - point[0][0])*( point[1][1] + point[0][1]),
    #             ( point[2][0] - point[1][0])*( point[2][1] + point[1][1]),
    #             ( point[3][0] - point[2][0])*( point[3][1] + point[2][1]),
    #             ( point[0][0] - point[3][0])*( point[0][1] + point[3][1])
    # ]

    # summatory = edge[0] + edge[1] + edge[2] + edge[3];
    # if summatory>0:
    #     raise Exception("Points are not clockwise. The coordinates of bounding quadrilaterals have to be given in clockwise order. Regarding the correct interpretation of 'clockwise' remember that the image coordinate system used is the standard one, with the image origin at the upper left, the X axis extending to the right and Y axis extending downwards.")
    pts = [(points[j], points[j+1]) for j in range(0, len(points), 2)]
    try:
        pdet = Polygon(pts)
    except:
        assert(0), ('not a valid polygon', pts)
    # The polygon should be valid.
    if not pdet.is_valid:
        assert(0), ('polygon has intersection sides', pts)
    pRing = LinearRing(pts)
    if pRing.is_ccw:
        assert(0),  ("Points are not clockwise. The coordinates of bounding quadrilaterals have to be given in clockwise order. Regarding the correct interpretation of 'clockwise' remember that the image coordinate system used is the standard one, with the image origin at the upper left, the X axis extending to the right and Y axis extending downwards.")


def get_tl_line_values_from_file_contents(content, CRLF=True, LTRB=True, with_transcription=False, with_confidence=False, imWidth=0, imHeight=0, sort_by_confidences=True):
    """
    Returns all points, confindences and transcriptions of a file in lists. Valid line formats:
    xmin,ymin,xmax,ymax,[confidence],[transcription]
    x1,y1,x2,y2,x3,y3,x4,y4,[confidence],[transcription]
    """
    points_list = []
    transcriptions_list = []
    confidences_list = []

    lines = content.split("\r\n" if CRLF else "\n")
    for line in lines:
        line = line.replace("\r", "").replace("\n", "")
        if(line != ""):
            points, confidence, transcription = get_tl_line_values_gt(
                line, LTRB, with_transcription, with_confidence, imWidth, imHeight)
            points_list.append(points)
            transcriptions_list.append(transcription)
            confidences_list.append(confidence)

    if with_confidence and len(confidences_list) > 0 and sort_by_confidences:
        import numpy as np
        sorted_ind = np.argsort(-np.array(confidences_list))
        confidences_list = [confidences_list[i] for i in sorted_ind]
        points_list = [points_list[i] for i in sorted_ind]
        transcriptions_list = [transcriptions_list[i] for i in sorted_ind]

    return points_list, confidences_list, transcriptions_list


def get_tl_line_values_from_file_contents_det(content, CRLF=True, LTRB=True, with_transcription=False, with_confidence=False, imWidth=0, imHeight=0, sort_by_confidences=True):
    """
    Returns all points, confindences and transcriptions of a file in lists. Valid line formats:
    xmin,ymin,xmax,ymax,[confidence],[transcription]
    x1,y1,x2,y2,x3,y3,x4,y4,[confidence],[transcription]
    """
    points_list = []
    transcriptions_list = []
    confidences_list = []

    lines = content.split("\r\n" if CRLF else "\n")
    for line in lines:
        line = line.replace("\r", "").replace("\n", "")
        if(line != ""):
            points, confidence, transcription = get_tl_line_values(
                line, LTRB, with_transcription, with_confidence, imWidth, imHeight)
            points_list.append(points)
            transcriptions_list.append(transcription)
            confidences_list.append(confidence)

    if with_confidence and len(confidences_list) > 0 and sort_by_confidences:
        import numpy as np
        sorted_ind = np.argsort(-np.array(confidences_list))
        confidences_list = [confidences_list[i] for i in sorted_ind]
        points_list = [points_list[i] for i in sorted_ind]
        transcriptions_list = [transcriptions_list[i] for i in sorted_ind]

    return points_list, confidences_list, transcriptions_list


def main_evaluation(p, det_file, gt_file, default_evaluation_params_fn, validate_data_fn, evaluate_method_fn, show_result=True, per_sample=True):
    """
    This process validates a method, evaluates it and if it succed generates a ZIP file with a JSON entry for each sample.
    Params:
    p: Dictionary of parmeters with the GT/submission locations. If None is passed, the parameters send by the system are used.
    default_evaluation_params_fn: points to a function that returns a dictionary with the default parameters used for the evaluation
    validate_data_fn: points to a method that validates the corrct format of the submission
    evaluate_method_fn: points to a function that evaluated the submission and return a Dictionary with the results
    """

    # if (p == None):
    #     p = dict([s[1:].split('=') for s in sys.argv[1:]])
    #     if(len(sys.argv)<3):
    #         print_help()
    p = {}
    p['g'] = gt_file  # 'tttgt.zip'
    p['s'] = det_file  # 'det.zip'

    eval_params = default_evaluation_params_fn()
    if 'p' in p.keys():
        eval_params.update(p['p'] if isinstance(p['p'], dict)
                          else json.loads(p['p'][1:-1]))

    res_dict = {'calculated': True, 'Message': '',
               'method': '{}', 'per_sample': '{}'}
    # try:
    validate_data_fn(p['g'], p['s'], eval_params)
    eval_data = evaluate_method_fn(p['g'], p['s'], eval_params)
    res_dict.update(eval_data)

    # except Exception as e:
    # res_dict['Message']= str(e)
    # res_dict['calculated']=False

    if 'o' in p:
        if not os.path.exists(p['o']):
            os.makedirs(p['o'])

        results_output_name = p['o'] + '/results.zip'
        outZip = zipfile.ZipFile(results_output_name, mode='w', allowZip64=True)

        del res_dict['per_sample']
        if 'output_items' in res_dict.keys():
            del res_dict['output_items']

        outZip.writestr('method.json', json.dumps(res_dict))

    if not res_dict['calculated']:
        if show_result:
            sys.stderr.write('Error!\n' + res_dict['Message']+'\n\n')
        if 'o' in p:
            outZip.close()
        return res_dict

    if 'o' in p:
        if per_sample == True:
            for k, v in eval_data['per_sample'].items():
                outZip.writestr(k + '.json', json.dumps(v))

            if 'output_items' in eval_data.keys():
                for k, v in eval_data['output_items'].items():
                    outZip.writestr(k, v)

        outZip.close()

    if show_result:
        sys.stdout.write("Calculated!")
        sys.stdout.write('\n')
        sys.stdout.write(json.dumps(res_dict['e2e_method']))
        sys.stdout.write('\n')
        sys.stdout.write(json.dumps(res_dict['det_only_method']))
        sys.stdout.write('\n')

    return res_dict


def main_validation(default_evaluation_params_fn, validate_data_fn):
    """
    This process validates a method
    Params:
    default_evaluation_params_fn: points to a function that returns a dictionary with the default parameters used for the evaluation
    validate_data_fn: points to a method that validates the corrct format of the submission
    """
    try:
        p = dict([s[1:].split('=') for s in sys.argv[1:]])
        eval_params = default_evaluation_params_fn()
        if 'p' in p.keys():
            eval_params.update(p['p'] if isinstance(
                p['p'], dict) else json.loads(p['p'][1:-1]))

        validate_data_fn(p['g'], p['s'], eval_params)
        print('SUCCESS')
        sys.exit(0)
    except Exception as e:
        print(str(e))
        sys.exit(101)
