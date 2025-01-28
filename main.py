import configparser
import os.path

conversion_config_file = os.path.sep.join([os.path.dirname(os.path.realpath(__file__)), "conversion_config.ini"])

class AwsAzureLoginConfigConverter:
    def __init__(self, azure_config_file_path: str) -> None:
        self._data = self.__read_config(azure_config_file_path)
        self._script_config = self.__read_config(conversion_config_file)

    def __read_config(self, file_path: str) -> dict:
        config = configparser.ConfigParser()
        config.read(file_path)
        data = {}

        for section in config.sections():
            data[section] = {}
            print(f"Section: {section}")
            for key in config[section]:
                data[section][key] = config[section][key]
                print(f"{key} = {config[section][key]}")
        return data

    def __get_saml_config_name(self, name: str) -> str:
        return name.split(' ')[1] if name.startswith('profile') else name
    
    def __convert_hours_to_seconds(self, hours: int) -> int:
        return hours * 60 * 60

    def __produce_saml2aws_configuration(self) -> dict:
        product = {}
        for config_name, value in self._data.items():
            saml_config_name = self.__get_saml_config_name(config_name)
            product[saml_config_name] = {
                "name": saml_config_name,
                "app_id": value.get('azure_app_id_uri', None),
                "url": self._script_config['ID_PROVIDER']['url'],
                "username": value.get('azure_default_username', None),
                "provider": self._script_config['ID_PROVIDER']['provider'],
                "mfa": self._script_config['MFA']['auth_type'],
                "mfa_ip_address": None,
                "skip_verify": False,
                "timeout": 0,
                "aws_urn": 'urn:amazon:webservices',
                "aws_session_duration": self.__convert_hours_to_seconds( int(value.get('azure_default_duration_hours', self._script_config['Defaults']['session_duration'])) ),
                "aws_profile": saml_config_name,
                "resource_id": None,
                "subdomain": None,
                "role_arn": value.get('azure_default_role_arn', None),
                "region": value.get('region', self._script_config['Defaults']['aws_region']),
                "http_attempts_count": None,
                "http_retry_delay": None,
                "credentials_file": None,
                "saml_cache": self._script_config['Defaults']['saml_cache'],
                "saml_cache_file": None,
                "target_url": None,
                "disable_remember_device": False,
                "disable_sessions": False,
                "download_browser_driver": False,
                "headless": False,
                "prompter": None
            }

        return product

    def __write_saml2aws_configuration(self, output_file_path: str, data: dict) -> None:
        with open(output_file_path, 'w') as f:
            for key, value in data.items():
                f.write(f"[{key}]\n")
                for k, v in value.items():
                    f.write(f"{k}={'' if v is None else v}\n")
                f.write('\n')


    def convert_to_saml2aws_configuraation(self, output_file_path: str) -> None:
        self.__write_saml2aws_configuration(output_file_path, self.__produce_saml2aws_configuration())
     

def main():
    converter = AwsAzureLoginConfigConverter('./input/config')
    converter.convert_to_saml2aws_configuraation('./output/.saml2aws')

if __name__ == "__main__":
    main()