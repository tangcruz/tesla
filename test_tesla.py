import unittest
from unittest.mock import patch, MagicMock
from telegram import Update, CallbackQuery
from telegram.ext import CallbackContext
from handlers import button, handle_input
from update_status_handlers import handle_update_status, update_status, handle_update_selection
from parameterized import parameterized
import random
import itertools

def generate_button_combinations(n=1000):
    buttons = ['query_status', 'query_all', 'query_all_locations', 'query_by_car_number', 
               'query_by_status', 'query_by_unit', 'update_status', 
               'update_status_selection', 'update_location_selection']
    
    # Generate all possible pairs of buttons
    all_pairs = list(itertools.product(buttons, repeat=2))
    
    # If we have less than n pairs, repeat the list
    while len(all_pairs) < n:
        all_pairs.extend(all_pairs)
    
    # Shuffle and slice to get exactly n combinations
    random.shuffle(all_pairs)
    return all_pairs[:n]

class TestTelegramBot(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock(spec=Update)
        self.context = MagicMock(spec=CallbackContext)
        self.context.user_data = {}

    @parameterized.expand(generate_button_combinations(1000))
    @patch('handlers.query_all')
    @patch('handlers.query_all_locations')
    @patch('handlers.query_by_status')
    @patch('handlers.query_by_car_number')
    @patch('handlers.query_by_unit')
    @patch('update_status_handlers.handle_update_status')
    @patch('update_status_handlers.handle_update_selection')
    async def test_button_combinations(self, button1, button2, mock_query_all, mock_query_all_locations,
                                       mock_query_by_status, mock_query_by_car_number, mock_query_by_unit,
                                       mock_handle_update_status, mock_handle_update_selection):
        # First button press
        query1 = MagicMock(spec=CallbackQuery)
        query1.data = button1
        self.update.callback_query = query1
        
        await button(self.update, self.context)
        
        # Check the result of the first button press
        self.assert_button_result(button1, mock_query_all, mock_query_all_locations,
                                  mock_query_by_status, mock_query_by_car_number, mock_query_by_unit,
                                  mock_handle_update_status, mock_handle_update_selection)
        
        # Reset mocks
        for mock in [mock_query_all, mock_query_all_locations, mock_query_by_status, 
                     mock_query_by_car_number, mock_query_by_unit, mock_handle_update_status, 
                     mock_handle_update_selection]:
            mock.reset_mock()
        
        # Second button press
        query2 = MagicMock(spec=CallbackQuery)
        query2.data = button2
        self.update.callback_query = query2
        
        await button(self.update, self.context)
        
        # Check the result of the second button press
        self.assert_button_result(button2, mock_query_all, mock_query_all_locations,
                                  mock_query_by_status, mock_query_by_car_number, mock_query_by_unit,
                                  mock_handle_update_status, mock_handle_update_selection)

    def assert_button_result(self, button_data, mock_query_all, mock_query_all_locations,
                             mock_query_by_status, mock_query_by_car_number, mock_query_by_unit,
                             mock_handle_update_status, mock_handle_update_selection):
        if button_data == 'query_all':
            mock_query_all.assert_called_once()
        elif button_data == 'query_all_locations':
            mock_query_all_locations.assert_called_once()
        elif button_data == 'query_by_status':
            self.assertEqual(self.context.user_data['operation'], 'query_by_status')
        elif button_data == 'query_by_car_number':
            self.assertEqual(self.context.user_data['operation'], 'query_by_car_number')
        elif button_data == 'query_by_unit':
            self.assertEqual(self.context.user_data['operation'], 'query_by_unit')
        elif button_data == 'update_status':
            self.assertEqual(self.context.user_data['operation'], 'update_status')
        elif button_data in ['update_status_selection', 'update_location_selection']:
            mock_handle_update_selection.assert_called_once()

    @parameterized.expand([
        ('query_status', 'ABC123'),
        ('update_status', 'XYZ789'),
        ('query_by_status', '維修中'),
        ('query_by_unit', '單位A'),
        ('query_by_car_number', 'DEF456')
    ])
    @patch('handlers.handle_car_number')
    @patch('update_status_handlers.handle_update_status')
    @patch('handlers.query_by_status')
    @patch('handlers.query_by_unit')
    @patch('handlers.query_by_car_number')
    async def test_handle_input(self, operation, input_text, mock_handle_car_number, 
                                mock_handle_update_status, mock_query_by_status, 
                                mock_query_by_unit, mock_query_by_car_number):
        self.context.user_data['operation'] = operation
        self.update.message.text = input_text
        
        await handle_input(self.update, self.context)
        
        if operation == 'query_status':
            mock_handle_car_number.assert_called_once()
        elif operation == 'update_status':
            mock_handle_update_status.assert_called_once()
        elif operation == 'query_by_status':
            mock_query_by_status.assert_called_once()
        elif operation == 'query_by_unit':
            mock_query_by_unit.assert_called_once()
        elif operation == 'query_by_car_number':
            mock_query_by_car_number.assert_called_once()

if __name__ == '__main__':
    unittest.main()