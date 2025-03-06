import unittest
from unittest.mock import patch, MagicMock
import requests
from crawler import get_random_proxy, validate_proxy, fetch_github_search_results


class TestGetRandomProxy(unittest.TestCase):

    @patch("crawler.validate_proxy", return_value=True)
    def test_with_working_proxy(self, mock_validate_proxy):
        proxies = ["proxy1", "proxy2", "proxy3"]
        result = get_random_proxy(proxies)
        self.assertIn("http", result)
        self.assertIn(result["http"], [f"http://{proxy}" for proxy in proxies])

    @patch("crawler.validate_proxy", return_value=False)
    def test_with_no_working_proxy(self, mock_validate_proxy):
        proxies = ["proxy1", "proxy2", "proxy3"]
        result = get_random_proxy(proxies)
        self.assertEqual(result, {})


class TestTestProxy(unittest.TestCase):

    @patch("requests.get")
    def test_validate_proxy_working(self, mock_get):
        mock_get.return_value.status_code = 200
        self.assertTrue(validate_proxy("proxy1"))

    @patch("requests.get", side_effect=requests.RequestException)
    def test_validate_proxy_not_working(self, mock_get):
        self.assertFalse(validate_proxy("proxy1"))

    @patch("requests.get")
    def test_validate_proxy_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout
        self.assertFalse(validate_proxy("proxy1"))


class TestFetchGithubSearchResults(unittest.TestCase):

    @patch("crawler.get_random_proxy", return_value={})
    @patch("requests.get")
    def test_fetch_github_search_results_success(self, mock_get, mock_get_random_proxy):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <div class="Box-sc-g0xbh4-0 gPrlij">
            <div class="Box-sc-g0xbh4-0 MHoGG search-title">
                <a class="prc-Link-Link-85e08" href="/owner/repo">repo</a>
            </div>
            <ul class="bZkODq">
                <span>Python</span>
            </ul>
        </div>
        """
        mock_get.return_value = mock_response

        keywords = ["python"]
        proxies = ["proxy1", "proxy2"]
        search_type = "repositories"
        results = fetch_github_search_results(keywords, proxies, search_type)

        expected_results = [
            {
                "url": "https://github.com/owner/repo",
                "extra": {"owner": "owner", "language_details": {"Python": True}},
            }
        ]
        self.assertEqual(results, expected_results)

    @patch("crawler.get_random_proxy", return_value={})
    @patch("requests.get", side_effect=requests.RequestException)
    def test_fetch_github_search_results_request_exception(
        self, mock_get, mock_get_random_proxy
    ):
        keywords = ["python"]
        proxies = ["proxy1", "proxy2"]
        search_type = "repositories"
        results = fetch_github_search_results(keywords, proxies, search_type)
        self.assertEqual(results, [])

    @patch("crawler.get_random_proxy", return_value={})
    @patch("requests.get")
    def test_fetch_github_search_results_no_results(
        self, mock_get, mock_get_random_proxy
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<div></div>"
        mock_get.return_value = mock_response

        keywords = ["python"]
        proxies = ["proxy1", "proxy2"]
        search_type = "repositories"
        results = fetch_github_search_results(keywords, proxies, search_type)
        self.assertEqual(results, [])

    @patch("crawler.get_random_proxy", return_value={})
    @patch("requests.get")
    def test_fetch_github_search_results_no_language(
        self, mock_get, mock_get_random_proxy
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <div class="Box-sc-g0xbh4-0 gPrlij">
            <div class="Box-sc-g0xbh4-0 MHoGG search-title">
                <a class="prc-Link-Link-85e08" href="/owner/repo">repo</a>
            </div>
        </div>
        """
        mock_get.return_value = mock_response

        keywords = ["python"]
        proxies = ["proxy1", "proxy2"]
        search_type = "repositories"
        results = fetch_github_search_results(keywords, proxies, search_type)

        expected_results = [
            {"url": "https://github.com/owner/repo", "extra": {"owner": "owner"}}
        ]
        self.assertEqual(results, expected_results)


if __name__ == "__main__":
    unittest.main()
