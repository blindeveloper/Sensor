from app.utils import convert_tuples_to_strings
from app.queries import get_names_of_parameters, add_new_event, add_new_parameter, get_parameter_id, add_parameter_values_to_event_data, get_is_unique_event
from fastapi import HTTPException


def process_new_event(raw_climate_record, cur, con):
    raw_climate_record = dict(raw_climate_record)
    # check if no event with same ts exist in db
    is_unique = get_is_unique_event(cur, raw_climate_record['ts'])
    if is_unique:
        # add new event to Event table
        event_id = add_new_event(cur, con, raw_climate_record)
        # load supporting parameters
        names_of_parameters = get_names_of_parameters(cur)
        supporting_parameters = convert_tuples_to_strings(names_of_parameters)
        # add new parameters if needed to Parameter table
        for row in raw_climate_record['rows']:
            if row[0] == 'Variable':
                continue
            if row[0] not in supporting_parameters:
                add_new_parameter(cur, con, row)
            # get parameter id
            parameter_id = get_parameter_id(cur, row)
            # add all parameters values to EventData table
            add_parameter_values_to_event_data(
                cur, con, row, parameter_id, event_id)
    else:
        return HTTPException(
            status_code=500, detail='Event is already in database')
