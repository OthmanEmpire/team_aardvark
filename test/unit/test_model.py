##
## Unittests for the model module in the client package
##


__docformat__ = 'reStructuredText'


from src.client.model import (
    Client, Table, Food, Menu, MenuSet, Reservation, Restaurant
)

import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import call
from datetime import datetime


class ClientTest(unittest.TestCase):
    """
    Unit test class for Customer.
    """

    def setUp(self):
        """
        Prepares some mock data for the JSON menu and food, a mock menu,
        and a mock food object. Also, creates a Client object.
        """
        self.foodInfo = ["seaweed",
                         "breakfast",
                         "My hopes and dreams...",
                         11]

        self.JSONFood = \
        {
            "name": self.foodInfo[0],
            "type": self.foodInfo[1],
            "description": self.foodInfo[2],
            "price": self.foodInfo[3],
        }

        self.JSONMenu = {"menu": [self.JSONFood, self.JSONFood]}

        self.client = Client()
        self.mockMenu = self.setUpMenu()
        self.mockFood = self.setUpFood()

    def setUpMenu(self):
        """
        Sets up a dummy menu to be used for testing.
        :return: A mock menu object.
        """
        woodInfo = ["wood", 123.00]
        breadInfo = ["bread", 111.00]
        cardboardInfo = ["cardboard", 321.00]

        foodInfo = [woodInfo, breadInfo, cardboardInfo]
        foodList = []

        for info in foodInfo:
            food = MagicMock()
            food.name = info[0]
            food.price = info[1]
            foodList.append(food)

        menu = MagicMock()
        menu.items = foodList
        return menu

    def setUpFood(self):
        """
        Sets up a dummy food object to be used for testing.
        :return: A mock food object.
        """
        mockFood = MagicMock()
        mockFood.name = self.JSONFood["name"]
        mockFood.type = self.JSONFood["type"]
        mockFood.description = self.JSONFood["description"]
        mockFood.price = self.JSONFood["price"]
        return mockFood

    @patch("src.client.model.Client.parseJSONMenu")
    @patch("src.client.model.Menu")
    @patch("requests.get")
    def testRequestMenu(self, mockRequestMethod, mockMenu, mockParse):
        """
        Tests whether the client can fetch the menu from a mock object
        representing the server.
        """
        response = MagicMock()
        response.text = self.JSONMenu

        mockRequestMethod.return_value = response
        mockParse.return_value = [self.mockFood, self.mockFood]

        menuArgs = [call([self.mockFood, self.mockFood])]
        menu = self.client.requestMenu()

        self.assertEqual(mockMenu.call_args_list, menuArgs)

    @patch("src.client.model.Food")
    @patch("src.client.model.Client.parseJSONFood")
    def testParseJSONMenu(self, mockParse, mockFoodClass):
        """
        Tests whether data about menu in JSON formatting can be parsed
        correctly (so that it can later be fed into the Menu constructor).
        """
        mockParse.return_value = self.foodInfo
        mockFoodClass.return_value = self.mockFood

        parseArgs = [call(self.JSONFood), call(self.JSONFood)]
        foodArgs = [call(self.foodInfo), call(self.foodInfo)]

        foodList = self.client.parseJSONMenu(self.JSONMenu)

        self.assertListEqual(mockParse.call_args_list, parseArgs)
        self.assertListEqual(mockFoodClass.call_args_list, foodArgs)
        self.assertListEqual(foodList, [self.mockFood, self.mockFood])

    def testParseJSONFood(self):
        """
        Tests whether data about menu in JSON formatting can be parsed
        correctly (so that it can later be fed into the Food constructor).
        """
        foodData = self.client.parseJSONFood(self.JSONFood)
        self.assertEqual(foodData, self.foodInfo)

    def testConvertFoodToJSON(self):
        """
        Tests whether a food object (mocked) can be parsed to JSON
        formatting correctly.
        """
        self.assertDictEqual(self.client.convertFoodToJSON(self.mockFood),
                             self.JSONFood)

    @patch("requests.post")
    def testSendMenu(self, requestPostMethod):
        """
        Tests whether the client can send the menu to a mock object
        representing the server.
        """

        mockResponse = MagicMock()
        mockResponse.text = self.JSONMenu
        requestPostMethod.return_value = mockResponse

        menu = self.setUpMenu()

        self.assertDictEqual(self.client.sendMenu(menu).text, self.JSONMenu)


