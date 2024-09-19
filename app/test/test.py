from datetime import datetime

from pydantic import BaseModel, Field

from app.database.mysql.xxlxdb.service_confirm.service_confirm_school import select_service_school, \
    select_service_history

service_school_dict_list = select_service_school("XT1020156")
service_school_id_list = [service_school_dict.get("id") for service_school_dict in
                          service_school_dict_list]
service_history_dict_list = select_service_history(service_school_id_list)
# Create a dictionary with school id as the key
school_dict = {school['id']: school for school in service_school_dict_list}
# Initialize the service_history field for each school
for school in school_dict.values():
    school['service_history'] = []
# Append each history item to the corresponding school dictionary
for history in service_history_dict_list:
    confirm_schl_id = history['confirm_schl_id']
    if confirm_schl_id in school_dict:
        school_dict[confirm_schl_id]['service_history'].append(history)
# Convert the dictionary back to a list
application_progress_data_list = list(school_dict.values())

