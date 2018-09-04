# -*- coding: utf-8 -*-
import time

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.test import TestCase, TransactionTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.support.wait import WebDriverWait

from flightTable import views
from flightTable.models import Crew, Flight, Airport, Plane, Airline
import datetime
from django.core import serializers
import json

# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions


class SeleniumTestMine(StaticLiveServerTestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.driver = webdriver.Chrome(
            executable_path="/home/miron/PycharmProjects/WWW2_2/flightTable/webDrivers/chromedriver")
        self.driver.implicitly_wait(5)
        self.base_url = "https://www.katalon.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        # self.driver.get(self.live_server_url)
        self.user = User.objects.create_user(username='user',
                                             email='jlennon@beatles.com',
                                             password='password123')

    def test_buy_ticket(self):
        driver = self.driver
        driver.get(self.live_server_url)

        driver.find_element_by_name("username").send_keys("user")
        driver.find_element_by_name("password").send_keys("password123")
        driver.find_element_by_name("password").send_keys(Keys.ENTER)
        driver.find_element_by_link_text("Go back").click()
        driver.find_element_by_link_text("Add passengers").click()
        driver.find_element_by_id("id_name").send_keys("Name")
        driver.find_element_by_id("id_surname").send_keys("Surname")
        driver.find_element_by_id("id_surname").send_keys(Keys.ENTER)

        try:
            self.assertEqual("1", driver.find_element_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='Surname'])[2]/following::th[1]").text)
        except AssertionError as e:
            self.verificationErrors.append(str(e))
        try:
            self.assertEqual("19 seats remaining.", driver.find_element_by_id("Seats Remaining").text)
        except AssertionError as e:
            self.verificationErrors.append(str(e))
        driver.find_element_by_id("id_name").send_keys("Name")
        driver.find_element_by_id("id_surname").send_keys("Surname")
        driver.find_element_by_id("id_surname").send_keys(Keys.ENTER)

        try:
            self.assertEqual("2", driver.find_element_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='Surname'])[2]/following::th[1]").text)
        except AssertionError as e:
            self.verificationErrors.append(str(e))
        try:
            self.assertEqual("18 seats remaining.", driver.find_element_by_id("Seats Remaining").text)
        except AssertionError as e:
            self.verificationErrors.append(str(e))

    def test_assign_crew(self):
        driver = self.driver
        driver.get(self.live_server_url)

        driver.find_element_by_name("username").send_keys("user")
        driver.find_element_by_name("password").send_keys("password123")
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Awesome Flights'])[1]/following::input[4]").click()
        driver.find_element_by_link_text("Go back").click()
        driver.find_element_by_link_text("Change crews assignments").click()
        driver.find_element_by_name("username").send_keys("user")
        driver.find_element_by_name("password").send_keys("password123")
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Logout'])[1]/preceding::input[1]").click()
        driver.find_element_by_name("date_field").send_keys("09042018")
        driver.find_element_by_id("date_button").click()
        # driver.find_element_by_xpath(
        #     "(.//*[normalize-space(text()) and normalize-space(.)='PG'])[1]/following::td[1]").click()
        driver.find_element_by_name("Firstname").send_keys("A1")
        driver.find_element_by_name("Surname").send_keys("B1")
        driver.find_element_by_name("FlightId").send_keys("1")
        driver.find_element_by_id("assign_button").click()
        try:
            WebDriverWait(driver, 5).until(
                expected_conditions.visibility_of(driver.find_element_by_id("change_success")))
            if "A1 B1" not in driver.find_element_by_xpath(
                    "(.//*[normalize-space(text()) and normalize-space(.)='crew'])[1]/following::td[1]").text:
                raise AssertionError("Crew assignment isn't displayed.")
        except AssertionError as e:
            self.verificationErrors.append(str(e))

        driver.find_element_by_name("Firstname").clear()
        driver.find_element_by_name("Firstname").send_keys("A1")
        driver.find_element_by_name("Surname").clear()
        driver.find_element_by_name("Surname").send_keys("B1")
        driver.find_element_by_name("FlightId").clear()
        driver.find_element_by_name("FlightId").send_keys("21")
        driver.find_element_by_id("assign_button").click()

        try:
            # time.sleep(5)
            WebDriverWait(driver, 5).until(
                expected_conditions.visibility_of(driver.find_element_by_id("change_error")))

            self.assertEqual("This crew has already flight at this time.",
                             driver.find_element_by_id("change_error").text)
        except AssertionError as e:
            self.verificationErrors.append(str(e))

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


class ApiTest(TestCase):

    def setUp(self):
        self.password = 'password123'
        self.user = User.objects.create_user(username='john',
                                             email='jlennon@beatles.com',
                                             password=self.password)
        self.user.save()
        self.crew = Crew(captain_name="A1", captain_surname="B1")
        self.crew.save()
        self.crew2 = Crew(captain_name="A2", captain_surname="B2")
        self.crew2.save()
        self.airport1 = Airport(name="Airport1")
        self.airport1.save()
        self.airport2 = Airport(name="Airport2")
        self.airport2.save()
        self.airline1 = Airline(name="Airline1")
        self.airline1.save()
        self.departure_time = datetime.datetime(year=2015, month=5, day=13, hour=12, minute=15)
        self.arrival_time = datetime.datetime(year=2015, month=5, day=13, hour=17, minute=15)
        self.plane = Plane(registration_num="1", airline=self.airline1)
        self.plane.save()
        self.flight = Flight(arrival_airport=self.airport1, departure_airport=self.airport2,
                             plane=self.plane,
                             crew=self.crew,
                             arrival_time=self.arrival_time, departure_time=self.departure_time)
        self.flight.save()

    def test_get_crews_on_day(self):
        response = self.client.get('/api/flights_and_crews/', data={
            'day': self.departure_time.day,
            'month': self.departure_time.month,
            'year': self.departure_time.year,
        })
        expected = []
        expected.append({'flightId': self.flight.id,
                         'crew': self.flight.crew.captain_name + " " + self.flight.crew.captain_surname,
                         "departure airport": self.flight.departure_airport.__str__(),
                         "arrival airport": self.flight.arrival_airport.__str__()})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, JsonResponse({'crews': expected}).content)

    def test_change_crew_success(self):
        json_data = {
            'captain_name': self.crew2.captain_name,
            'flight_id': self.flight.id,
            'captain_surname': self.crew2.captain_surname,
            'username': self.user.username,
            'password': self.password,
        }
        response = self.client.generic('POST', '/api/change_crew/', json.dumps(json_data))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.crew2, Flight.objects.first().crew)

    def test_change_crew_fail(self):
        flight = Flight(arrival_airport=self.airport1, departure_airport=self.airport2,
                        plane=self.plane,
                        crew=self.crew2,
                        arrival_time=self.arrival_time + datetime.timedelta(hours=1),
                        departure_time=self.departure_time + datetime.timedelta(hours=1))
        flight.save()

        json_data = {
            'captain_name': self.crew.captain_name,
            'flight_id': flight.id,
            'captain_surname': self.crew.captain_surname,
            'username': self.user.username,
            'password': self.password,
        }
        response = self.client.generic('POST', '/api/change_crew/', json.dumps(json_data))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.crew2, Flight.objects.filter(id=flight.id).first().crew)  # unchanged
