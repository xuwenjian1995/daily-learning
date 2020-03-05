# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2019-04-30-15:51
processor_conf_list = [
    {
        "name": "detect_table_areas_od",
        "module": "slave.detect_table_areas_od",
        "args": {
            'enable': False,
        }
    },
    {
        "name": "find_custom_lines",
        "module": "slave.find_custom_lines",
        "args": {
            'enable': False,
        }
    },
    {
        "name": "detect_table_areas_ip",
        "module": "slave.detect_table_areas_ip",
        "args": {
            'enable': True,
            'algorithm_params': {
                'filter_invalid_areas': True,
                'tuner_border': True
            }
        }
    },
    {
        "name": "filter_lines",
        "module": "slave.filter_lines",
        "args": {
            'y_position_epsilon': 0.6,
            'x_position_epsilon': 0.6,
        }
    },
    {
        "name": "extract_table_cells",
        "module": "slave.extract_table_cells",
        "args": {
            'algorithm_params': {
                'y_position_epsilon': 0.8,
                'x_position_epsilon': 0.9,
                'border_filter_theta': 1.0,
                'merge_cell_overlap_threshold': 0.5,
                'outlier_line_threshold': 0.6,
            }
        }
    },
    {
        "name": "find_od_lines",
        "module": "slave.find_od_lines",
        "args": {
            'algorithm_params': {
                'pse_ip': '47.102.252.183',
                'pse_port': '51002',
            }
        }
    },
]
