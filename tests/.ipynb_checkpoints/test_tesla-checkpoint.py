import unittest
from unittest.mock import patch, MagicMock
from telegram import Update, CallbackQuery
from telegram.ext import CallbackContext
from update_status_handlers import handle_update_status, update_status, handle_update_selection
from handlers import button, handle_input
from google_sheets import read_sheet, update_sheet
from parameterized import parameterized

class TestTelegramBot(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock(spec=Update)
        self.context = MagicMock(spec=CallbackContext)
        self.context.user_data = {}

    @patch('update_status_handlers.read_sheet')
    async def test_handle_update_status(self, mock_read_sheet):
        mock_read_sheet.return_value = [
            ['車號', '狀態', '單位', '位置'],
            ['ABC123', '空閒', '單位A', '位置X']
        ]
        self.update.message.text = 'ABC123'
        
        await handle_update_status(self.update, self.context)
        
        self.assertEqual(self.context.user_data['car_number'], 'ABC123')
        self.assertEqual(self.context.user_data['row_number'], 2)
        self.update.message.reply_text.assert_called_once()

    @patch('update_status_handlers.update_sheet')
    @patch('update_status_handlers.read_sheet')
    async def test_update_status(self, mock_read_sheet, mock_update_sheet):
        mock_read_sheet.return_value = [
            ['車號', '狀態', '單位', '位置'],
            ['ABC123', '空閒', '單位A', '位置X']
        ]
        self.context.user_data = {
            'car_number': 'ABC123',
            'row_number': 2,
            'action': 'update_status'
        }
        self.update.message.text = '維修中'
        
        await update_status(self.update, self.context)
        
        mock_update_sheet.assert_called_once_with(2, 'B', '維修中')
        self.update.message.reply_text.assert_called_once_with("車號 ABC123 的狀態已更新為 維修中。")

    async def test_handle_update_selection_status(self):
        query = MagicMock(spec=CallbackQuery)
        query.data = 'update_status_selection'
        self.update.callback_query = query
        
        await handle_update_selection(self.update, self.context)
        
        self.assertEqual(self.context.user_data['action'], 'update_status')
        query.message.reply_text.assert_called_once_with("請輸入新的狀態:")

    async def test_handle_update_selection_location(self):
        query = MagicMock(spec=CallbackQuery)
        query.data = 'update_location_selection'
        self.update.callback_query = query
        
        await handle_update_selection(self.update, self.context)
        
        self.assertEqual(self.context.user_data['action'], 'update_location')
        query.message.reply_text.assert_called_once_with("請輸入新的位置:")

    @patch('handlers.query_all')
    @patch('handlers.query_all_locations')
    async def test_button_query_all(self, mock_query_all_locations, mock_query_all):
        query = MagicMock(spec=CallbackQuery)
        query.data = 'query_all'
        self.update.callback_query = query
        
        await button(self.update, self.context)
        
        mock_query_all.assert_called_once_with(self.update, self.context)

    @patch('handlers.handle_car_number')
    async def test_handle_input_query_status(self, mock_handle_car_number):
        self.context.user_data['operation'] = 'query_status'
        self.update.message.text = 'ABC123'
        
        await handle_input(self.update, self.context)
        
        mock_handle_car_number.assert_called_once_with(self.update, self.context)

    @parameterized.expand([
        ('ABC123', '維修中', 'update_status', '狀態'),
        ('XYZ789', '新位置', 'update_location', '位置'),
    ])
    @patch('update_status_handlers.update_sheet')
    @patch('update_status_handlers.read_sheet')
    async def test_update_status_parameterized(self, car_number, new_value, action, column, mock_read_sheet, mock_update_sheet):
        mock_read_sheet.return_value = [
            ['車號', '狀態', '單位', '位置'],
            ['ABC123', '空閒', '單位A', '位置X'],
            ['XYZ789', '使用中', '單位B', '位置Y']
        ]
        self.context.user_data = {
            'car_number': car_number,
            'row_number': 2 if car_number == 'ABC123' else 3,
            'action': action
        }
        self.update.message.text = new_value
        
        await update_status(self.update, self.context)
        
        expected_column = 'B' if column == '狀態' else 'D'
        mock_update_sheet.assert_called_once_with(self.context.user_data['row_number'], expected_column, new_value)
        self.update.message.reply_text.assert_called_once_with(f"車號 {car_number} 的{column}已更新為 {new_value}。")

    @patch('handlers.query_by_status')
    async def test_handle_input_query_by_status(self, mock_query_by_status):
        self.context.user_data['operation'] = 'query_by_status'
        self.update.message.text = '維修中'
        
        await handle_input(self.update, self.context)
        
        self.assertEqual(self.context.user_data['status_query'], '維修中')
        mock_query_by_status.assert_called_once_with(self.update, self.context)

    @patch('update_status_handlers.read_sheet')
    async def test_handle_update_status_car_not_found(self, mock_read_sheet):
        mock_read_sheet.return_value = [
            ['車號', '狀態', '單位', '位置'],
            ['ABC123', '空閒', '單位A', '位置X']
        ]
        self.update.message.text = 'XYZ789'  # Non-existent car number
        
        await handle_update_status(self.update, self.context)
        
        self.update.message.reply_text.assert_called_once_with("沒有找到相關車輛，請重新輸入車號:")

if __name__ == '__main__':
    unittest.main()