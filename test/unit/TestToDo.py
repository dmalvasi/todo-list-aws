# from pprint import pprint
import warnings
import unittest
import boto3
from moto import mock_dynamodb2
import sys
import os
import json

@mock_dynamodb2
class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        print ('---------------------')
        print ('Start: setUp')
        warnings.filterwarnings(
            "ignore",
            category=ResourceWarning,
            message="unclosed.*<socket.socket.*>")
        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message="callable is None.*")
        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message="Using or importing.*")
        """Create the mock database and table"""
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        # Agrego servicio de omprehend y traslate
        url_comprehend = 'https://comprehend.us-east-1.amazonaws.com/'
        url_translate = 'https://translate.us-east-1.amazonaws.com/'
        self.comprehend =  boto3.client(service_name='comprehend', region_name='us-east-1', endpoint_url=url_comprehend)
        self.translate =  boto3.client(service_name='translate', region_name='us-east-1', endpoint_url=url_translate)
        self.is_local = 'true'
        self.uuid = "123e4567-e89b-12d3-a456-426614174000"
        self.text = "Aprender DevOps y Cloud en la UNIR"
        self.origin_lang = "es"
        self.dest_lang = "it"
        self.traduccion = "Scopri DevOps e Cloud presso UNIR"

        from src.todoList import create_todo_table
        self.table = create_todo_table(self.dynamodb)
        #self.table_local = create_todo_table()
        print ('End: setUp')

    def tearDown(self):
        print ('---------------------')
        print ('Start: tearDown')
        """Delete mock database and table after test is run"""
        self.table.delete()
        print ('Table deleted succesfully')
        #self.table_local.delete()
        self.dynamodb = None
        print ('End: tearDown')

    def test_table_exists(self):
        print ('---------------------')
        print ('Start: test_table_exists')
        #self.assertTrue(self.table)  # check if we got a result
        #self.assertTrue(self.table_local)  # check if we got a result

        print('Table name:' + self.table.name)
        tableName = os.environ['DYNAMODB_TABLE'];
        # check if the table name is 'ToDo'
        self.assertIn(tableName, self.table.name)
        #self.assertIn('todoTable', self.table_local.name)
        print ('End: test_table_exists')
        

    def test_put_todo(self):
        print ('---------------------')
        print ('Start: test_put_todo')
        # Testing file functions
        from src.todoList import put_item
        # Table local
        response = put_item(self.text, self.dynamodb)
        print ('Response put_item:' + str(response))
        self.assertEqual(200, response['statusCode'])
        # Table mock
        #self.assertEqual(200, put_item(self.text, self.dynamodb)[
        #                 'ResponseMetadata']['HTTPStatusCode'])
        print ('End: test_put_todo')

    def test_put_todo_error(self):
        print ('---------------------')
        print ('Start: test_put_todo_error')
        # Testing file functions
        from src.todoList import put_item
        # Table mock
        self.assertRaises(Exception, put_item("", self.dynamodb))
        self.assertRaises(Exception, put_item("", self.dynamodb))
        print ('End: test_put_todo_error')

    def test_get_todo(self):
        print ('---------------------')
        print ('Start: test_get_todo')
        from src.todoList import get_item
        from src.todoList import put_item

        # Testing file functions
        # Table mock
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response put_item:' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print ('Id item:' + idItem)
        self.assertEqual(200, responsePut['statusCode'])
        responseGet = get_item(
                idItem,
                self.dynamodb)
        print ('Response Get:' + str(responseGet))
        self.assertEqual(
            self.text,
            responseGet['text'])
        print ('End: test_get_todo')
    
    def test_list_todo(self):
        print ('---------------------')
        print ('Start: test_list_todo')
        from src.todoList import put_item
        from src.todoList import get_items

        # Testing file functions
        # Table mock
        put_item(self.text, self.dynamodb)
        result = get_items(self.dynamodb)
        print ('Response GetItems' + str(result))
        self.assertTrue(len(result) == 1)
        self.assertTrue(result[0]['text'] == self.text)
        print ('End: test_list_todo')


    def test_update_todo(self):
        print ('---------------------')
        print ('Start: test_update_todo')
        from src.todoList import put_item
        from src.todoList import update_item
        from src.todoList import get_item
        updated_text = "Aprender m??s cosas que DevOps y Cloud en la UNIR"
        # Testing file functions
        # Table mock
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response PutItem' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print ('Id item:' + idItem)
        result = update_item(idItem, updated_text,
                            "false",
                            self.dynamodb)
        print ('Result Update Item:' + str(result))
        self.assertEqual(result['text'], updated_text)
        print ('End: test_update_todo')


    def test_update_todo_error(self):
        print ('---------------------')
        print ('Start: atest_update_todo_error')
        from src.todoList import put_item
        from src.todoList import update_item
        updated_text = "Aprender m??s cosas que DevOps y Cloud en la UNIR"
        # Testing file functions
        # Table mock
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response PutItem' + str(responsePut))
        self.assertRaises(
            Exception,
            update_item(
                updated_text,
                "",
                "false",
                self.dynamodb))
        self.assertRaises(
            TypeError,
            update_item(
                "",
                self.uuid,
                "false",
                self.dynamodb))
        self.assertRaises(
            Exception,
            update_item(
                updated_text,
                self.uuid,
                "",
                self.dynamodb))
        print ('End: atest_update_todo_error')

    def test_delete_todo(self):
        print ('---------------------')
        print ('Start: test_delete_todo')
        from src.todoList import delete_item
        from src.todoList import put_item
        from src.todoList import get_items
        # Testing file functions
        # Table mock
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response PutItem' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print ('Id item:' + idItem)
        delete_item(idItem, self.dynamodb)
        print ('Item deleted succesfully')
        self.assertTrue(len(get_items(self.dynamodb)) == 0)
        print ('End: test_delete_todo')

    def test_delete_todo_error(self):
        print ('---------------------')
        print ('Start: test_delete_todo_error')
        from src.todoList import delete_item
        # Testing file functions
        self.assertRaises(TypeError, delete_item("", self.dynamodb))
        print ('End: test_delete_todo_error')

    def test_get_todo_error(self):
        #En este caso, busco un id no valido.
        print ('---------------------')
        print ('Start: test_get_todo_error')
        dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
        from src.todoList import get_item
        self.assertRaises(TypeError, get_item(None,dynamodb))
        print ('End: test_get_todo_error')

    def test_get_table_none(self):
        '''
            Caso agregado, es para ingresar en todoList.py en get_table cuando no se pasa
            la db. En este caso no utilizo el mock.
            Se agrega os.environ["ENDPOINT_OVERRIDE"] = '' para que no ingrese a la 
            coneccion via URL
        '''
        print ('---------------------')
        print ('Start: test_get_table_none')
        os.environ["ENDPOINT_OVERRIDE"] = ''
        from src.todoList import get_table
        table = get_table()
        print('Table name:' + str(table))
        self.assertIsNotNone(table)
        del os.environ['ENDPOINT_OVERRIDE']
        print ('End: test_get_table_none')

