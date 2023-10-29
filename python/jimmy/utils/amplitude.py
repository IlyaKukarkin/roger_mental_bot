def user_to_string(user):
    return {
        **user,
        '_id': str(user['_id']),
        'form_id': str(user['form_id']),
        'created_at': str(user['created_at']),
    }


def message_to_string(message):
    return {
        **message,
        '_id': str(message['_id']),
        'id_user': str(message['id_user']),
        'created_date': str(message['created_date']),
        "sent": list(map(str, message['sent'])),
        "users": list(map(str, message['users']))
    }


def user_message_to_string(user_message):
    return {
        **user_message,
        '_id': str(user_message['_id']),
        'id_user': str(user_message['id_user']),
        'id_message': str(user_message['id_message']),
        'time_to_send': str(user_message['time_to_send']),
    }
