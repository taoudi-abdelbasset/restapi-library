import argparse
import json
import sys
from pathlib import Path
from .core.config import ConfigParser
from .core.exceptions import ConfigurationError

def validate_config(config_path: str) -> None:
    """Validate configuration file"""
    try:
        parser = ConfigParser(config_path=config_path)
        print(f"✓ Configuration file '{config_path}' is valid")
        
        # Print API summary
        for api_name, api_config in parser.config.items():
            print(f"\nAPI: {api_name}")
            print(f"  Base URL: {api_config['base_url']}")
            print(f"  Default Version: {api_config.get('default_version', 'v1')}")
            print(f"  Auth Type: {api_config.get('auth', {}).get('type', 'none')}")
            
            if 'endpoints' in api_config:
                endpoint_count = sum(len(endpoints) for endpoints in api_config['endpoints'].values())
                print(f"  Endpoints: {endpoint_count}")
        
    except ConfigurationError as e:
        print(f"✗ Configuration validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)

def generate_template(output_path: str) -> None:
    """Generate configuration template"""
    template = {
        "example-api": {
            "base_url": "${API_BASE_URL:https://api.example.com}",
            "default_version": "v1",
            "timeout": 30,
            "auth": {
                "type": "bearer",
                "token": "${API_TOKEN}"
            },
            "cache": {
                "type": "memory",
                "ttl": 3600
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "log_requests": True,
                "log_responses": True,
                "log_sensitive_data": False
            },
            "endpoints": {
                "v1": {
                    "get_items": {
                        "path": "/items",
                        "method": "GET",
                        "auth_required": True,
                        "cache": {
                            "enabled": True,
                            "ttl": 300
                        },
                        "retry": {
                            "attempts": 3,
                            "delay": 1.0,
                            "backoff_factor": 2.0
                        }
                    },
                    "create_item": {
                        "path": "/items",
                        "method": "POST",
                        "auth_required": True,
                        "body_required": True,
                        "request_model": "ItemModel",
                        "response_model": "ItemModel"
                    }
                }
            }
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✓ Configuration template generated: {output_path}")

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="REST API Library CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate configuration file'
    )
    validate_parser.add_argument(
        'config_path',
        help='Path to configuration file'
    )
    
    # Generate template command
    template_parser = subparsers.add_parser(
        'template',
        help='Generate configuration template'
    )
    template_parser.add_argument(
        '-o', '--output',
        default='config_template.json',
        help='Output file path (default: config_template.json)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'validate':
        validate_config(args.config_path)
    elif args.command == 'template':
        generate_template(args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()