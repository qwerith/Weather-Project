import unittest
from accounts import *

class Accounts_Test(unittest.TestCase):

    def test_register(self):
        account = Accounts("email", "12345")
        account_true = Accounts("yuriisorokin98@gmail.com", "12345")
        account_test = Accounts("Test@gmail.com", "12345")
        self.assertEqual(account.register(1), ['Registration failed'])
        self.assertEqual(account_true.register("Yurii"), ["Account already exists"])
        #Needs db with out this account "Test@gmail.com", "12345"
        #self.assertEqual(account_test.register("Dev"), ["Your account has been successfully created"])
    
    def test_user_verification(self):
        account_test = Accounts("Test@gmail.com", "12345")
        account_invalid = Accounts("Test1@gmail.com", "123456")
        account_invalid1 = Accounts("Test@gmail.com", "123456")
        #Needs db with this account "Test@gmail.com", "12345"
        self.assertEqual(type(account_test.user_verification()), tuple)
        self.assertEqual(account_invalid.user_verification(), None)
        self.assertEqual(account_invalid1.user_verification(), None)
    
    def test_generate_temporary_password(self):
        self.assertEqual(type(generate_temporary_password("Test@gmail.com")), tuple)
        self.assertEqual(generate_temporary_password("Test1@gmail.com"), (None,""))
    
    def test_input_validation(self):
        self.assertEqual(input_validation(["adssda@gmail.","12345"]), ["Invalid email"])
        self.assertEqual(input_validation(["adssda@gmail.","1234"]), ["Invalid email", "Password must be 5 to 10 characters long"])
        self.assertEqual(input_validation(["adssda@gmail.","1234","12345","123456"]), ["Invalid email", "Password must be 5 to 10 characters long", "Passwords do not match"])
        self.assertEqual(input_validation(["adssda@gmail.gmail.com","1234","12345","123456"]), ["Password must be 5 to 10 characters long", "Passwords do not match"])
        self.assertEqual(input_validation(["adssda@gmail.gmail.com","12345","12345","123456"]), ["Passwords do not match"])
        self.assertEqual(input_validation(["adssda@gmail.gmail.com","1234","12345","12345"]), ["Password must be 5 to 10 characters long"])
        self.assertEqual(input_validation(["adssda@gmail.gmail.com","12345","12345","12345"]), [])
        self.assertEqual(input_validation(["adssda@gmail.gmail.com", 1 , 2]), ["Invalid data type"])
    
    def test_raises_input_validation(self):
        self.assertRaises(IndexError, input_validation, ["adssda@gmail.com"])


if __name__=='__main__':
    unittest.main()