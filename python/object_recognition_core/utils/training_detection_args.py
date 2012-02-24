"""
Module that creates a function to define/read common arguments for the training/detection pipeline
"""

from object_recognition_core.db.interface import ObjectDbParameters
from object_recognition_core.db.object_db import ObjectDb, core_db_types
from object_recognition_core.db import models, dbtools
from object_recognition_core.utils.parser import ObjectRecognitionParser
import os
import sys
import yaml
try:
    import ecto_ros
    ECTO_ROS_FOUND = True
except ImportError:
    ECTO_ROS_FOUND = False

def common_interpret_object_ids(pipeline_param_full, args=None):
    """
    Given command line arguments and the parameters of the pipeline, clean the 'object_ids' field to be a list of
    object ids
    """
    pipeline_param = pipeline_param_full['parameters']

    # read the object_ids
    object_ids = None
    if args:
        objs = [args.__dict__, pipeline_param]
    else:
        objs = [pipeline_param]

    for obj in objs:
        ids = obj.get('object_ids', None)
        names = obj.get('object_names', None)

        if not ids and not names:
            continue

        for val in [ ids, names ]:
            if val is not 'all' and val is not 'missing' and isinstance(val, str):
                val = eval(val)

        if object_ids is None:
            object_ids = set()
        # initialize the DB
        db_params = pipeline_param_full['parameters']['db']
        type = db_params.get('type', None)
        if type.lower() not in core_db_types():
            continue
        db = dbtools.db_params_to_db(ObjectDbParameters(db_params))

        if 'all' in (ids, names):
            object_ids = set([ str(x.id) for x in models.Object.all(db) ]) #unicode without the str()
            break
        if 'missing' in (ids, names):
            tmp_object_ids = set([ str(x.id) for x in models.Object.all(db) ])
            tmp_object_ids_from_names = set([ str(x.object_id) for x in models.Model.all(db) ])
            object_ids.update(tmp_object_ids.difference(tmp_object_ids_from_names))
        if ids and ids != 'missing':
            object_ids.update(ids)
        if names and names != 'missing':
            for object_name in names:
                object_ids.update([str(x.id) for x in models.objects_by_name(db, object_name)])
        # if we got some ids through the command line, just stop here
        if object_ids:
            break
    if object_ids is not None:
        pipeline_param_full['parameters']['object_ids'] = list(object_ids)

def common_create_parser():
    def filter_node_name(node_name):
        return node_name
    parser = ObjectRecognitionParser()
    parser.add_argument('-c', '--config_file', help='Config file')
    parser.add_argument('--object_ids', help='If set, it overrides the list of object_ids in the config file. E.g.: \'["1ef112f21f12"]\'')
    parser.add_argument('--object_names', help='If set, it overrides the list of object names in the config file')
    parser.add_argument('--visualize', help='If set, it will display some windows with temporary results',
                       default=False, action='store_true')

    ros_group = parser.add_argument_group('ROS Parameters')
    ros_group.add_argument('--node_name', help='The name for the node. If "", it is not run in a ROS node',
                           default='object_recognition', type=filter_node_name)
    return parser

def ros_common_parse_args(parser):
    if ECTO_ROS_FOUND:
        original_argv = sys.argv
        clean_args = sys.argv
        ecto_ros.strip_ros_args(clean_args)
        args = parser.parse_args(args=clean_args[1:])

        if args.node_name and args.node_name != '""':
            ecto_ros.init(original_argv, args.node_name, False)
    else:
        args = parser.parse_args()

    return args

def common_parse_config_file(config_file_path, extra_pipeline_fields):
    # define the input
    if config_file_path is None or not os.path.exists(config_file_path):
        print >> sys.stderr, "The option file does not exist. --help for usage."
        sys.exit(-1)

    params = yaml.load(open(config_file_path))

    # read the different parameters from the config file, for each pipeline
    source_params = {}
    pipeline_params = {}
    sink_params = {}
    voter_params = {}
    for key , value in params.iteritems():
        if key.startswith('source'):
            source_params[key] = value
        elif key.startswith('pipeline'):
            # check the different fields
            for field in [ 'method', 'submethod', 'package', 'parameters'] + extra_pipeline_fields:
                if field not in value:
                    raise RuntimeError('The pipeline parameters need to have the subfield "%s", current parameters: %s' %
                                       (field, str(value)))
            pipeline_params[key] = value
        elif key.startswith('sink'):
            sink_params[key] = value
        elif key.startswith('voter'):
            voter_params[key] = value

    return source_params, pipeline_params, sink_params, voter_params

def read_arguments_training():
    parser = common_create_parser()
    parser.add_argument('--commit', dest='commit', action='store_true',
                        default=False, help='Commit the data to the database.')
    args = parser.parse_args()

    source_params, pipeline_params, sink_params, _voter_params = common_parse_config_file(args.config_file, [])
    # for each pipeline, get the right object ids
    for _pipeline_id, pipeline_param in pipeline_params.iteritems():
        # clean the object_ids
        common_interpret_object_ids(pipeline_param, args)

    args = vars(args)
    return source_params, pipeline_params, sink_params, args

def read_arguments_detector():
    parser = common_create_parser()
    args = ros_common_parse_args(parser)

    source_params, pipeline_params, sink_params, voter_params = common_parse_config_file(args.config_file, [ 'sources' ])

    # for each pipeline, make sure the corresponding source/sink exist
    for _pipeline_id, pipeline_param in pipeline_params.iteritems():
        for cell_type, params in [ ('source', source_params), ('sink', sink_params), ('voter', voter_params) ]:
            for cell_id in pipeline_param.get(cell_type + 's', []):
                if cell_id not in params and cell_id not in pipeline_params:
                    raise RuntimeError('The pipeline parameters has an invalid %s number' % cell_id)
        # clean the object_ids
        common_interpret_object_ids(pipeline_param, args)

    args = vars(args)
    return source_params, pipeline_params, sink_params, voter_params, args