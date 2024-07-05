import unittest
from unittest.mock import patch, MagicMock
import os
from config import load_env_vars_from_config, get_api_keys

class TestConfig(unittest.TestCase):

    def setUp(self):
        # Clear environment variables before each test
        for key in list(os.environ.keys()):
            if key.startswith(('OPENAI_', 'ANTHROPIC_', 'GEMINI_', 'AZURE_', 'AWS_')):
                del os.environ[key]

    def test_load_env_vars_from_config(self):
        config_vars = {
            'TEST_VAR1': 'value1',
            'TEST_VAR2': 'value2',
            'resources': 'test_resource'
        }
        mock_args = MagicMock()
        load_env_vars_from_config(config_vars, mock_args)

        self.assertEqual(os.environ['TEST_VAR1'], 'value1')
        self.assertEqual(os.environ['TEST_VAR2'], 'value2')
        self.assertEqual(mock_args.resources, 'test_resource')

    def test_load_env_vars_from_config_without_args(self):
        config_vars = {
            'TEST_VAR1': 'value1',
            'TEST_VAR2': 'value2'
        }
        load_env_vars_from_config(config_vars)

        self.assertEqual(os.environ['TEST_VAR1'], 'value1')
        self.assertEqual(os.environ['TEST_VAR2'], 'value2')

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_openai_key'})
    def test_get_api_keys_openai(self):
        key = get_api_keys('openai/gpt-4')
        self.assertEqual(key, 'test_openai_key')

    def test_get_api_keys_missing_key_openai(self):
        with self.assertRaises(ValueError):
            get_api_keys('openai/gpt-4')

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_anthropic_key'})
    def test_get_api_keys_anthropic(self):
        key = get_api_keys('anthropic/claude-2')
        self.assertEqual(key, 'test_anthropic_key')

    def test_get_api_keys_missing_key_anthropic(self):
        with self.assertRaises(ValueError):
            get_api_keys('anthropic/claude-2')

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_gemini_key'})
    def test_get_api_keys_gemini(self):
        key = get_api_keys('gemini/gemini-pro')
        self.assertEqual(key, 'test_gemini_key')

    def test_get_api_keys_missing_key_gemini(self):
        with self.assertRaises(ValueError):
            get_api_keys('gemini/gemini-proclaude-2')

    @patch.dict(os.environ, {
        'AZURE_API_KEY': 'test_azure_key',
        'AZURE_API_BASE': 'test_azure_base',
        'AZURE_API_VERSION': 'test_azure_version'
    })
    def test_get_api_keys_azure(self):
        key, base, version = get_api_keys('azure/gpt-4')
        self.assertEqual(key, 'test_azure_key')
        self.assertEqual(base, 'test_azure_base')
        self.assertEqual(version, 'test_azure_version')

    @patch.dict(os.environ, {
        'AZURE_API_BASE': 'test_azure_base',
        'AZURE_API_VERSION': 'test_azure_version'
    })
    def test_get_api_keys_missing_key_azure(self):
        with self.assertRaises(ValueError):
            get_api_keys('azure/gpt-4')

    @patch.dict(os.environ, {
        'AZURE_API_KEY': 'test_azure_key',
        'AZURE_API_VERSION': 'test_azure_version'
    })
    def test_get_api_keys_missing_base_azure(self):
        with self.assertRaises(ValueError):
            get_api_keys('azure/gpt-4')

    @patch.dict(os.environ, {
        'AZURE_API_KEY': 'test_azure_key',
        'AZURE_API_BASE': 'test_azure_base',
    })
    def test_get_api_keys_missing_version_azure(self):
        with self.assertRaises(ValueError):
            get_api_keys('azure/gpt-4')

    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_aws_key',
        'AWS_SECRET_ACCESS_KEY': 'test_aws_secret',
        'AWS_REGION_NAME': 'test_aws_region'
    })
    def test_get_api_keys_bedrock(self):
        key, secret, region = get_api_keys('bedrock/anthropic.claude-v2')
        self.assertEqual(key, 'test_aws_key')
        self.assertEqual(secret, 'test_aws_secret')
        self.assertEqual(region, 'test_aws_region')

    @patch.dict(os.environ, {
        'AWS_SECRET_ACCESS_KEY': 'test_aws_secret',
        'AWS_REGION_NAME': 'test_aws_region'
    })
    def test_get_api_keys_missing_key_bedrock(self):
        with self.assertRaises(ValueError):
            get_api_keys('azure/gpt-4')

    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_aws_key',
        'AWS_REGION_NAME': 'test_aws_region'
    })
    def test_get_api_keys_missing_secret_bedrock(self):
        with self.assertRaises(ValueError):
            get_api_keys('azure/gpt-4')

    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_aws_key',
        'AWS_SECRET_ACCESS_KEY': 'test_aws_secret',
    })
    def test_get_api_keys_missing_region_bedrock(self):
        with self.assertRaises(ValueError):
            get_api_keys('azure/gpt-4')

    def test_get_api_keys_unsupported_model(self):
        with self.assertRaises(ValueError):
            get_api_keys('unsupported/model')

    @patch.dict(os.environ, {
        'AZURE_API_KEY': 'test_azure_key',
        'AZURE_API_BASE': 'test_azure_base'
    })
    def test_get_api_keys_azure_missing_version(self):
        with self.assertRaises(ValueError):
            get_api_keys('azure/gpt-4')

if __name__ == '__main__':
    unittest.main()