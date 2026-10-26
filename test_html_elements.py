
import os
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


class TestH5Tag(unittest.TestCase):
    def setUp(self):
        # Configure Firefox to run without opening a visible browser window.
        firefox_options = Options()
        firefox_options.add_argument("--headless")

        self.driver = webdriver.Firefox(options=firefox_options)

    def test_h5_tag_content(self):
        driver = self.driver

        # Use the Jenkins TARGET_URL environment variable, if provided.
        target_url = os.environ.get(
            "TARGET_URL",
            "http://10.48.229.171"
        )
        driver.get(target_url)

        # Find the h5 element and check its text.
        h5_text = driver.find_element(By.TAG_NAME, "h5").text

        self.assertEqual(
            "Lab 3-7 Works!",
            h5_text,
            "The h5 tag does not contain the expected text."
        )

    def tearDown(self):
        if hasattr(self, "driver"):
            self.driver.quit()


if __name__ == "__main__":
    unittest.main()