class ReservationTest(unittest.TestCase):
    """
    Unit test class for Reservation.
    """

    def setUp(self):
        """
        Creates a Reservation object.
        """
        self.reservation = Reservation()

    def testReserve(self):
        """
        Tests whether the information generated from a booking or cancellation
        request is correct.
        """
        bookingInfo = \
            self.reservation.reserve(True, 3, datetime(2005, 7, 14, 12, 30))

        self.assertEqual(bookingInfo["table"], 3)
        self.assertEqual(bookingInfo["date"], (2005, 7, 14))
        self.assertEqual(bookingInfo["time"], (12, 30))
        self.assertEqual(bookingInfo["book"], True)

        bookingInfo = \
            self.reservation.reserve(False, 3, datetime(2005, 7, 14, 12, 30))

        self.assertEqual(bookingInfo["book"], False)


class RestaurantTest(unittest.TestCase):
    """
    Unit test class for Restaurant.
    """

    @patch("src.client.model.Table")
    def setUp(self, mockTable):
        """
        Creates a restaurant object with a mock menu prior to each test.
        :param mockTable: A mock object of a table.
        """
        menu = self.setUpMenu()
        mockTable.side_effect = self.createMockTable
        self.restaurant = Restaurant(menu, 50)

    def setUpMenu(self):
        """
        Sets up a dummy menu to be used for testing.
        :return: A mock menu object.
        """
        woodInfo = ["wood", 123.00]
        breadInfo = ["bread", 111.00]
        cardboardInfo = ["cardboard", 321.00]

        foodInfo = [woodInfo, breadInfo, cardboardInfo]
        foodList = []

        for info in foodInfo:
            food = MagicMock()
            food.name = info[0]
            food.price = info[1]
            foodList.append(food)

        menu = MagicMock()
        menu.items = foodList
        return menu

    def createMockTable(self, *args, **kwargs):
        """
        Creates and returns a new modified mock table object per call.
        :return: A prepared mock table.
        """
        mockTable = MagicMock()
        mockTable.isAvailable = False
        return mockTable

    def testFindEmptyTable(self):
        """
        Tests whether available table can be found.
        """
        tableList = []
        tableNum = [11, 22, 33]

        # Initialize Empty tables
        for i, num in enumerate(tableNum):
            tableList.append(self.restaurant.tables[num])
            tableList[i].isAvailable = True

        emptyTables = self.restaurant.findEmptyTable()

        for i, empty in enumerate(emptyTables):
            self.assertEqual(empty, tableList[i])


class TableTest(unittest.TestCase):
    """
    Unit test class for the Table class.
    """

    def setUp(self):
        """
        Initialises a table object prior to each test using mock objects.
        """
        menu = self.setUpMenu()
        self.table = Table(10, menu)

    def setUpMenu(self):
        """
        Sets up a dummy menu to be used for testing.
        :return: A mock menu object.
        """
        woodInfo = ["wood", 123.00]
        breadInfo = ["bread", 111.00]
        cardboardInfo = ["cardboard", 321.00]

        foodInfo = [woodInfo, breadInfo, cardboardInfo]
        foodList = []

        for info in foodInfo:
            food = MagicMock()
            food.name = info[0]
            food.price = info[1]
            foodList.append(food)

        menu = MagicMock()
        menu.items = foodList
        return menu

    def testOrder(self):
        """
        Tests whether the order method registers orders properly.
        """
        self.table.order("wood")
        self.table.order("wood")

        # Orders actually requested
        self.assertTrue(len(self.table.orderHistory), 2)
        self.assertTrue(self.table.orderHistory[0].name, "wood")

        # Orders not requested
        with self.assertRaises(NameError):
            self.table.order("metal")

    def testComputeBill(self):
        """
        Tests whether the bill matches the dollar.
        """
        self.table.order("wood")
        self.table.order("bread")
        self.table.order("cardboard")
        self.assertEqual(self.table.computeBill(), 555.00)

    def testPayBill(self):
        """
        Tests whether the payBill method properly accumulates payments.
        """
        self.table.payBill(10.00)
        self.table.payBill(10.00)
        self.table.payBill(20.00)
        self.table.payBill(30.00)
        self.table.payBill(50.00)
        self.assertEqual(self.table.totalPaid, 120.00)


