import unittest

from src.netdiag.tools import check_ports, dns_lookup, system_info


class TestNetworkToolkit(unittest.TestCase):
    def test_system_info_has_expected_keys(self):
        info = system_info()
        self.assertIn("hostname", info)
        self.assertIn("operating_system", info)
        self.assertIn("local_ipv4_addresses", info)
        self.assertIn("default_gateway", info)

    def test_dns_lookup_localhost(self):
        result = dns_lookup("localhost")
        self.assertTrue(result["success"])
        self.assertTrue(result["addresses"])

    def test_invalid_port_raises_error(self):
        with self.assertRaises(ValueError):
            check_ports("localhost", [70000])


if __name__ == "__main__":
    unittest.main()
