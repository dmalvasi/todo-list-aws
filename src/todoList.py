import os
import boto3
import time
import uuid
import json
import functools
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_table(dynamodb=None):
    if not dynamodb:
        URL = os.environ['ENDPOINT_OVERRIDE']
        if URL:  # pragma: no cover
            print('URL dynamoDB:'+URL)
            boto3.client = functools.partial(boto3.client, endpoint_url=URL)
            boto3.resource = functools.partial(boto3.resource,
                                               endpoint_url=URL)
        dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
    # fetch todo from the database
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    return table


def get_item(key, dynamodb=None):
    table = get_table(dynamodb)
    try:
        result = table.get_item(
            Key={
                'id': key
            }
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print('Result getItem:'+str(result))
        if 'Item' in result:
            return result['Item']


def get_items(dynamodb=None):
    table = get_table(dynamodb)
    # fetch todo from the database
    result = table.scan()
    return result['Items']


def put_item(text, dynamodb=None):
    table = get_table(dynamodb)
    timestamp = str(time.time())
    print('Table name:' + table.name)
    item = {
        'id': str(uuid.uuid1()),
        'text': text,
        'checked': False,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }
    try:
        # write the todo to the database
        table.put_item(Item=item)
        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(item)
        }

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


def update_item(key, text, checked, dynamodb=None):
    table = get_table(dynamodb)
    timestamp = int(time.time() * 1000)
    # update the todo in the database
    try:
        result = table.update_item(
            Key={
                'id': key
            },
            ExpressionAttributeNames={
              '#todo_text': 'text',
            },
            ExpressionAttributeValues={
              ':text': text,
              ':checked': checked,
              ':updatedAt': timestamp,
            },
            UpdateExpression='SET #todo_text = :text, '
                             'checked = :checked, '
                             'updatedAt = :updatedAt',
            ReturnValues='ALL_NEW',
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return result['Attributes']


def delete_item(key, dynamodb=None):
    table = get_table(dynamodb)
    # delete the todo from the database
    try:
        table.delete_item(
            Key={
                'id': key
            }
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return


def create_todo_table(dynamodb):
    # For unit testing
    tableName = os.environ['DYNAMODB_TABLE']
    print('Creating Table with name:' + tableName)
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=tableName)
    if (table.table_status != 'ACTIVE'):
        raise AssertionError()  # pragma: no cover

    return table


# ------------------ TRASLATE INICIO --------------------
# Obtiene el servicio de comprehend
def get_comprehend(comprehend=None):  # pragma: no cover
    if not comprehend:
        url_comprehend = 'https://comprehend.us-east-1.amazonaws.com/'
        comprehend = boto3.client(service_name='comprehend',
                                  endpoint_url=url_comprehend)
    logger.debug("Obteniendo comprehend")
    logger.debug(comprehend)
    return comprehend


# Obtiene el servicio de traslate
def get_translate(translate=None):  # pragma: no cover
    if not translate:
        url_translate = 'https://translate.us-east-1.amazonaws.com/'
        translate = boto3.client(service_name='translate',
                                 endpoint_url=url_translate)
    logger.debug("Obteniendo translate")
    logger.debug(translate)
    return translate


# Detecta el lenguaje original del texto.
def get_item_languaje(text, comprehend=None):  # pragma: no cover
    comprehend = get_comprehend(comprehend)
    logger.info(comprehend)
    try:
        logger.info("Detect text lang: " + str(text))
        response = comprehend.detect_dominant_language(
                Text=text
        )
    except ClientError as e:
        logger.exception("Couldn't detect languages.")
        print(e.response['Error']['Message'])
    else:
        languages = response['Languages']
        logger.info("Detected %s languages.", len(languages))

        # Ordeno la lista de lenguajes por el mejor score
        order_languaje = sorted(
                response['Languages'],
                key=lambda k: k['Score'],
                reverse=True)
        # Obtengo el primero de la lista ordenada
        thelangcode = order_languaje[0]['LanguageCode']
        return str(thelangcode)


# Realiza el traslate del texto.
def translate_text(text, s_lang, t_lang, translate=None):  # pragma: no cover
    logging.info('get translateclient --------------------')
    translate = get_translate(translate)
    logging.debug('TRASLATE CLIENTE  --------------------')
    logger.debug(translate)

    try:
        logger.debug(translate)
        logger.debug("texto: " + text)
        logger.debug("Lenguaje entrada: " + str(s_lang))
        logger.debug("Lenguaje salida: " + str(t_lang))

        response = translate.translate_text(
                Text=text,
                SourceLanguageCode=s_lang,
                TargetLanguageCode=t_lang
        )
    except ClientError as e:
        logger.exception("No fue posible realizar la traduccion")
        print(e.response['Error']['Message'])
        print(e)

    else:
        logger.debug("traduccion.")
        logger.debug(response)
        return str(response['TranslatedText'])


# pre requisitos: ID y Lenguaje
def translate_item(key, language, dynamodb=None):  # pragma: no cover
    logging.info('inicio translate (translate_item) --------------------')
    try:
        logging.debug('Llamo funcion get_item --------------------')
        item = get_item(key, dynamodb)
        if item:
            logging.debug('Respuesta funcion get_item --------------------')
            thetext = item['text']
            logging.debug(item)
            logging.debug(thetext)
            logging.debug('source languaje --------------------')
            # Obtiene el longuaje del texto (Lenguaje Origen)
            source_language = get_item_languaje(thetext)
            logging.debug(source_language)
            translateresult = translate_text(
                    thetext,
                    source_language,
                    language
            )

            logging.debug("Translation output: " + str(translateresult))
            # Actualizo texto traducido
            item['text'] = translateresult
            logging.debug("Item Traslate:")
            logging.debug(item)

    except ClientError as e:
        logger.exception("Couldn't translate.")
        print(e.response['Error']['Message'])
    else:
        return item

# ------------------ TRASLATE FIN --------------------