class MenuTest(unittest.TestCase):
    """
    Unit test class for Menu class.
    """

    def setUp(self):
        """
        Prepares a menu to be tested against using mock objects.
        """
        self.bread = MagicMock()
        self.cardboard = MagicMock()

        self.bread.name = "bread"
        self.cardboard.name = "cardboard"
        foodItems = [self.cardboard, self.bread]

        self.menu = Menu(foodItems)

    def testFindItem(self):
        """
        Tests whether a specified food item can be found on the menu.
        """
        # Items on the menu

        self.assertEqual(self.menu.findItem("bread"), self.bread)
        self.assertEqual(self.menu.findItem("cardboard"), self.cardboard)

        # Items not on the menu
        with self.assertRaises(NameError):
            self.menu.findItem("salvation")


class MenuSetTest(unittest.TestCase):
    """
    Unit test class for the MenuSet class.
    """

    @patch("sys.stdout", None)
    def testAddingItem(self):
        """
        Tests whether the overridden add method behaves similar
        to the super class method (i.e. everything should be identical
        excluding a print statement upon adding a duplicate element).
        """
        itemA = "Item A"
        itemB = "Item B"

        menuSet = MenuSet()
        menuSet.add(itemA)
        menuSet.add(itemA)
        menuSet.add(itemB)

        self.assertEqual(len(menuSet), 2)
        self.assertTrue(itemA in menuSet)
        self.assertTrue(itemB in menuSet)


class FoodTest(unittest.TestCase):
    """
    Unit tests class for the Food class.
    """

    def testConstructor(self):
        """
        Tests whether constructing a valid food passes (and invalid fails).
        """
        # Valid food description
        validFood = ["Potato", "Main Course", "Very mushy...", 42.0]

        # Invalid food descriptions
        blankName = ["",  "Main Course", "Very mushy...", 42.0]
        blankDescription = ["Potato",  "Main Course", "", 42.0]
        invalidDishType = ["Potato", "MainCourse", "", 42.0]

        stringPrice = ["Potato",  "Main Course", "Very mushy...", "Kiwi"]
        negativePrice = ["Potato",  "Main Course", "Very mushy...", -42.0]
        blankPrice = ["Potato",  "Main Course", "Very mushy...", ""]
        emptyPrice = ["Potato",  "Main Course", "Very mushy...",]


        # Valid object
        potato = Food(validFood)
        self.assertEqual(potato.name, "potato")
        self.assertEqual(potato.type, "main course")
        self.assertEqual(potato.description, "very mushy...")
        self.assertEqual(potato.price, 42.0)

        # Invalid objects
        with self.assertRaises(ValueError):
            Food(blankName)
            Food(blankDescription)
            Food(invalidDishType)
            Food(negativePrice)
            Food(blankPrice)
            Food(emptyPrice)
        with self.assertRaises(TypeError):
            Food(stringPrice)


def testPrintStatements():
    """
    Runs all the print statements across all unit tested classes.
    This is factored out to avoid spam.
    """
    # Initialization
    cardboardInfo = ["cardboard", "dessert", "Fibericious", 42]
    breadInfo = ["bread", "main course", "I am BREAD.", 666]
    cardboard = Food(cardboardInfo)
    bread = Food(breadInfo)
    foodItems = [cardboard, bread]

    menu = Menu(foodItems)
    table = Table(7, menu)
    table.order("bread")
    table.order("bread")
    table.order("bread")

    # All print statements
#    menu.print()
#    table.printAllOrders()
#    table.printBill()


def main():
    """
    Code is executed through this method.
    """
    testPrintStatements()


if __name__ == "__main__":
#    main()
    unittest.main()