#  ------------------------------ PRUEBAS TRANSLATE INICIO ------------------------------
    # Testeo Obtener Lenguaje
    def test_get_languaje(self):
        print ('---------------------')
        print ('Start: test_get_languaje')
        from src.todoList import get_item_languaje
        responseLanguaje = get_item_languaje(
                self.text,
                self.comprehend)
        print ('Response Languaje:' + str(responseLanguaje))
        self.assertEqual(responseLanguaje, self.origin_lang)
        print ('End: test_get_languaje')

    # Testeo Obtener Lenguaje Error
    def test_get_language_err(self):
        print ('---------------------')
        print ('Start: test_err_get_languaje---------------')
        from src.todoList import get_item_languaje
        self.assertRaises(
            Exception,
            get_item_languaje("-", self.comprehend))
        print ('End: test_err_get_languaje---------------')

    # Testeo Traduccion Error
    def test_translate_text_err(self):
        print ('---------------------')
        print ('Start: test_err_translate_text')
        from src.todoList import translate_text
        
        self.assertRaises(Exception,
            translate_text(self.text,
                None,
                "es",
                self.translate))
        self.assertRaises(TypeError,
            translate_text(self.text,
                "it",
                "es",
                self.translate))
        self.assertRaises(Exception,
            translate_text(self.text,
                "it",
                "es", 
                self.translate))
        print ('End: test_err_translate_text')

    # Testeo Traduccion
    def test_translate_text(self):
        print ('---------------------')
        print ('Start: test_translate_text')
        from src.todoList import translate_text
        response = translate_text(
                self.text,
                self.origin_lang,
                self.dest_lang,
                self.translate)
        print ('Response Translate:' + str(response))
        self.assertEqual(response, self.traduccion)
        print ('End: test_translate_text')

    # Testeo funcion traduiccion item
    def test_translate_item(self):
        print ('---------------------')
        print ('Start: test_translate_item')
        from src.todoList import translate_item
        from src.todoList import put_item
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response PutItem' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        responseTranslate = translate_item(
                idItem,
                self.dest_lang,
                self.dynamodb)
        print ('Response translate:' + str(responseTranslate))
        self.assertEqual(
            self.traduccion,
            responseTranslate['text'])
        print ('End: test_translate_item')

#  ------------------------------ PRUEBAS TRANSLATE FIN ------------------------------

if __name__ == '__main__':
    unittest.main()