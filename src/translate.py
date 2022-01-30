import logging
import todoList
import json
import decimalencoder


def translate(event, context):
    logging.info('inicio traducciones --------------------')
    logging.debug(event)
    if ('id' not in event['pathParameters'] or
            'language' not in event['pathParameters']):
        logging.error("Validation Failed")
        raise Exception("Couldn't translate the todo item.")
        # Ver dde agregar error reposnse statuscode: 400

    # Obtiene el item de ToDo traducido
    item = todoList.translate_item(event['pathParameters']['id'],
                                   event['pathParameters']['language'])
    logging.debug('resultado de la salida:')
    logging.debug(item)
    # create a response
    if item:
        response = {
            "statusCode": 200,
            "body": json.dumps(item,
                               cls=decimalencoder.DecimalEncoder)
        }
    else:
        response = {
            "statusCode": 404,
            "body": ""
        }
    return response
